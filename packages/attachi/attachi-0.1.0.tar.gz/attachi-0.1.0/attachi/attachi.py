import os
import sys
import logging
import datetime
import subprocess

logger = logging.getLogger("attachi")
logger.setLevel(logging.DEBUG)

formatter = formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)

try:
    ch = logging.FileHandler(filename="attachi.log", mode="a+")
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
except Exception as e:
    print('Could not create logging file, will log on command line instead!')

class Attachi(object):

    def __init__(self, qcode, fpath, comment, username = "", outdir = ""):
        self.code = qcode
        self.path = fpath
        self.comment = comment
        self.username = username
        self.outdir = outdir

    def run(self):
        now = str(datetime.datetime.now())

        USER = self.username
        PROJECT = self.code
        PATH = self.path
        COMMENT = self.comment
        target = os.getcwd() if not self.outdir else self.outdir

        logger.debug("Want to upload Attachment "+PATH+" ("+COMMENT+") to openBIS project "+PROJECT+" as user "+USER)

        if os.path.isdir(PATH):
            logger.debug(PATH+" is a directory. Quitting.")
            sys.exit(PATH+" is a directory. You can only upload files as attachments.")
        f = os.path.basename(PATH)
        
        timestamp = now.replace(" ","").replace(":","").replace(".","").replace("-","")
        base = PROJECT+"000A"
        barcode = base+checksum(base)
        folder = os.path.join(target, barcode+"_"+timestamp)
        os.system("mkdir "+folder)
        logger.debug("Folder "+folder+" created")

        metadata = open(os.path.join(folder,"metadata.txt"),"w")
        if USER:
	        metadata.write("user="+USER+"\n")
        metadata.write("info="+COMMENT+"\n")
        metadata.write("barcode="+PROJECT+"000\n")
        metadata.write("type=Results\n")
        metadata.close()

        logger.debug("Wrote metadata file to folder "+folder)
        cmd = "cp "+PATH+" "+os.path.join(folder,f)
        logger.info("copying "+PATH+" to the dropbox...")
        subprocess.call(cmd.split(" "))
        logger.debug("Copying of data file done. checking existence...")
        exists = os.path.isfile(os.path.join(folder,f))
        logger.debug(str(exists))
        if not exists:
            logger.info("File could not be copied!")

def now():
    return str(datetime.datetime.now())

def mapToDigit(num):
	num += 48 # 0 to 9
	if num > 57:
		num += 7 # A to X
	return chr(num)

def checksum(name):
	i = 1
	sum = 0
	for x in name:
		sum += (ord(x))*i
		i += 1
	return mapToDigit(sum%34) # 10 numbers + 24 letters
