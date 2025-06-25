import tkinter as tk
from tkinter import messagebox
from tkinter import BooleanVar
import imaplib
import argparse
import threading
import sys
import re
import socket
socket.setdefaulttimeout(300)


class GuiOutput:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.after(0, self._append_text, message)

    def flush(self):
        pass

    def _append_text(self, message):
        self.text_widget.insert(tk.END, message)
        self.text_widget.see(tk.END)


class IMAPCopy:
    def connect(self, args):
        if args.ssl:
            self.src = imaplib.IMAP4_SSL(args.host, int(args.port))
        else:
            self.src = imaplib.IMAP4(args.host, int(args.port))
        self.src.login(args.username, args.password)

        if args.rssl:
            self.dest = imaplib.IMAP4_SSL(args.remote_host, int(args.remote_port))
        else:
            self.dest = imaplib.IMAP4(args.remote_host, int(args.remote_port))
        self.dest.login(args.remote_username, args.remote_password)

    def clone_folder(self, folder):
        print(f"\n📁 Cloning folder: {folder}")
        try:
            self.src.select(f'"{folder}"')
        except Exception as e:
            print(f"Issues connecting to folder {folder}: {e}")
            return

        # Get the destination delimiter
        status, data = self.dest.list('""', 'INBOX')
        if status == "OK" and data:
            delimiter_match = re.search(r'\((?:[^)]*)\)\s+"([^"]+)"\s+INBOX', data[0].decode())
            delimiter = delimiter_match.group(1) if delimiter_match else "/"
        else:
            delimiter = "/"

        # Build destination folder path
        # Only prefix with INBOX if the folder is not already rooted under INBOX or is not INBOX itself
        if folder.upper() != "INBOX" and not folder.upper().startswith("INBOX" + delimiter):
            dest_folder = f"INBOX{delimiter}{folder}"
        else:
            dest_folder = folder

        try:
            self.dest.create(f'"{dest_folder}"')
        except imaplib.IMAP4.error as e:
            print(f"⚠️ Could not create folder '{dest_folder}': {e}. Attempting to continue...")

        try:
            self.dest.subscribe(f'"{dest_folder}"')
        except imaplib.IMAP4.error:
            pass  # Some servers auto-subscribe; ignore if it fails
        # Always check response of select()
        resp, _ = self.dest.select(f'"{dest_folder}"')
        if resp != "OK":
            print("⚠️ Destination session dropped or folder not selectable. Reconnecting...")
            self.dest.logout()
            if self.args.rssl:
                self.dest = imaplib.IMAP4_SSL(self.args.remote_host, int(self.args.remote_port))
            else:
                self.dest = imaplib.IMAP4(self.args.remote_host, int(self.args.remote_port))
            self.dest.login(self.args.remote_username, self.args.remote_password)
            resp, _ = self.dest.select(f'"{dest_folder}"')
            if resp != "OK":
                print(f"❌ Failed to select destination folder '{dest_folder}' after reconnect.")
                return

        BATCH_SIZE = 1000

        # Scan existing Message-IDs in batches
        status, existing_data = self.dest.search(None, 'ALL')
        existing_ids = set()

        if status == "OK":
            all_ids = existing_data[0].split()
            for batch_start in range(0, len(all_ids), BATCH_SIZE):
                batch = all_ids[batch_start:batch_start + BATCH_SIZE]
                id_string = b",".join(batch).decode()
                print(f"📥 Scanning Message-ID headers {batch_start + 1}–{batch_start + len(batch)} of {len(all_ids)}")

                try:
                    _, msg_data = self.dest.fetch(id_string, "(BODY.PEEK[HEADER.FIELDS (MESSAGE-ID)])")
                except Exception as e:
                    print(f"❌ Failed to fetch batch of headers: {e}")
                    continue

                if msg_data:
                    for item in msg_data:
                        if not isinstance(item, tuple):
                            continue
                        header = item[1].decode(errors='ignore')
                        match = re.search(r'Message-ID:\s*<([^>]+)>', header, re.IGNORECASE)
                        if match:
                            existing_ids.add(match.group(1).strip())

        status, data = self.src.search(None, 'ALL')
        if status != "OK" or not data or not data[0]:
            print(f"⚠️ No messages found in source folder '{folder}'")
            return

        messages = [m for m in data[0].split() if m.decode(errors='ignore').isdigit()]
        print(f"🔎 Found {len(messages)} messages to process in folder '{folder}'")
        for batch_start in range(0, len(messages), BATCH_SIZE):
            batch = messages[batch_start:batch_start + BATCH_SIZE]
            print(f"\n📦 Processing batch {batch_start + 1}–{batch_start + len(batch)} of {len(messages)}")

            for message in batch:
                #if int(message.decode()) <= 75510:
                #    print("🚫 Skipping already processed")
                #    continue
                print(f"⏳ Fetching message ID {message.decode()}...")
                try:
                    mrv, mdata = self.src.fetch(message, "(RFC822)")
                except socket.timeout:
                    print(f"⏱️ Timeout while fetching message {message.decode()}. Skipping...")
                    continue
                if mrv != "OK":
                    print(f"❌ Error getting message: {message.decode()}")
                    continue

                raw = mdata[0][1]
                match = re.search(rb'Message-ID:\s*<([^>]+)>', raw, re.IGNORECASE)
                msgid = match.group(1).decode().strip() if match else None

                if msgid and msgid in existing_ids:
                    print(f"🔁 Skipping duplicate Message-ID <{msgid}>")
                    continue

                try:
                    self.dest.append(f'"{dest_folder}"', None, None, raw)
                    print(f"✅ Message {message.decode()} appended.")
                    if msgid:
                        existing_ids.add(msgid)
                except (imaplib.IMAP4.abort, imaplib.IMAP4.error, OSError) as e:
                    print(f"❌ Append failed due to connection error: {e}. Reconnecting...")
                    try:
                        self.dest.logout()
                    except Exception:
                        pass
                    if self.args.rssl:
                        self.dest = imaplib.IMAP4_SSL(self.args.remote_host, int(self.args.remote_port))
                    else:
                        self.dest = imaplib.IMAP4(self.args.remote_host, int(self.args.remote_port))
                    self.dest.login(self.args.remote_username, self.args.remote_password)
                    self.dest.select(f'"{dest_folder}"')

                    try:
                        self.dest.append(f'"{dest_folder}"', None, None, raw)
                        print(f"✅ (Retry) Message {message.decode()} appended.")
                        if msgid:
                            existing_ids.add(msgid)
                    except Exception as e2:
                        print(f"❌ Final failure appending message {message.decode()}: {e2}")

    def clone_all(self, args):
        self.args = args
        status, folders = self.src.list()
        if status != "OK" or folders is None:
            print("Failed to retrieve folder list.")
            return

        folder_pattern = re.compile(r'(?P<flags>\(.*?\)) "(?P<delimiter>.*)" (?P<name>.*)')
        folder_list = []

        for folder in folders:
            try:
                decoded = folder.decode()
                match = folder_pattern.match(decoded)
                if match:
                    folder_name = match.group("name").strip('"')
                    if folder_name and folder_name != ".":
                        folder_list.append(folder_name)
            except Exception as e:
                print(f"Error parsing folder: {e}")
                continue

        if not folder_list:
            print("No folders found.")
            return

        print("The following folders will be cloned:")
        for item in folder_list:
            print(item)
        print()

        for item in folder_list:
            self.clone_folder(item)


