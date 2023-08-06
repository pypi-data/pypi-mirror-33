import os
import sys
import argparse
import smtplib
from email.mime.text import MIMEText
from p3mail import consts
from pathlib import Path
from configparser import ConfigParser


def parse_config(fname=None):
    config_fname = Path.home() / ".config" / consts.prg_name / "config"

    if fname is not None:
        config_fname = fname

    config = ConfigParser()
    if len(config.read(config_fname)) == 0:
        raise ValueError("'{}' is an invalid config file".format(config_fname))
    return config["DEFAULT"]


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "subject", help="The subject of the mail", type=str)

    parser.add_argument(
        "--to", help="The receiver's address. If not provided, \
        it will look at the config file", type=str)

    # use dest=dest because 'from' is a Python reserved word
    parser.add_argument(
        "--from", help="The sender's address. If not provided, \
        it will look at the config file", type=str, dest="dest")

    parser.add_argument(
        "--config", help="Specify a custom location for the config file",
        type=str)

    return parser.parse_args()


def main():
    args = parse_args()

    custom_config_fname = args.config or None
    config = parse_config(fname=custom_config_fname)

    msg_text = sys.stdin.read()

    if len(msg_text) == 0:
        print("empty message body", file=sys.stderr)
        return

    msg = MIMEText(msg_text)
    msg['Subject'] = args.subject
    msg['From'] = args.dest or config["From"]
    msg['To'] = args.to or config["To"]

    s = smtplib.SMTP(config["SmtpServer"], port=config["SmtpPort"])

    smtp_user = config['SmtpUser'] or os.environ["SMTP_USER"]
    smtp_pass = config['SmtpPass'] or os.environ["SMTP_PASS"]
    s.login(smtp_user, smtp_pass)
    s.send_message(msg)
    s.quit()


if __name__ == '__main__':
    main()
