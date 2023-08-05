import os
import sys
import argparse
import configparser
import subprocess

import pyperclip

import brocket

prefs_file = os.path.expanduser("~/.brocket.cfg")

parser = argparse.ArgumentParser(
    description='Make an Amazon link and Amazon Associates link.'
)

parser.add_argument(
    '--url',
    dest='amazon_url',
    default=None,
    help='An Amazon URL (default: whatever is on the clipboard).'
)

parser.add_argument(
    '--tracking-id',
    dest='tracking_id',
    default=None,
    help='The tracking-id to use (default: saved tracking-id in settings).'
)

parser.add_argument(
    '--show-tracking-id',
    dest='show_tracking_id',
    action='store_true',
    default=False,
    help='Print out the saved Amazon Associates tracking-id.'
)

parser.add_argument(
    '--set-tracking-id',
    dest='set_tracking_id',
    default=None,
    help='Set the tracking-id in the settings.'
)


def save_tracking_id(tracking_id):
    config = configparser.ConfigParser()
    config['brocket'] = {}
    config['brocket']['tracking_id'] = tracking_id
    with open(prefs_file, 'w') as configfile:
        config.write(configfile)


def load_tracking_id():
    config = configparser.ConfigParser()
    config.read(prefs_file)
    return config['brocket']['tracking_id']


def notify(title, subtitle, message, openUrl=None):

    cmd = ['terminal-notifier']

    if title:
        cmd.append('-title')
        cmd.append(title)

    if subtitle:
        cmd.append('-subtitle')
        cmd.append(subtitle)

    if message:
        cmd.append('-message')
        cmd.append(message)

    if openUrl:
        cmd.append('-open')
        cmd.append(str(openUrl))

    try:
        subprocess.call(cmd)
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            # Looks like terminal notifier is not available.
            pass
        else:
            raise


def main():
    args = parser.parse_args()

    # Setup the default config file if it's not there.
    if not os.path.isfile(prefs_file):
        tracking_id = input('Enter Amazon Associates Tracking ID: ')
        save_tracking_id(tracking_id)
        sys.exit(0)

    if args.show_tracking_id:
        print(load_tracking_id())
        sys.exit(0)

    if args.set_tracking_id:
        save_tracking_id(args.set_tracking_id)
        print("Tracking ID updated: {}".format(args.set_tracking_id))
        sys.exit(0)

    if args.tracking_id is None:
        tracking_id = load_tracking_id()
    else:
        tracking_id = args.tracking_id

    via_clipboard = False

    if args.amazon_url is None:
        url = pyperclip.paste()
        via_clipboard = True
    else:
        url = args.amazon_url

    if not brocket.is_amazon_url(url):

        notify(
            title='Brocket Error',
            subtitle='Invalid URL',
            message='Not an Amazon URL on the clipboard.',
        )

        sys.exit(1)

    amazon_assocate_url = brocket.process_url(url, tracking_id)

    if via_clipboard:
        msg = (
            "Adding the tracking {} to the URL {} and putting it on the"
            " clipboard."
        )

        print(msg.format(tracking_id, url))

        pyperclip.copy(amazon_assocate_url)

        notify(
            title='Brocket Success',
            subtitle='URL Processed',
            message='Amazon URL Saved to Clipboard.',
            openUrl=amazon_assocate_url
        )

    print(amazon_assocate_url)


if __name__ == "__main__":
    main()
