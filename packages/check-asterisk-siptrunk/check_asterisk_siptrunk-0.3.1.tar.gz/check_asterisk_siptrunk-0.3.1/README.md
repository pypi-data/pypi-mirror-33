# check_asterisk_siptrunk

Nagios plugin to check status of a SIP Peer via the Asterisk Management Interface (AMI).


## Usage

```
usage: check_asterisk_siptrunk.py [-h] [-v] [-H HOST] [-P PORT]
                                  user password peer

positional arguments:
  user                  Username for AMI
  password              Password for AMI
  peer                  Name of the SIP peer to check

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         increase output verbosity (use up to 3 times)
  -H HOST, --host HOST  IP Address for AMI
  -P PORT, --port PORT  Port for AMI

```

## Requirements

- pyst2 (https://github.com/rdegges/pyst2)
- nagiosplugin (https://bitbucket.org/flyingcircus/nagiosplugin)

## Acknowlegments

This plugin borrows a lot (not least the name) from a similar perl plugin https://github.com/dlintott/check_asterisk_siptrunk