def run_gui():
    def run_imap_clone():
        host = src_host.get()
        port = src_port.get()
        username = src_user.get()
        password = src_pass.get()
        ssl = src_ssl.get()

        remote_host_ = dst_host.get()
        remote_port_ = dst_port.get()
        remote_user_ = dst_user.get()
        remote_pass_ = dst_pass.get()
        remote_ssl_ = dst_ssl.get()

        if not all([host, port, username, password, remote_host_, remote_port_, remote_user_, remote_pass_]):
            messagebox.showerror("Missing Info", "Please fill in all required fields.")
            return

        args = argparse.Namespace(
            host=host,
            port=port,
            username=username,
            password=password,
            ssl=ssl,
            remote_host=remote_host_,
            remote_port=remote_port_,
            remote_username=remote_user_,
            remote_password=remote_pass_,
            rssl=remote_ssl_
        )

        def clone_thread():
            try:
                copier = IMAPCopy()
                copier.connect(args)
                copier.clone_all(args)
                print("\n✅ Cloning completed.")
            except Exception as e:
                print(f"\n❌ Error: {e}")

        sys.stdout = sys.stderr = GuiOutput(output_box)
        threading.Thread(target=clone_thread, daemon=True).start()

    global src_host, src_port, src_user, src_pass, src_ssl
    global dst_host, dst_port, dst_user, dst_pass, dst_ssl, output_box

    root = tk.Tk()
    root.title("IMAP Cloner")
    root.geometry("700x700")

    tk.Label(root, text="Source IMAP Server", font=("Arial", 12, "bold")).pack(pady=5)
    tk.Label(root, text="Host:").pack()
    src_host = tk.Entry(root, width=60)
    src_host.pack()

    tk.Label(root, text="Port:").pack()
    src_port = tk.Entry(root, width=60)
    src_port.insert(0, "143")
    src_port.pack()

    tk.Label(root, text="Username:").pack()
    src_user = tk.Entry(root, width=60)
    src_user.pack()

    tk.Label(root, text="Password:").pack()
    src_pass = tk.Entry(root, width=60, show="*")
    src_pass.pack()

    src_ssl = BooleanVar()
    tk.Checkbutton(root, text="Use SSL", variable=src_ssl).pack()

    tk.Label(root, text="Destination IMAP Server", font=("Arial", 12, "bold")).pack(pady=10)
    tk.Label(root, text="Host:").pack()
    dst_host = tk.Entry(root, width=60)
    dst_host.pack()

    tk.Label(root, text="Port:").pack()
    dst_port = tk.Entry(root, width=60)
    dst_port.insert(0, "143")
    dst_port.pack()

    tk.Label(root, text="Username:").pack()
    dst_user = tk.Entry(root, width=60)
    dst_user.pack()

    tk.Label(root, text="Password:").pack()
    dst_pass = tk.Entry(root, width=60, show="*")
    dst_pass.pack()

    dst_ssl = BooleanVar()
    tk.Checkbutton(root, text="Use SSL", variable=dst_ssl).pack()

    tk.Button(root, text="Start Cloning", command=run_imap_clone, bg="blue", fg="white", height=2).pack(pady=10)

    output_box = tk.Text(root, height=20, width=80, bg="black", fg="white")
    output_box.pack(pady=10)

    root.mainloop()


def run_cli():
    parser = argparse.ArgumentParser(description="Dump IMAP account onto external server")
    parser.add_argument('-s', dest='host', help="IMAP host", required=True)
    parser.add_argument('-P', dest='port', help="IMAP port", default='143')
    parser.add_argument('-u', dest='username', help="IMAP username", required=True)
    parser.add_argument('-p', dest='password', help="IMAP password", required=True)
    parser.add_argument("--ssl", help="Connect using SSL", action="store_true")
    parser.add_argument('-rs', dest='remote_host', help="Remote Server", required=True)
    parser.add_argument('-ru', dest='remote_username', help="Remote Server Username", required=True)
    parser.add_argument('-rp', dest='remote_password', help="Remote Server Password", required=True)
    parser.add_argument('-rP', dest='remote_port', help="Remote Server Port", default='143')
    parser.add_argument("--rssl", help="Connect using SSL on remote server", action="store_true")
    parser.add_argument('--from-folder', help="Start cloning from this folder name (inclusive)")
    args = parser.parse_args()

    copier = IMAPCopy()
    copier.connect(args)
    copier.clone_all(args)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        run_gui()
    else:
        run_cli()
