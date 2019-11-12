# imap-eml-python
imapclone.py - Python script which clones all folders from one server to another


./imapclone.py -h
usage: imapclone.py [-h] -s HOST [-P PORT] -u USERNAME -p PASSWORD [--ssl]
                    [-l LOCAL_FOLDER] [-rs REMOTE_HOST] [-ru REMOTE_USERNAME]
                    [-rp REMOTE_PASSWORD] [-rP REMOTE_PORT] [--rssl]

Dump IMAP account into .eml files or another server

optional arguments:
  -h, --help           show this help message and exit
  -s HOST              IMAP host, like imap.gmail.com or mail1.ukisp.com
  -P PORT              IMAP port
  -u USERNAME          IMAP username
  -p PASSWORD          IMAP password
  --ssl                connects using ssl
  -l LOCAL_FOLDER      Local folder where to save .eml files if remote server args are not passed
  -rs REMOTE_HOST      Remote Server
  -ru REMOTE_USERNAME  Remote Server Username
  -rp REMOTE_PASSWORD  Remote Server Password
  -rP REMOTE_PORT      Remote Server Port
  --rssl               connects using ssl on remote server
