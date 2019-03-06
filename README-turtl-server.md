# Install and host a Turtl Server

> Assumption: A modest competence at basic linux systems administration.
>
> Dummy values used in this document: **turtl.example.com** and
> **198.51.100.35**, examples representing user configured hostname and IP
> address

A Turtl Server most powerfully sits on a hosted platform and serves as your
personal, private, end-to-end encrypted repository of
[markdown](https://commonmark.org/)-formatted notes, thoughts, grand ideas, and
missives... all synchronized between your devices. And if you like, the devices
of your friends, family, and team-members.

Installation and configuration is a bit more complicated than "TL;DR", but I
will do my best to summarize.

Note: Special thanks have to go out to Jeremy Schroeder for the general
structure of these instructions.
[Here's](https://spudz.org/2019/02/24/how-to-setup-a-private-turtl-server/) his
howto. I took what he wrote, expanded upon it, and adjusted the configuration to
accommodate managing everything with natively constructed RPM packages. It would
have taken me forever to figure out how to implement this without his fine
document.

**Table of Contents**
<!-- TOC -->

- [Install and host a Turtl Server](#install-and-host-a-turtl-server)
  - [[1] Set up and configured a minimal headless VPS](#1-set-up-and-configured-a-minimal-headless-vps)
  - [[2] Install the software...](#2-install-the-software)
  - [[3] Enable and start the Postgresql DB](#3-enable-and-start-the-postgresql-db)
  - [[4] Configure a Postgresql user and database instance specifically for the Turtl Server application](#4-configure-a-postgresql-user-and-database-instance-specifically-for-the-turtl-server-application)
    - [Test that the PostgreSQL server is running in the general sense.](#test-that-the-postgresql-server-is-running-in-the-general-sense)
    - [Create a PostgreSQL user and database for Turtl](#create-a-postgresql-user-and-database-for-turtl)
    - [Update the database password for the turtl user](#update-the-database-password-for-the-turtl-user)
    - [Edit PostgreSQL's connection permission configuration file](#edit-postgresqls-connection-permission-configuration-file)
    - [Restart the PostgreSQL systemd service and test the connection...](#restart-the-postgresql-systemd-service-and-test-the-connection)
  - [[5] Configure your Turtl Server](#5-configure-your-turtl-server)
    - [Edit the Turtl configuration file](#edit-the-turtl-configuration-file)
    - [Initialize the database structure](#initialize-the-database-structure)
  - [[6] Setup and configure the Nginx webserver](#6-setup-and-configure-the-nginx-webserver)
    - [Boost Nginx's `types_hash_max_size` from `2048` to `4096`](#boost-nginxs-types_hash_max_size-from-2048-to-4096)
    - [Firewall: Poke a hole to the outside world for ports 80 (http) and 443 (https)](#firewall-poke-a-hole-to-the-outside-world-for-ports-80-http-and-443-https)
    - [Start nginx.service](#start-nginxservice)
    - [Setup your domain and point DNS to your VPS](#setup-your-domain-and-point-dns-to-your-vps)
    - [Generate (issue) a TLS certicate from Let's Encrypt for this service](#generate-issue-a-tls-certicate-from-lets-encrypt-for-this-service)
  - [[7] Configure Nginx to service Turtl Server](#7-configure-nginx-to-service-turtl-server)
- [Doing this as root](#doing-this-as-root)

<!-- /TOC -->


There are four components to a Turtl Server.
1. A VPS or physical Fedora Linux server.
2. The Turtl Server application itself
3. A database. Specifically PostgreSQL
4. A webserver. In this example, Nginx.

## [1] Set up and configured a minimal headless VPS

Instruction for how to deploy and manage a general purpose minimal server for all kinds of workloads can be found here: <https://github.com/taw00/howto/blob/master/howto-deploy-and-configure-a-minimalistic-fedora-linux-server.md>

## [2] Install the software...

```
# Initial install...
sudo dnf copr enable taw/turtl
sudo dnf install turtl-server nginx
```

```
# Update/upgrade...
sudo dnf upgrade turtl-desktop
```

## [3] Enable and start the Postgresql DB
Note: Really good information: <https://fedoraproject.org/wiki/PostgreSQL>

```
sudo systemctl enable postgresql
sudo systemctl start postgresql
```

If the start failed, you have to initialize the database...

```
sudo postgresql-setup --initdb --unit postgresql
sudo systemctl start postgresql
```

The PostgreSQL log files can be found here: `/var/lib/pgsql/log/*.log`
```
sudo tail -f /var/lib/pgsql/data/log/*.log
```

## [4] Configure a Postgresql user and database instance specifically for the Turtl Server application

The `turtl-server` RPM installation already created a `turtl` system user. But
you need a user that can access and admin the Turtl Server's database instance
as well.

#### Test that the PostgreSQL server is running in the general sense.

```
# Open the PostgreSQL interactive terminal as the default 'postgres' user
sudo -i -u postgres psql
```
```
# Did that run okay? Good. CTRL-D and get back to the commandline.
```

#### Create a PostgreSQL user and database for Turtl

```
# The database is named turtl and user is named turtl
sudo -i -u postgres createuser turtl
sudo -i -u postgres createdb --owner=turtl turtl
```

#### Update the database password for the turtl user  

Keep it to letters and numbers for ease of configuration later.

```
sudo -i -u turtl psql
# use the \password command to change the password for database user turtl
```

```
# CTRL-D to log out
```

#### Edit PostgreSQL's connection permission configuration file
Edit `/var/lib/pgsql/data/pg_hba.conf` and change the `127.0.0.1/32`
line from `ident` to `trust`. Make it look like this...
```
host    all             all             127.0.0.1/32            trust
```

#### Restart the PostgreSQL systemd service and test the connection...
```
sudo systemctl restart postgresql
```

Test the database direct login credentials...
```
psql -d turtl -U turtl -W
```

## [5] Configure your Turtl Server

#### Edit the Turtl configuration file
File `/usr/share/turtl-server/config/config.yaml`  
Update the DB connection and other things local to you [emails, domain,
upload directory, etc].

The database connection string:
```
# This is the format: dbusername:dbpassword@127.0.0.1:5432/database_instance
connstr: 'postgres://turtl:TURTL_DATABASE_PASSWORD@127.0.0.1:5432/turtl'
```

#### Initialize the database structure

```
# Init the DB structure
sudo -i -u turtl
cd /usr/share/turtl-server
./scripts/init-db.sh

# Test and fix the things you messed up
# If it works... you are running!
sudo -i -u turtl
cd /usr/share/turtl-server
node server.js
```

```
CTRL-C to shut down again
```

## [6] Setup and configure the Nginx webserver

Helpful: <https://fedoraproject.org/wiki/Nginx>

#### Boost Nginx's `types_hash_max_size` from `2048` to `4096`

This has nothing to do with anything except that Nginx will forever log a
warning that the types_hash_max_size is too small. This is changed directly in
the `/etc/nginx/nginx.conf` configuration file.

#### Firewall: Poke a hole to the outside world for ports 80 (http) and 443 (https)

```
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-rich-rule='rule service name=http accept limit value=10/s'
sudo firewall-cmd --permanent --add-rich-rule='rule service name=https accept limit value=10/s'
sudo firewall-cmd --reload
sudo firewall-cmd --list-all
```

#### Start nginx.service

```
sudo systemctl start nginx
```

Now use your browser and browse to the IP address of your server. **You should
see the default Nginx welcome or test page.** If not, something is wrong and you
need to troubleshoot (beyond the scope of this document), by examining the Nginx
log files: `sudo tail -f /var/log/nginx/*.log`

#### Setup your domain and point DNS to your VPS

Purchase a domain name from someone like GoDaddy or Gandi. Let's say we were
able to purchase `example.com`. Maybe `example.com` is my general website and
directs to some other server. For my Turtl Server, I decided to create a
sub-domain `turtl.example.com` and point that at this server. To do that all I
need to do is add an "A" record in my domain provider's DNS Record configuration
for the `example.com` domain. It would look something like this (IP address is
completely made up, of course)...

```
turtl			A			1800			198.51.100.35
```

Now use your browser and browse to the web address (http://turtl.example.com) of
your server. **You should see the default Nginx welcome or test page.** If not,
something is wrong and you need to troubleshoot (beyond the scope of this
document), by examining the Nginx log files: `sudo tail -f /var/log/nginx/*.log`

#### Generate (issue) a TLS certicate from Let's Encrypt for this service

We use the fine acme.sh utility from Neil Pang to issue ourselves a TLS
certificate from Let's Encrypt.

Reference: <https://en.wikipedia.org/wiki/Let's_Encrypt> and <https://github.com/Neilpang/acme.sh>

Let's Encrypt requires you to prove you have control of the domain you want to
use. The acme.sh utility leverages a mini webserver so that we don't have to
configure nginx in unnatural ways to enable this just yet. We already directed
our domain to our IP address, so we just need to shut down nginx and let acme.sh
do it's thing in "standalone" mode.

Shut down nginx
```
sudo systemctl stop nginx
```

Install the `socat` RPM (mini-webserver)
```
sudo dnf install socat -y
```

Install acme.sh (recommended you do this as root and a fully logged in)
```
sudo su -
# This will...
# - create a ~/.acme.sh/ directory and copy the acme.sh script into it
# - edit root's ~/.bashrc file and create an alias acme.sh=~/.acme.sh/acme.sh
# - set up a cronjob to run daily to check and renew the certs if need be
curl https://get.acme.sh | sh
```
```
# CTRL-D to log out of root...
# ...and then log back in again
sudo su -
```

Issue your TLS certificate (using our turtl.example.com example)
```
# This will populate ~/.acme.sh/turtl.example.com/ with certs and keys and such
acme.sh --issue --standalone -d turtl.example.com
```

Install your cert and key to an appropriate directory to be used by Nginx
```
# We're still root...
DOMAIN=turtl.example.com
mkdir -p /etc/nginx/ssl/$DOMAIN

acme.sh --install-cert -d $DOMAIN \
--fullchain-file /etc/nginx/ssl/$DOMAIN/$DOMAIN.cert.pem \
--key-file       /etc/nginx/ssl/$DOMAIN/$DOMAIN.key.pem  \
--reloadcmd     "systemctl force-reload nginx"
```

Populate openssl dhparams to /etc/ssl...
```
# We're still root...
openssl dhparam -out /etc/ssl/dhparam.pem 4096
```


## [7] Configure Nginx to service Turtl Server

All Nginx configuration resides in `/etc/nginx/nginx.conf` and
`/etc/nginx/conf.d/`. Other than the `types_hash_max_size` (see above), you will
not be changing the configuration of ``/etc/nginx/nginx.conf`.

#### Create a new file in the `nginx/conf.d` drop directory

Let's call it `turtl.example.com.conf` for this example.

The configuration should look something like this (edit as makes sense):
```
upstream turtl {
  server 127.0.0.1:8181;
}

server {
    listen 80 ;
    listen [::]:80 ;
    server_name turtl.example.com;
    # Comment out the next line if you wish non-secure port 80 to be available
    # for use by the Turtl remote clients.
    return 302 https://$server_name$request_uri;
    location / {
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header Host $http_host;
      proxy_set_header X-NginX-Proxy true;
      proxy_pass http://turtl;
      proxy_redirect off;
    }
}

server {
    listen 443 ssl http2  ;
    listen [::]:443 ssl http2  ;

    # SSL requires extra configuration!
    server_name turtl.example.com;

    ### SSL Stuff
    ## troubleshoot with: openssl s_client -debug -connect turtl.example.com:443
    ssl_certificate /etc/nginx/ssl/turtl.example.com/turtl.example.com.cert.pem;
    ssl_certificate_key /etc/nginx/ssl/turtl.example.com/turtl.example.com.key.pem;

    # openssl dhparam -out /etc/ssl/dhparam.pem 4096
    ssl_dhparam /etc/ssl/dhparam.pem;

    ssl_protocols TLSv1.2 TLSv1.1;
    ssl_prefer_server_ciphers on;
    ssl_ciphers AES256+EECDH:AES256+EDH:!aNULL;

    ssl_session_cache shared:TLS:2m;

    # OCSP stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 1.1.1.1;

    # Set HSTS to 365 days
    add_header Strict-Transport-Security 'max-age=31536000; includeSubDomains';

    location / {
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header Host $http_host;
      proxy_set_header X-NginX-Proxy true;
      proxy_pass http://turtl;
      proxy_redirect off;
    }
}
```

#### Test nginx, start, and enable nginx.service
```
nginx -t
sudo systemctl start nginx
sudo systemctl enable nginx
```

NOTE: If you want to test the functionality without the added complexity of
troubleshooting SSL/TLS on top of that, edit the configuration file above and
comment out the line starting with "return 302". You should be able to then use
`http://turtl.example.com` as your Turtl desktop (or mobile sync setting).

## [8] Start and enable the Turtl Server and browse to your domain

This time, we are using systemd for the Turtl server management

```
sudo systemctl enable turtl-serverd.service
sudo systemctl start turtl-serverd.service
```

Use a web-browser and browse to your domain...

Instead of an Nginx default test page you should see rudimentary webpage and a message that says 'Greeting: "Hi."'

If this does not work, troubleshoot by looking at ....

```
sudo tail -f /var/log/turtl-server/turtl-server.log
sudo tail -f /var/log/nginx/error.log
sudo journalctl -xe
```

## [9] Configure a Turtl client to sync to your server

Install a Turtl desktop application (like, for example, the one provided by this packager called 'turtl-desktop'). Or the Turtl mobile application (Android and probably iOS).

When you first open the application, click on "Create account". Enter an email
and password, but then click on "Advanced settings" and change the "Turtl
server" setting to your domain: `http://turtl.example.com` if you didn't set up
TLS yet and make the config file changes I mentioned above, or
`https://turtl.example.com`.

The application should sync right up and ... you can now securely annotate your life! ;)

## Comments? Suggestions?
Open an issue here, or send me a note via Keybase -- https://keybase.io/toddwarner

---

## Addendum - Backing up your Turtl Server

This could be, of course, automated.

```
# Doing this as root
sudo su -

DATE_F=$(date +%F)
DOMAIN=turtl.example.com
ARCHIVEBASENAME=backup-$DOMAIN-$DATE_F
CHOWNTO=todd

echo "## Backing up our Turtl Server!"
echo "#### Shutting down services..."
systemctl stop turtl-serverd.service
systemctl stop nginx.service
systemctl stop postgresql.service
sleep 5

echo "#### Copying files..."
mkdir -p $ARCHIVEBASENAME
cd $ARCHIVEBASENAME
mkdir -p ./etc/ssl
cp -a /etc/ssl/dhparam.pem ./etc/ssl/
mkdir -p ./etc/nginx/conf.d
cp -a /etc/nginx/conf.d/* ./etc/nginx/conf.d/$DOMAIN
mkdir -p ./etc/sysconfig
cp -a /etc/sysconfig/turtl-serverd ./etc/sysconfig/
mkdir ./root
cp -a /root/.acme.sh ./root/DOTacme.sh
mkdir -p ./var/lib
cp -a /var/lib/pgsql ./var/lib/
cp -a /var/lib/turtl-server ./var/lib/
cd ..
systemctl start turtl-serverd.service
systemctl start nginx.service
systemctl start postgresql.service

echo "#### Creating archive (tarball)..."
tar -czf $ARCHIVEBASENAME.tar.gz $ARCHIVEBASENAME
chown $CHOWNTO:$CHOWNTO $ARCHIVEBASENAME.tar.gz
mv -v $ARCHIVEBASENAME.tar.gz /home/$CHOWNTO/
ls -lh /home/$CHOWNTO/$ARCHIVEBASENAME.tar.gz
echo ## DONE!
```
