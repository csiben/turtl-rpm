#!/usr/bin/bash
# Download this, and it's helper script to your desktop and then run it.
# Usage example:
#   ./backup-turtl-server.sh myturtlserver turtl.example.com 1
#
# This will plop a backup script on a remote system, gather up important
# files, retrieve all that stuff, and then cleanup after itself
# Very ansible-like. Probably should just use ansible.
if [ "$#" -ne "3" ]; then
  echo "Turtl Server Backup"
  echo "Usage: $0 <ssh_host_alias> <IP_or_DomainName> <Nginx? 1 or 0>" >&2
  exit 1;
fi
SSH_TARGET=$1
DOMAIN=$2
NGINX_ENABLED=$3

rsync -az ./backup-turtl-server.remote-helper.sh $SSH_TARGET:
ssh $SSH_TARGET "sudo ./backup-turtl-server.remote-helper.sh $DOMAIN $NGINX_ENABLED"
echo "## Retrieving backup archive"
rsync -az $SSH_TARGET:backup-$DOMAIN*.tar.gz ./
echo "## Cleanup"
ssh $SSH_TARGET 'rm ./backup-turtl-server.remote-helper.sh backup-$DOMAIN*.tar.gz'
echo "## The archive(s)..."
ls -lh ./backup-$DOMAIN*.tar.gz
echo "## Backup of Turtl Server is complete"

