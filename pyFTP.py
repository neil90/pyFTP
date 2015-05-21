import	logging
import	os
import	smtplib
from 	email.MIMEMultipart 	import MIMEMultipart
from 	email.MIMEText 			import MIMEText
from 	email.mime.application 	import MIMEApplication
from	ftplib 		import FTP 
from 	datetime	import datetime

class Callback(object):
	def __init__(self, totalsize,fp):
		self.totalsize = totalsize
		self.fp = fp
		self.received = 0

	def __call__(self,data):
		self.fp.write(data)
		self.received += len(data)
		self.percent = '%.2f%%' % (100.0*self.received/self.totalsize)
		print '\r%s completed of %s\r' % (self.percent, os.path.basename(self.fp.name)),

class Getfiles(object):
	def __init__(self, website):
		self.ftp = FTP(website)
		self.ftp.login()
		logging.info('Connected to FTP Site')

	def ftpdownload(self,dlfile, svfile):

		self.src = dlfile
		self.ftp.sendcmd('Type i') #set to image(binary data)
		self.size = self.ftp.size(self.src)

		self.f = open(svfile, 'wb')
		self.w = Callback(self.size, self.f)
		self.ftp.retrbinary('RETR %s' % self.src, self.w, 32768)
		self.f.close()

		logging.info('Downloaded %s', os.path.basename(self.f.name))
		print '%s is fully downloaded!' % os.path.basename(self.f.name)

	def ftpclose(self):
		self.ftp.close()

def send_email():

	email_user = "serviceacc@gmail.com"
	email_pwd = "password"

	msg = MIMEMultipart()
	msg['From'] 	= 'serviceacc@gmail.com'
	msg['To']		= 'admins@gmail.com'
	msg['Subject']	= 'FTP Job Failed!'

	body = MIMEText("Please look at attached ftpfile.log to see why the Job failed")
	msg.attach(body)

	body = MIMEApplication(open("ftpfile.log", "rb").read(), 'log', name ='ftpfile.log')
	body.add_header('Content-Disposition', 'attachment', filename ='ftpfile %s.log' % (datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
	msg.attach(body)


	try:
	    server = smtplib.SMTP("smtp.gmail.com", 587) #or port 465 doesn't seem to work!
	    server.ehlo()
	    server.starttls()
	    server.login(gmail_user, gmail_pwd)
	    server.sendmail(msg['From'], msg['To'], msg.as_string())
	    #server.quit()
	    server.close()
	    print 'Successfully sent the mail'
	except Exception, e:
		print 'Failed to send email'
		logging.error('Email related: %s',e)

		

def main():

	#USER SETUP
	ftpsetup =	{ 
					'ftpsite'	: 'mirror.reverse.net',
					'ftpfile'	: ['pub/apache/ace/apache-ace-2.0.1/apache-ace-2.0.1-src.zip','pub/apache/allura/allura-1.2.1.tar.gz'],
					'savedir'	: 'C:/ftpsaves/',
				}


	try: 
		os.makedirs(ftpsetup['savedir'])
	except OSError:
		if not os.path.isdir(ftpsetup['savedir']):
			raise


	try:
		dl = Getfiles(ftpsetup['ftpsite'])
		for remote_file in ftpsetup['ftpfile']:
			local_file = os.path.join(ftpsetup['savedir'], remote_file.split("/")[-1])
			dl.ftpdownload(remote_file, local_file)
	except Exception, e:
		logging.error('FTP dir/file related: %s',e)
		send_email()
		exit()


	dl.ftpclose()


if __name__ == "__main__":

	logging.basicConfig(filename = 'ftpfile.log', level = logging.INFO,
		format = '%(asctime)s: %(levelname)s %(name)s: %(message)s')


	main()