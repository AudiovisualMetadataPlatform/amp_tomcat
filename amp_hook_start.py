#!/bin/env python3
# The start hook doesn't take any arguments (except possibly the --debug flag)
# but it is passed the AMP_ROOT and AMP_DATA_ROOT environment variables

import argparse
import os
from amp.config import load_amp_config
from amp.logging import setup_logging
import logging
import subprocess
from pathlib import Path
from datetime import datetime

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", default=False, action="store_true", help="Turn on debugging")
    args = parser.parse_args()

    setup_logging(None, args.debug)

    # Roll catalina.out
    amp_root = os.environ['AMP_ROOT']
    old_catalina = Path(amp_root, "tomcat/logs/catalina.out")    
    new_catalina = Path(amp_root, f"tomcat/logs/catalina.out-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
    if old_catalina.exists():
        logging.info(f"Rolling catalina.log {old_catalina!s} -> {new_catalina!s}")
        old_catalina.rename(new_catalina)

    try:
        subprocess.run([f"{os.environ['AMP_ROOT']}/tomcat/bin/startup.sh"], check=True)
    except Exception as e:
        logging.error(f"Cannot start tomcat: {e}")


if __name__ == "__main__":
    main()



