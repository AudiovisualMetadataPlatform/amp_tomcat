#!/bin/env python3
from re import L
from amp.logging import setup_logging
import argparse
import logging
from pathlib import Path
import urllib
import urllib.request
import tarfile
import shutil
import os

# We need to use one of the 9.x since 10.x changed the package names for the EE
# stuff and it breaks code
tomcat_download_url_base = "https://archive.apache.org/dist/tomcat/tomcat-9/"
tomcat_download_version = "9.0.65"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', default=False, action='store_true', help="Enable debugging")
    parser.add_argument('install_path', help="Where the package will be installed")
    args = parser.parse_args()

    setup_logging(None, args.debug)

    amp_root = Path(os.environ['AMP_ROOT'])

    if (amp_root / "tomcat/webapps").exists():
        logging.warning("Skipping tomcat download: Tomcat package may already be installed.")
        exit(0)
        
    # Install a tomcat.  Specifically we're going with tomcat 9.0.x
    # which is the latest as of this release.  Tomcat 10 changes the
    # servlet namespace and is incompatible with what we're running
    logging.info(f"Installing tomcat {tomcat_download_version} as {amp_root / 'tomcat'!s}")
    tomcat_url = f"{tomcat_download_url_base}/v{tomcat_download_version}/bin/apache-tomcat-{tomcat_download_version}.tar.gz"    
    u = urllib.request.urlopen(tomcat_url)
    with tarfile.open(fileobj=u, mode="r|gz") as t:
        t.extractall(amp_root)
    (amp_root / f"apache-tomcat-{tomcat_download_version}").rename(amp_root / "tomcat")
    shutil.rmtree(amp_root / 'tomcat/webapps')
    (amp_root / 'tomcat/webapps').mkdir()



if __name__ == "__main__":
    main()