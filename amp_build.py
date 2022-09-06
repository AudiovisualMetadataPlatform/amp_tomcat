#!/bin/env python3

from amp.package import *
import argparse
import logging
from pathlib import Path
import subprocess
import sys
import tempfile
import shutil
import amp_hook_pre

def main():
    parser = argparse.ArgumentParser()    
    parser.add_argument("--debug", default=False, action="store_true", help="Turn on debugging")    
    parser.add_argument("--package", default=False, action="store_true", help="Build package instead of install")
    parser.add_argument("destination", help="Destination for build (should be an AMP_ROOT for non-package)")
    args = parser.parse_args()
    logging.basicConfig(format="%(asctime)s [%(levelname)-8s] (%(filename)s:%(lineno)d)  %(message)s",
                        level=logging.DEBUG if args.debug else logging.INFO)

    # Build the software
    # this is a metapackage with no payload, just hook scripts
    pass

    # Install the software
    # Nothing to install except lifecycle scripts, so this has to be installed
    # via a package.
    if not args.package:
        logging.error("Metapackages need to be installed via package")
        exit(1)

    try:
        new_package = create_package("tomcat", amp_hook_pre.tomcat_download_version, "tomcat",
                                     Path(args.destination), None,
                                     hooks={'pre': 'amp_hook_pre.py',                                             
                                            'config': 'amp_hook_config.py',
                                            'start': 'amp_hook_start.py',
                                            'stop': 'amp_hook_stop.py'})

        logging.info(f"New package in {new_package}")    
    except Exception as e:
        logging.error(f"Failed to build backage: {e}")
        exit(1)


if __name__ == "__main__":
    main()