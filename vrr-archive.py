#!/usr/bin/env python

SSH_CONFIG="/etc/ssh/ssh_config"
HOSTS=["vrr1", "vrr2", "vrr3", "vrr4", "vrr5", "vrr6", "vrr7", "vrr8"];

from jnpr.junos import Device
from lxml import etree
from time import strftime, gmtime
from calendar import timegm
import sys
import tarfile
import StringIO

# Default on error handler. Just print the exception message and exit
# Stack traces not necessary here
def onError(exception_type, exception, traceback):
    print "%s: %s" % (exception_type.__name__, exception)
sys.excepthook = onError

mode="save"
if len(sys.argv)<2:
	sys.stderr.write("Usage: %s save|load filename.tgz\n" % sys.argv[0])
	sys.exit(1)
else:
	mode = sys.argv[1].lower()

if len(sys.argv)<3:
	if mode=="load":
		sys.stderr.write("%s: Must specify filename.tgz with load method\n" % sys.argv[0])
		sys.exit(1)
	else:
		filename = "%s.tgz" % strftime("%Y%m%d%H%M%S", gmtime()) 
else:
	filename = sys.argv[2]

# Read from tar file and load on VRR
if mode=="load":

	tgz = tarfile.open(name=filename, mode='r:gz')
	sys.stderr.write("Reading from %s\n" % filename)

	for host in tgz.getnames():

		if (not host in HOSTS):
			sys.stderr.write("\tignoring %s\n" % host)
			break

		sys.stderr.write("\treading %s... " % host)
		file = tgz.extractfile(host)
		config = file.read()
		sys.stderr.write("\t%d byte(s)\n" % len(config))

		with Device(host=host, user="user", ssh_config=SSH_CONFIG, port=22) as dev:   
			dev.rpc.load_config(etree.fromstring(config), action="replace")
			dev.rpc.commit()

	tgz.close()

# Read from VRR and write to tar
else:

	tgz = tarfile.open(name=filename, mode='w:gz')
	sys.stderr.write("Writing to %s\n" % filename)

	for host in HOSTS:

		sys.stderr.write("\twriting %s... " % host)

		dev = Device(host=host, user="user", ssh_config=SSH_CONFIG, port=22)
		dev.open()

		file = StringIO.StringIO()

		with Device(host=host, user="user", ssh_config=SSH_CONFIG, port=22) as dev:   
			file.write(etree.tostring(dev.rpc.get_config()))

		file.flush()
		file.name=host

		tarinfo = tarfile.TarInfo(name=host)
		tarinfo.size = file.tell()
		tarinfo.mtime = timegm(gmtime())

		file.seek(0)

		tgz.addfile(tarinfo, fileobj=file)
		sys.stderr.write("\t%d byte(s)\n" % tarinfo.size)

		file.close()

	tgz.close()


