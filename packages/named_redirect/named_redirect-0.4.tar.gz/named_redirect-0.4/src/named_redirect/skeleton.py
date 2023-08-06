#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is a skeleton file that can serve as a starting point for a Python
console script. To run this script uncomment the following line in the
entry_points section in setup.py:

    [console_scripts]
    fibonacci = named_redirect.skeleton:run

Then run `python setup.py install` which will install the command `fibonacci`
inside your current environment.
Besides console scripts, the header (i.e. until _logger...) of this file can
also be used as template for Python modules.

Note: This skeleton file can be safely removed if not needed!
"""
from __future__ import division, print_function, absolute_import

import argparse
import sys
import logging
#import urllib.request
import os

from named_redirect import __version__

__author__ = "Anish Mangal"
__copyright__ = "Anish Mangal"
__license__ = "gpl3"

_logger = logging.getLogger(__name__)


def check_internet():
    """Check for internet connectivity
   
    Args:

    Returns:
      bool: Whether connected to the internet or not
    """
    _logger.debug("Checking for internet connectivity")
    try:
        #urllib.request.urlopen('http://216.58.192.142', timeout=5)
        return os.system("ping -c 1 8.8.8.8")
    except OSError as err: 
        _logger.debug("Internet connectivity absent!")
        return False


def restart_bind9():
    """Restart bind9 named service
   
    Returns:
      bool: Whether operation was successful or not
    """
    _logger.debug("Restarting the named/bind9 systemd service")
    try:
        os.system("sudo systemctl restart bind9.service")
    except OSError as err:
        _logger.error("Could not restart bind9")
        return False
    
    _logger.debug("Restarted bind9 service")
    return True
        
def reconfigure_bind9(dns_jail=False):
    """Reconfigure bind9 to serve as a DNS jail or not depending on argument provided. 
   
    Args:
      dns_jail: Whether to reconfigure as a dns jail or not

    Returns:
      bool: Whether operation was successful or not
    """
    _logger.debug("Reconfiguring named/bind9")
    dns_jail_zone_file=""
    dns_jail_zone_file_destination="/var/named-iiab/named.blackhole"
    bind9_conf_file=""
    bind9_conf_file_destination="/etc/named-iiab.conf"
    
    try:
        if check_internet() or not dns_jail:
            _logger.info("We have internet, so dns_jail is not required")
            dns_jail_zone_file = "/var/named-iiab/named.blackhole.empty"
            bind9_conf_file = "/etc/named-iiab.conf.nojail"
        else:
            _logger.info("We do not have internet, so dns_jail is required")
            dns_jail_zone_file = "/var/named-iiab/named.blackhole.dnsjail"
            bind9_conf_file = "/etc/named-iiab.conf.jail"
    except:
        _logger.error("Could not reconfigure bind9")
        return False

    try:
        os.system("sudo cp %(source)s %(destination)s" % {'source': dns_jail_zone_file, "destination": dns_jail_zone_file_destination})
        os.system("sudo cp %(source)s %(destination)s" % {'source': bind9_conf_file, "destination": bind9_conf_file_destination})
        _logger.info("Copied new configuration and zone files")
    except OSError as err:
        _logger.error("Could not copy configuration and zone files")
        return False

    return restart_bind9()

def parse_args(args):
    """Parse command line parameters

    Args:
      args ([str]): command line parameters as list of strings

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(
        description="Check for internet and reconfigure and restart bind9 accordingly")
    parser.add_argument(
        '--version',
        action='version',
        version='named_redirect {ver}'.format(ver=__version__))
    parser.add_argument(
        '-j',
        '--jail',
        dest="dns_jail",
        help="1 for enabling dns jail, 0 for disabling dns jail",
        type=int,
        metavar="INT")
    parser.add_argument(
        '-v',
        '--verbose',
        dest="loglevel",
        help="set loglevel to INFO",
        action='store_const',
        const=logging.INFO)
    parser.add_argument(
        '-vv',
        '--very-verbose',
        dest="loglevel",
        help="set loglevel to DEBUG",
        action='store_const',
        const=logging.DEBUG)
    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(level=loglevel, stream=sys.stdout,
                        format=logformat, datefmt="%Y-%m-%d %H:%M:%S")


def main(args):
    """Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list
    """
    args = parse_args(args)
    setup_logging(args.loglevel)
    _logger.info("Reconfiguring DNS for this machine")
    reconfigure_bind9(args.dns_jail)
    _logger.info("Script ends here")


def run():
    """Entry point for console_scripts
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
