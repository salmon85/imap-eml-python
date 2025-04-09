import imaplib
import argparse
import sys
import os

try:
    from tqdm import tqdm
except ImportError:
    print("Missing tqdm, install with: pip install tqdm or pip install --user tqdm")
    sys.exit(1)

imaplib._MAXLINE = 1000000

argparser = argparse.ArgumentParser(description="Dump IMAP account onto external server")
argparser.add_argument('-s', dest='host', help="IMAP host", required=True)
argparser.add_argument('-P', dest='port', help="IMAP port", default='143')
argparser.add_argument('-u', dest='username', help="IMAP username", required=True)
argparser.add_argument('-p', dest='password', help="IMAP password", required=True)
argparser.add_argument("--ssl", help="Connect using SSL", action="store_true")
argparser.add_argument('-rs', dest='remote_host', help="Remote Server")
argparser.add_argument('-ru', dest='remote_username', help="Remote Server Username", required=True)
argparser.add_argument('-rp', dest='remote_password', help="Remote Server Password", required=True)
argparser.add_argument('-rP', dest='remote_port', help="Remote Server Port", default='143')
argparser.add_argument("--rssl", help="Connect using SSL on remote server", action="store_true")
args = argparser.parse_args()

class IMAPCopy:
    def connect(self):
        try:
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
        except Exception as e:
            print(f"Connection error: {e}")
            sys.exit(1)

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

        print("Cloning Read Messages")
        rv, data = self.src.search(None, "SEEN")
        if rv != "OK":
            print(f"No messages found in folder: {folder}")
            return
        for message in tqdm(data[0].split()):
            mrv, mdata = self.src.fetch(message, "(RFC822)")
            if mrv != "OK":
                print(f"Error getting message: {message}")
                continue
            try:
                self.dest.append(f'"{folder}"', '\\Seen', None, mdata[0][1])
            except Exception as e:
                print(f"Issues creating mail in folder {folder}: {e}")

        print("Cloning Unread Messages")
        rv, data = self.src.search(None, "UNSEEN")
        if rv != "OK":
            print(f"No messages found in folder: {folder}")
            return
        for message in tqdm(data[0].split()):
            mrv, mdata = self.src.fetch(message, "(RFC822)")
            if mrv != "OK":
                print(f"Error getting message: {message}")
                continue
            try:
                self.dest.append(f'"{folder}"', None, None, mdata[0][1])
            except Exception as e:
                print(f"Issues creating mail in folder {folder}: {e}")
        print()

    def clone_all(self):
        self.list = []
        status, folders = self.src.list()
        if status != "OK" or folders is None:
            print("Failed to retrieve folder list.")
            return

        print("Raw folder list:")
        for f in folders:
            print(f.decode())

        for folder in folders:
            try:
                decoded = folder.decode()
                # Get the folder name: it's the third element if you split by space max 2 times
                parts = decoded.split(' ', 2)
                if len(parts) == 3:
                    folder_name = parts[2].strip()
                    # Remove surrounding quotes if present
                    folder_name = folder_name.strip('"')
                    if folder_name and folder_name != '.':
                        self.list.append(folder_name)
            except Exception as e:
                print(f"Error parsing folder: {e}")
                continue

        if not self.list:
            print("No folders found.")
            return

        print("The following folders will be cloned:")
        for item in self.list:
            print(item)
        print()

        for item in self.list:
            self.clone_folder(item)

def main():
    connection = IMAPCopy()
    connection.connect()
    connection.clone_all()

if __name__ == "__main__":
    main()