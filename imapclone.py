#!/usr/bin/python2

import imaplib, argparse, sys, os
imaplib._MAXLINE = 40000

argparser = argparse.ArgumentParser(description="Dump IMAP account into .eml files")
argparser.add_argument('-s', dest='host', help="IMAP host, like imap.gmail.com or mail1.ukisp.com", required=True)
argparser.add_argument('-P', dest='port', help="IMAP port", default='143')
argparser.add_argument('-u', dest='username', help="IMAP username", required=True)
argparser.add_argument('-p', dest='password', help="IMAP password", required=True)
argparser.add_argument("--ssl", help="connects using ssl", action="store_true")
argparser.add_argument('-l', dest='local_folder', help="Local folder where to save .eml files", default='.')
argparser.add_argument('-rs', dest='remote_host', help="Remote Server")
argparser.add_argument('-ru', dest='remote_username', help="Remote Server Username")
argparser.add_argument('-rp', dest='remote_password', help="Remote Server Password")
argparser.add_argument('-rP', dest='remote_port', help="Remote Server Port", default='143')
argparser.add_argument("--rssl", help="connects using ssl on remote server", action="store_true")
args = argparser.parse_args()

def Clone_Local(FOLDER):
        print ("Cloning folder: ", FOLDER)
        M.select(FOLDER)
        savefolder = (args.local_folder + "/" + args.username + "/" + FOLDER)
        try:
                os.stat(savefolder)
        except:
                os.makedirs(savefolder, 0775)
        rv, data = M.search(None, "ALL")

        if rv != 'OK':
                print "No messages found in folder ", FOLDER
                return

        for num in data[0].split():
                rv, data = M.fetch(num, '(RFC822)')
                if rv != 'OK':
                        print "ERROR getting message: ", num
                        return
                f = open('%s/%s.eml' %(savefolder, num), 'wb')
                f.write(data[0][1])
                f.close

def Clone_Remote(FOLDER):
        print ("Cloning folder: ", FOLDER)
        M.select(FOLDER)
                # Get all Read messages
        rv, data = M.search(None, "Seen")
        if rv != 'OK':
                print "No Read messages found in folder ", FOLDER
                return
        for num in data[0].split():
                rv, data = M.fetch(num, '(RFC822)')
                if rv != 'OK':
                        print "ERROR getting message: ", num
                        return
                try:
                        RM.create(FOLDER)
                except:
                        print "Folder already excists ", FOLDER
                try:
                        RM.subscribe(FOLDER)
                except:
                        return
                RM.append(FOLDER, '\SEEN', None, data[0][1])
                rv, data = M.search(None, "UnSeen")
        if rv != 'OK':
                print "No Unread messages found in folder ", FOLDER
                return
        for num in data[0].split():
                rv, data = M.fetch(num, '(RFC822)')
                if rv != 'OK':
                        print "ERROR getting message: ", num
                        return
                try:
                        RM.create(FOLDER)
                except:
                        print "Folder already excists ", FOLDER
                try:
                        RM.subscribe(FOLDER)
                except:
                        return
                RM.append(FOLDER, None, None, data[0][1])


def main():
        global M
        global RM
        global Remote
        print ("Cloning account: ", args.username)
        if args.ssl:
                print "Connecting to server on SSL"
                M = imaplib.IMAP4_SSL(args.host, args.port)
        else:
                M = imaplib.IMAP4(args.host, args.port)
        if args.rssl:
                RM = imaplib.IMAP4_SSL(args.remote_host, args.remote_port)
                Remote = "True"
                RM.login(args.remote_username, args.remote_password)
        elif args.rs:
                RM = imaplib.IMAP4(args.remote_host, args.remote_port)
                RM.login(args.remote_username, args.remote_password)
                Remote = "True"
        else:
                Remote = "False"
        M.login(args.username, args.password)
        for f in M.list()[1]:
                fn = f.split(' "')
                if Remote == False:
                        Clone_Local(fn[2].replace('"',''),)
                else:
                        Clone_Remote(fn[2].replace('"',''),)
        M.logout()
        if Remote == "True":
                RM.logout()

if __name__ == "__main__":
        main()
