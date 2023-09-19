# Heraud

A plain-text SMTP sending tool for Windows.

![Heraud screenshot](heraud-screenshot.jpg)

This simple Python script remembers your SMTP account details (securely protecting it with a PIN using [Fernet](https://cryptography.io/en/latest/fernet/) cryptography) and launches the good old Windows Notepad to let you compose your email.

It’s a convenience tool you might find neat if, for example, you have an account set up with an SMTP service provider such as Amazon SES, Zoho Mail, or Mailgun, and occasionally want to fire off emails without opening full-featured email clients.

“[Heraud](https://en.wiktionary.org/wiki/heraud)” is Middle English for “herald”.

## Requirements and setup

This tool is made for Windows (tested with Windows 11). For convenient launching, it uses a shebang line to run in a virtual environment; therefore it assumes that the [`py` launcher](https://docs.python.org/3/using/windows.html#shebang-lines) is installed. The shebang line in turn assumes that the virtual environment is installed in a `venv` directory next to `heraud.py` (e.g., created with `py -m venv venv`). The virtual environment is to be populated with `pip install -r requirements.txt`. With this setup, you can create a basic Start menu shortcut with a command like `py C:\Users\Foo\heraud\heraud.py`, and this tool will always be only a few keystrokes away. (Caveat: error messages, for example those due to SMTP issues, won’t be visible in this setup as the terminal will close immediately after printing the exception. One solution is to use a batch file to call `heraud.py`, and add a [`pause`](https://ss64.com/nt/pause.html) at the end.)

Of course, if you’re the type to actually use this tool, you can ignore all that and use the script your way, modifying it as you please. In any case, you’ll probably want to keep the `cryptography` dependency up-to-date.

This tool is tested with Python 3.11, although older versions will probably work too.
