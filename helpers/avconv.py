#!/usr/bin/env python

"""Transcodes given file to opus or vorbis, if it has an aac-like extension
(mp3, aac, 3gp, mp4, m4a, m4b, mpg).

By default the bitrate of the source material is used, but may be
limited by the --bitrate parameter or the BITRATE environment variable,
both in kbit/s.

If a given bitrate differs from source bitrate, -f (force transcoding)
is implied."""

# Copyright 2015 Gregor Bollerhey
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

from __future__ import print_function
import argparse
import subprocess
import re, sys, time
import os, os.path, stat
import collections

MB_per_kbit = 0.000125

# vt100 terminal codes
CUR_UP = '\x1b[1A'
ERASE_LINE = '\x1b[2K'

# determine output path, handle existing path
if args.o:
    outpath = args.o
    if outpath == args.path:
        print('source path and target path have to be different')
        exit(1)
else:
    new_extension = '.opus' if not args.vorbis else '.ogg'
    has_extension = re.match(r'.*\..{3,4}', args.path)

    # infile has extension -> replace it.
    if has_extension and not args.path.endswith(new_extension):
        outpath = args.path.rsplit('.',1)[0] + new_extension
    else:
        # elsewhere just append
        outpath = args.path + new_extension

if os.path.exists(outpath) and not args.y:
    print('path exists: "%s", use -y to overwrite' % outpath)
    exit(1)

print('output path: ' + outpath)


# run avprobe to get some information
if not stat.S_ISFIFO(os.stat(args.path).st_mode):
    try:
        avprobe = subprocess.check_output(['avprobe', args.path],
                stderr=subprocess.STDOUT)
    except (subprocess.CalledProcessError, OSError) as e:
        print('avprobe failed: "%s"' % e)
        avprobe = ''
else:
    print('input from pipe, skipping avprobe')
    avprobe = ''


# determine bitrate limit from --bitrate > env(BITRATE) > avprobe
bitrate_src = re.search(r'bitrate: ([0-9]+) kb/s', avprobe)
if not bitrate_src is None:
    bitrate_src = int(bitrate_src.group(1))
else:
    print("source bitrate can't be determined, defaulting to 256 kbit/s")
    bitrate_src = 256

if not args.bitrate:
    try:
        bitrate = int(128)
    except KeyError:
        bitrate = bitrate_src
else:
    bitrate = args.bitrate

bitrate = min(bitrate, bitrate_src)


# assert aac-like extension (from wikipedia)
has_aac_ext = re.match(r'.*\.(mp3|aac|3gp|mp4|m4a|m4b|mpg)$', args.path)
force = args.f or bitrate != bitrate_src

if not (force or has_aac_ext):
    print('nothing to do (extension mismatch, force transcoding with -f)')
    exit(0)


acodec = 'libopus' if not args.vorbis else 'libvorbis'
print('converting using %s with bitrate %d kbit/s' % (acodec, bitrate))


# duration for percentual progress stats
duration = re.search(r'Duration: (\d+):(\d+):(\d+).(\d+)', avprobe)
if not duration is None:
    hh, mm, ss, frac_ss = map(int, duration.groups())
    duration = hh*3600.0 + mm*60.0 + ss + frac_ss/100.0
    print('duration %d seconds, expected raw size: %d MB' % (
            duration, duration*bitrate*MB_per_kbit))


# call avconv to transcode, calculate progress by watching output
if duration is None:
    avconv_stderr = None # use internal stat output
else:
    avconv_stderr = subprocess.PIPE # use progress filter


av_cmd = ['avconv', '-threads', 'auto', '-i', args.path, '-vn',
        '-acodec', acodec, '-b', str(bitrate)+'K', outpath]

if not args.vorbis:
    av_cmd.insert(-1, '-vbr')
    av_cmd.insert(-1, 'on')

if args.y:
    av_cmd.append('-y')

try:
    avconv = subprocess.Popen(av_cmd, stderr=avconv_stderr)
except OSError as e:
    print('avconv failed, not recoverable: "%s"' % e)
    exit(1)


class Speedometer:
    """incrementally calculates walltime-speed of changing y based on
    linear regression."""

    def __init__(self, N=100, epsilon=0.1, delta=0.1):
        self.epsilon, self.delta = epsilon, delta
        self.x = collections.deque(maxlen=N)
        self.y = collections.deque(maxlen=N)

    def add(self, yn):
        t = time.time()
        yn = float(yn)

        if ((len(self.x)>0 and abs(t-self.x[-1]) < self.delta) or
                (len(self.y)>0 and abs(yn-self.y[-1]) < self.epsilon)):
            return # discard if too close together

        self.x.append(t)
        self.y.append(yn)

    def speed(self):
        n = len(self.x)
        if n<2:
            raise ValueError('need at least two data points')

        xm = sum(self.x)/n
        ym = sum(self.y)/n
        nom = sum((self.x[i]-xm)*(self.y[i]-ym) for i in xrange(n))
        den = sum((self.x[i]-xm)**2 for i in xrange(n))
        return nom/den


if duration is None: # no output monitoring
    ret = avconv.wait()
else: # monitor output, calculate progress and ETA
    ret = None
    output_buffer = collections.deque(maxlen=256)
    print('  progress=?')
    speedometer = Speedometer()

    while(ret is None):
        ret = avconv.poll()
        output_buffer.extend( avconv.stderr.read(16) )

        # get latest "time", completeness is guaranteed by matching the
        # "bitrate"-b
        position = re.search(r'.*time=(\d+.\d+) b', ''.join(output_buffer))

        if position is not None:
            position = float(position.group(1))
            progress = position/duration
            speedometer.add(position)

            try:
                t_remaining = (duration-position)/speedometer.speed()
                t_remaining = '%d:%02d' % (t_remaining//60, t_remaining%60)

                print(CUR_UP, ERASE_LINE, 'progress=%.1f%% ETA=%s' %
                        (progress*100.0, t_remaining))
            except (ValueError, ZeroDivisionError):
                pass

    print(CUR_UP, ERASE_LINE, 'progress=100%')


# optionally delete source file
if args.d:
    os.remove(args.path)


exit(ret) # return avconv exit status
