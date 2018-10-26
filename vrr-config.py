#!/usr/bin/env python

SSH_CONFIG="/etc/ssh/ssh_config"
HOSTS=["vrr1", "vrr2", "vrr3", "vrr4", "vrr5", "vrr6", "vrr7", "vrr8"];
#HOSTS=["vrr1"];

from jnpr.junos import Device
import sys
from string import Template

# Default on error handler. Just print the exception message and exit
# Stack traces not necessary here
def onError(exception_type, exception, traceback):
    print "%s: %s" % (exception_type.__name__, exception)
#sys.excepthook = onError

if len(sys.argv)<2:
	sys.stderr.write("Usage: %s filename [host1 host2 host3 ...]\n" % sys.argv[0])
	sys.stderr.write("       filename: should be in set/delete format)\n")
	sys.stderr.write("       hosts are optional; defaults to %s\n\n" % " ".join(HOSTS))
	sys.stderr.write("Some magic expansions for the source file:\n\t$host - the current hostname, eg. vrr1,\n")
	sys.stderr.write("\t$id - numeric extract from the hostname, eg. 1\n")
	sys.exit(1)
else:
	filename = sys.argv[1]

if len(sys.argv)>2:
	HOSTS=sys.argv[2:]

template = Template(open(filename, 'r').read())

for host in HOSTS:

	index = filter(str.isdigit, host)

	sys.stderr.write("\twriting configuraton to %s... " % host)
	config = template.substitute(id=index, host=host)

        device = Device(host=host, user="user", ssh_config=SSH_CONFIG, port=22)
        device.open()

        sys.stderr.write("loading... ") 
	device.rpc.open_configuration(private=True, ignore_warning=True)
	device.rpc.load_config(config, ignore_warning=True, action="set", format="text")

        sys.stderr.write("committing... ") 
	device.rpc.commit()
	sys.stderr.write("OK") 

        device.timeout=2
        try:
            device.close()
        except:
	    sys.stderr.write("!") 
            pass

        sys.stderr.write("\n")

