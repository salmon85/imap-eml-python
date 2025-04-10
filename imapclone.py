import tkinter as tk
from tkinter import messagebox
from tkinter import BooleanVar
import imaplib
import argparse
import threading
import sys
import re


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
        print(f"Cloning folder: {folder}")
        try:
            self.src.select(f'"{folder}"')
        except Exception as e:
            print(f"Issues connecting to folder {folder}: {e}")
            return

        try:
            self.dest.create(f'"{folder}"')
        except Exception:
            print(f"Folder already exists: {folder}")

        try:
            self.dest.subscribe(f'"{folder}"')
        except Exception:
            pass

        for flag, label in [("SEEN", "\\Seen"), ("UNSEEN", None)]:
            print(f"Cloning {flag.lower().capitalize()} Messages")
            rv, data = self.src.search(None, flag)
            if rv != "OK":
                print(f"No messages found in folder: {folder}")
                continue
            for message in data[0].split():
                mrv, mdata = self.src.fetch(message, "(RFC822)")
                if mrv != "OK":
                    print(f"Error getting message: {message}")
                    continue
                try:
                    self.dest.append(f'"{folder}"', label, None, mdata[0][1])
                except Exception as e:
                    print(f"Issues creating mail in folder {folder}: {e}")
            print()

    def clone_all(self, args):
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
    args = parser.parse_args()

    copier = IMAPCopy()
    copier.connect(args)
    copier.clone_all(args)


# Entry point: decide GUI vs CLI
if __name__ == "__main__":
    if len(sys.argv) == 1:
        run_gui()
    else:
        run_cli()
