import imaplib
import argparse
import sys
import os
try:
    from tqdm import tqdm
except:
    print("Missing tqdm, install with pip install tqdm or pip install --user tqdm")
    sys.exit(1)

imaplib._MAXLINE = 1000000

argparser = argparse.ArgumentParser(description="Dump IMAP account into .eml files")
argparser.add_argument(
    '-s', dest='host', help="IMAP host, like imap.gmail.com or mail1.ukisp.com", required=True)
argparser.add_argument('-P', dest='port', help="IMAP port", default='143')
argparser.add_argument('-u', dest='username', help="IMAP username", required=True)
argparser.add_argument('-p', dest='password', help="IMAP password", required=True)
argparser.add_argument("--ssl", help="connects using ssl", action="store_true")
argparser.add_argument('-rs', dest='remote_host', help="Remote Server")
argparser.add_argument('-ru', dest='remote_username', help="Remote Server Username", required=True)
argparser.add_argument('-rp', dest='remote_password', help="Remote Server Password", required=True)
argparser.add_argument('-rP', dest='remote_port', help="Remote Server Port", default='143')
argparser.add_argument("--rssl", help="connects using ssl on remote server", action="store_true")
args = argparser.parse_args()


class imapcopy:
    def __init__(self):
        return

    def connect(self):
        if args.ssl:
            self.src = imaplib.IMAP4_SSL(args.host, args.port)
            self.src.login(args.username, args.password)
        else:
            self.src = imaplib.IMAP4(args.host, args.port)
            self.src.login(args.username, args.password)
        if args.rssl:
            self.dest = imaplib.IMAP4_SSL(args.remote_host, args.remote_port)
            self.dest.login(args.remote_username, args.remote_password)
        else:
            self.dest = imaplib.IMAP4(args.remote_host, args.remote_port)
            self.dest.login(args.remote_username, args.remote_password)
        return

    def clone_folder(self, folder):
        print("""Cloning folder: """, folder)
        try:
            self.src.select("""\""""+str(folder)+"""\"""")
        except:
            print("""Issues connecting to folder: """, folder)
        try:
            self.dest.create("""\""""+str(folder)+"""\"""")
        except:
            print("""Folder already exists: """, folder)
        try:
            self.dest.subscribe("""\""""+str(folder)+"""\"""")
        except:
            return
        print("""Cloning Read Messages""")
        rv, data = self.src.search(None, "Seen")
        if rv != """OK""":
            print("""No messages found in folder: """, folder)
            return
        for message in tqdm(data[0].split()):
            mrv, mdata = self.src.fetch(message, """(RFC822)""")
            if mrv != """OK""":
                print("""Error getting message: """, message)
                return
            try:
                self.dest.append("""\""""+str(folder)+"""\"""", '\SEEN', None, mdata[0][1])
            except:
                print("""Issues creating mail in folder: """, folder)
                return
        print("""Cloning Unread Messages""")
        rv, data = self.src.search(None, "UnSeen")
        if rv != """OK""":
            print("""No messages found in folder: """, folder)
            return
        for message in tqdm(data[0].split()):
            mrv, mdata = self.src.fetch(message, """(RFC822)""")
            if mrv != """OK""":
                print("""Error getting message: """, message)
                return
            try:
                self.dest.append("""\""""+str(folder)+"""\"""", None, None, mdata[0][1])
            except:
                print("""Issues creating mail in folder: """, folder)
                return
        print("\n")

    def clone_all(self):
        self.list = []
        for folder in self.src.list()[1]:
            self.list.append(folder.split('"."')[1].replace('"', '').lstrip())
        print("""The following folders will be cloned:""")
        for item in self.list:
            print(item)
        print("\n")
        for item in self.list:
            self.clone_folder(item)


def main():
    connection = imapcopy()
    connection.connect()
    connection.clone_all()


if __name__ == """__main__""":
    main()
