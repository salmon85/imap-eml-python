import imaplib, argparse, sys, os

argparser = argparse.ArgumentParser(description="Dump IMAP account into .eml files")
argparser.add_argument('-s', dest='host', help="IMAP host, like imap.gmail.com or mail1.ukisp.com", required=True)
argparser.add_argument('-P', dest='port', help="IMAP port", default='143')
argparser.add_argument('-u', dest='username', help="IMAP username", required=True)
argparser.add_argument('-p', dest='password', help="IMAP password", required=True)
argparser.add_argument("--ssl", help="connects using ssl", action="store_true")
argparser.add_argument('-l', dest='local_folder', help="Local folder where to save .eml files", default='.')
args = argparser.parse_args()

def doshit(FOLDER):
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
	

def main():
	global M
	if args.ssl:
		print "Connecting to server on SSL"
		M = imaplib.IMAP4_SSL(args.host, args.port)
	else:
		M = imaplib.IMAP4(args.host, args.port)
	M.login(args.username, args.password)
	for f in M.list()[1]:
		fn = f.split(' "')
		doshit(fn[2].replace('"',''),)
	M.logout()

if __name__ == "__main__":
	main()
