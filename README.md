# imap-eml-python

This project provides tools to clone email from one IMAP server to another using Python. It includes a command-line script (`imapclone.py`) and an optional graphical user interface (`imapclone-gui.py`).

Note: This doesn't work for any email systems that use oauth (gmail.com / outlook.com / live.com). This tool was meant for people whom aren't clued up with transferring the emails. If you're savvy enough to set up oauth, you're going to be savvy enough to transfer these without this tool.
Workarounds:
Gmail: Use the add another email account feature. https://support.google.com/mail/answer/21289?hl=en-EN
Outlook.com: They expect you to export the emails as .eml and then re-upload them to their server via settings > files > import

todo: option in the tool to download rather than clone via imap
---

## 📨 imapclone.py

`imapclone.py` is a Python script that connects to a source IMAP account and clones all folders and emails to a destination IMAP account.

### 🔧 Features

- Clones **all folders** and **emails** (both read and unread)
- Replicates folder structure
- Supports **SSL** and non-SSL connections
- Command-line interface with sensible defaults
- Shows progress using `tqdm`

---

### 🐍 Usage

```bash
python3 imapclone.py -h
```

```
usage: imapclone.py [-h] -s HOST [-P PORT] -u USERNAME -p PASSWORD [--ssl]
                    [-rs REMOTE_HOST] -ru REMOTE_USERNAME -rp REMOTE_PASSWORD
                    [-rP REMOTE_PORT] [--rssl]

Dump IMAP account onto external server

options:
  -h, --help           show this help message and exit
  -s HOST              IMAP host
  -P PORT              IMAP port (default: 143)
  -u USERNAME          IMAP username
  -p PASSWORD          IMAP password
  --ssl                Connect using SSL

  -rs REMOTE_HOST      Remote IMAP host
  -ru REMOTE_USERNAME  Remote IMAP username
  -rp REMOTE_PASSWORD  Remote IMAP password
  -rP REMOTE_PORT      Remote IMAP port (default: 143)
  --rssl               Connect using SSL on remote server
```

---

## 🖥️ GUI Launcher
Launching the script without any arguments will open with a gui.
Fill in your source and destination IMAP connection details, then click **Run Clone** to launch the sync process in the background.

### 💡 GUI Features

- No need to use command-line arguments
- Easy toggles for SSL
- 
---

### 🖼️ Screenshot

Below is a screenshot of the GUI:

![GUI Screenshot](image.png)

---

## 📦 Requirements

- Python 3.6+
- `tqdm`:
  ```bash
  pip install tqdm
  ```

Tkinter is included with most Python installations by default.

---

## ⚠️ Disclaimer

Use this tool at your own risk. It modifies mailboxes on both servers and is intended for legitimate backup and migration use only. Make sure you have the proper permissions and credentials for both servers.

---

## 🙌 Contributions

Feel free to open issues or pull requests to contribute improvements or bug fixes.
