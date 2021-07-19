from telegram.utils.helpers import escape_markdown as es


def start_msg(name):
    msg = f"""*Hey {es(name,version=2)}* 🙂 *welcome to Jiosaavn downloader bot* ⚡⚡\n
    _Just send me a jiosaavn song or album link I will send you the audio_\n
Join channel @Royalbotz"""
    return msg


def help_msg():
    help = """ℹ️⁉⁉ *help*\n
*just send me a jiosaavn song,album or playlist link, I will send you the audio with lyrics*⚡⚡"""
    return help
