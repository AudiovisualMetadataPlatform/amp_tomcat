#!/bin/env python3
# This script will be run when the AMP system is reconfigured.  It will
# write the configuration files that amppd needs, driven by the amp
# configuration file.
#
# No arguments, but the AMP_ROOT and AMP_DATA_ROOT environment variables
# will be set by the caller so it can find all things AMP.

import argparse
import logging
from pathlib import Path
import os
import yaml
import subprocess
from amp.config import load_amp_config
from amp.logging import setup_logging

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', default=False, action='store_true', help="Turn on debugging")    
    args = parser.parse_args()

    # set up the standard logging
    setup_logging(None, args.debug)

    # grab the configuration file
    config = load_amp_config()

    # set amp_root
    amp_root = Path(os.environ['AMP_ROOT'])

    tomcat_port = config['amp']['port']
    tomcat_shutdown_port = str(int(tomcat_port) + 1)

    if config['amp'].get('https', False):        
        proxy_data = f'proxyName="{config["amp"]["host"]}" proxyPort="443" secure="true" scheme="https"'
    else:
        proxy_data = ""

    # Main tomcat configuration file
    with open(amp_root / "tomcat/conf/server.xml", "w") as f:
        f.write(f"""<?xml version="1.0" encoding="UTF-8"?>
<Server port="{tomcat_shutdown_port}" shutdown="SHUTDOWN">
  <Listener className="org.apache.catalina.startup.VersionLoggerListener" />
  <Listener className="org.apache.catalina.core.AprLifecycleListener" SSLEngine="on" />
  <Listener className="org.apache.catalina.core.JreMemoryLeakPreventionListener" />
  <Listener className="org.apache.catalina.mbeans.GlobalResourcesLifecycleListener" />
  <Listener className="org.apache.catalina.core.ThreadLocalLeakPreventionListener" />
  <GlobalNamingResources>
    <Resource name="UserDatabase" auth="Container"
              type="org.apache.catalina.UserDatabase"
              description="User database that can be updated and saved"
              factory="org.apache.catalina.users.MemoryUserDatabaseFactory"
              pathname="conf/tomcat-users.xml" />
  </GlobalNamingResources>
  <Service name="Catalina">
    <Connector port="{tomcat_port}" protocol="HTTP/1.1"
               connectionTimeout="20000"
               redirectPort="8443" {proxy_data}/>
    <Engine name="Catalina" defaultHost="localhost">
      <Realm className="org.apache.catalina.realm.LockOutRealm">
        <Realm className="org.apache.catalina.realm.UserDatabaseRealm"
               resourceName="UserDatabase"/>
      </Realm>
      <Host name="localhost"  appBase="webapps"
            unpackWARs="true" autoDeploy="true">
        <Valve className="org.apache.catalina.valves.AccessLogValve" directory="logs"
               prefix="localhost_access_log" suffix=".txt"
               pattern="%h %l %u %t &quot;%r&quot; %s %b" />
      </Host>
    </Engine>
  </Service>
</Server>\n""")

    # allow ROOT webapp to access symlinks
    (amp_root / "tomcat/conf/Catalina/localhost").mkdir(parents=True, exist_ok=True)
    with open(amp_root / "tomcat/conf/Catalina/localhost/ROOT.xml", "w") as f:
        f.write(f"""<Context>
   <Resources allowLinking="true">
    <PreResources className="org.apache.catalina.webresources.DirResourceSet" webAppMount="/symlinks" base="{amp_root / 'data/symlinks'!s}"/>
  </Resources>
</Context>\n""")




if __name__ == "__main__":
    main()