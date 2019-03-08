#!/usr/bin/bash
# This is called by backup-turtl-server.sh
# Do not use directly.

if [ "$#" -ne "2" ]; then
  echo "Turtl Server backup helper script"
  echo "This should not be called by a human"
  echo "Usage: $0 <IP_or_DomainName> <Nginx? 1 or 0>" >&2
  exit 1;
fi
DOMAIN=$1
NGINX_ENABLED=$2
DATE_F=$(date +%F)

ARCHIVEBASENAME=backup-$DOMAIN-$DATE_F
CHOWNTO=$SUDO_USER

echo "## Backing up our Turtl Server!"

echo "#### Shutting down services..."
if [ "$NGINX_ENABLED" -eq "1" ] ; then
systemctl stop nginx.service
fi
systemctl stop turtl-serverd.service
systemctl stop postgresql.service
sleep 5

mkdir -p $ARCHIVEBASENAME
cd $ARCHIVEBASENAME

if [ "$NGINX_ENABLED" -eq "1" ] ; then
echo "#### Copying files (nginx)..."
mkdir -p ./etc/ssl
cp -a /etc/ssl/dhparam.pem ./etc/ssl/
mkdir -p ./etc/nginx/conf.d
cp -a /etc/nginx/conf.d/* ./etc/nginx/conf.d/
mkdir -p ./etc/sysconfig
cp -a /etc/sysconfig/turtl-serverd ./etc/sysconfig/
mkdir ./root
cp -a /root/.acme.sh ./root/DOTacme.sh
fi

echo "#### Copying files (postgresql)..."
mkdir -p ./var/lib
cp -a /var/lib/pgsql ./var/lib/
echo "#### Copying files (turtl-server)..."
cp -a /var/lib/turtl-server ./var/lib/

systemctl start turtl-serverd.service
systemctl start postgresql.service
if [ "$NGINX_ENABLED" -eq "1" ] ; then
systemctl start nginx.service
fi

cd ..

echo "#### Creating archive (tarball)..."
tar -czf $ARCHIVEBASENAME.tar.gz $ARCHIVEBASENAME
rm -rf $ARCHIVEBASENAME
chown $CHOWNTO:$CHOWNTO $ARCHIVEBASENAME.tar.gz
#mv -v $ARCHIVEBASENAME.tar.gz /home/$CHOWNTO/
#ls -lh /home/$CHOWNTO/$ARCHIVEBASENAME.tar.gz
ls -lh $ARCHIVEBASENAME.tar.gz
echo "## Done gathering data"
