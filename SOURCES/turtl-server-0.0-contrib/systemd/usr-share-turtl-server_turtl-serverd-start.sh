#!/usr/bin/bash 
# This should not be called by the user, but by systemd
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <main application directory path> <log file path>" >&2
  echo "BUT! This should be only run by systemd. I.e. systemctl start turtl-serverd.service"
  return 1;
fi
echo "========= Starting Turtl Server ===========" > $2 2>&1
cd $1
node server.js > $2 2>&1 &
