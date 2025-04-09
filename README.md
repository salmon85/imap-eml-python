# imap-eml-python
imapclone.py - Python script which clones all folders from one server to another


python3 imapclone.py -h
usage: imapclone.py  [-h] -s HOST [-P PORT] -u USERNAME -p PASSWORD [--ssl] [-rs REMOTE_HOST] 
                      -ru REMOTE_USERNAME -rp REMOTE_PASSWORD [-rP REMOTE_PORT] [--rssl]

Dump IMAP account onto external server

options:
  -h, --help           show this help message and exit
  -s HOST              IMAP host
  -P PORT              IMAP port
  -u USERNAME          IMAP username
  -p PASSWORD          IMAP password
  --ssl                Connect using SSL
  -rs REMOTE_HOST      Remote Server
  -ru REMOTE_USERNAME  Remote Server Username
  -rp REMOTE_PASSWORD  Remote Server Password
  -rP REMOTE_PORT      Remote Server Port
  --rssl               Connect using SSL on remote server
