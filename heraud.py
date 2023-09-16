#!venv/Scripts/python

import base64
import json
import secrets
import smtplib
import sys
from email.message import EmailMessage
from getpass import getpass
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


BASE_DIR = Path(__file__).resolve().parent
SETTINGS_PATH = BASE_DIR / "settings.json"

KDF_ITERS = 1_000_000

settings = {
    "from_address": "",
    "smtp_host": "",
    "smtp_port": 587,
    "smtp_user": "",
    "smtp_pw_encrypted": "",
    "salt": "",
}


def retrieve_settings():
    if not SETTINGS_PATH.exists():
        return False
    with open(SETTINGS_PATH, "r", encoding="utf-8") as settings_file:
        disk_settings = json.loads(settings_file.read())
    for key, value in disk_settings.items():
        settings[key] = value
    return True


def derive_key(password, salt_bytes):
    password_bytes = password.encode()
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt_bytes,
        iterations=KDF_ITERS,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
    return key


def set_up():
    print("Configuring Heraud. Please input the following required settings.")
    settings["from_address"] = input(
        "From address (format: `Name <user@example.com>`): "
    )
    settings["smtp_host"] = input("SMTP host: ")
    settings["smtp_port"] = int(input("SMTP port: "))
    settings["smtp_user"] = input("SMTP user: ")

    smtp_pw = getpass("SMTP password: ")
    pin = getpass("Set PIN: ")

    salt_bytes = secrets.token_bytes(nbytes=16)
    key = derive_key(pin, salt_bytes)
    fernet = Fernet(key)
    token_b64bytes = fernet.encrypt(smtp_pw.encode())
    salt_b64bytes = base64.urlsafe_b64encode(salt_bytes)

    settings["smtp_pw_encrypted"] = token_b64bytes.decode()
    settings["salt"] = salt_b64bytes.decode()

    with open(SETTINGS_PATH, "w", encoding="utf-8") as settings_file:
        settings_file.write(json.dumps(settings, indent=4))

    print("Settings saved.")


def unlock_smtp_pw():
    pin = getpass("Enter PIN: ")
    salt_bytes = base64.urlsafe_b64decode(settings["salt"])
    key = derive_key(pin, salt_bytes)
    fernet = Fernet(key)
    try:
        smtp_pw_bytes = fernet.decrypt(settings["smtp_pw_encrypted"].encode())
        settings["smtp_pw"] = smtp_pw_bytes.decode()
    except InvalidToken:
        print("Invalid token error. The PIN might be wrong.")
        sys.exit()


def send_mail():
    msg = EmailMessage()
    msg["From"] = settings["from_address"]
    msg["To"] = input("To address (format: `Name <user@example.com>`): ")
    msg["Subject"] = input("Subject: ")
    msg.set_content(input("Body: "))  # TODO: use external editor?

    print("Connecting and sending...")

    smtp = smtplib.SMTP(settings["smtp_host"], port=settings["smtp_port"])
    smtp.starttls()
    smtp.login(settings["smtp_user"], settings["smtp_pw"])
    smtp.send_message(msg)
    smtp.quit()

    print("Done.")


def main():
    try:
        if not retrieve_settings():
            set_up()
        print(
            f"Sending as {settings['from_address']}",
            f"through {settings['smtp_host']}.",
        )
        unlock_smtp_pw()
        send_mail()
    except KeyboardInterrupt:
        print("\nExiting.")


if __name__ == "__main__":
    main()
