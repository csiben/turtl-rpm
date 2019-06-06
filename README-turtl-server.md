# Install and Host a Turtl Server

Turtl Server is a self-hostable communication and sychronization hub enabling
users to synchronize their Turtl client data across all of their devices and
collaborate with other users on the network. As part of the sychronization
process, a Turtl Server also serves as a secure backup of user content. All
data is secured with end-to-end encryption.

By default, the Turtl Server that your clients are configured to leverage is
the Turtl Server provided by the Turtl development team. The Turtl Server
application provided here enables an admin to bring the secure Turtl ecosystem
inhouse and in their full control.

> Assumptions:
> * A modest degree of competence at basic linux systems administration.
> * A dedicated domainname to use for this service. For the purposes of this
>   document, our example top-level domain is `example.com` and our dedicated
>   subdomain for this service is `turtl`, and therefore the full domain is
>   `turtl.example.com`. Also, for documentation purposes, we are using this
>   dummy IP address `198.51.100.35`.

_Note: Special thanks have to go out to Jeremy Schroeder for the general
structure of these instructions.
[Here's](https://spudz.org/2019/02/24/how-to-setup-a-private-turtl-server/) his
howto. I took what he wrote, expanded upon it, and adjusted the configuration
to accommodate managing everything with natively constructed RPM packages. It
would have taken me forever to figure out how to implement this without his
fine document._

**Table of Contents**
<!-- TOC -->
  - [[1] Set up and configure a headless VPS](#1-set-up-and-configured-a-minimal-headless-vps)
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
    - [Firewall: Poke a hole to the outside world for ports 80 (http) and 443 (https)](#firewall-poke-a-hole-to-the-outside-world-for-ports-80-http-and-443-https)
    - [and maybe port 8181 (turtl-server direct)](#and-maybe-port-8181-turtl-server-direct)
    - [Start nginx.service](#start-nginxservice)
    - [Setup your domain and point DNS to your VPS](#setup-your-domain-and-point-dns-to-your-vps)
    - [Generate (issue) a TLS certicate from Let's Encrypt for this service](#generate-issue-a-tls-certicate-from-lets-encrypt-for-this-service)
  - [[7] Configure Nginx to service Turtl Server](#7-configure-nginx-to-service-turtl-server)
<!-- /TOC -->

There are four components to a Turtl Server.
1. A VPS or physical Fedora Linux server.
2. The Turtl Server application itself
3. A database. Specifically PostgreSQL
4. A webserver. In this example, Nginx.

## [1] Set up and configure a headless VPS

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

The *crucial* configuration settings to enter correctly are the database
connection string (connstr) and the API URL (api\_url).

Other critical settings are "host", "port", and "local" (uploads directory).
But these can remain the default.

***Update the database connection string:***

```
# This is the format: dbusername:dbpassword@127.0.0.1:5432/database_instance
connstr: 'postgres://turtl:TURTL_DATABASE_PASSWORD@127.0.0.1:5432/turtl'
```

***Update the `api_url` setting:***

Since we are going to fetch and set an SSL certificate later, let's set this to
"https://turtl.example.com". If you were not going to configure this Turtl
Server to use SSL, then change that to http.

***Change the `secure_hash_salt` setting:***
Write out a long random diatribe. This is used to kickstart some of the
cryptography that Turtl employs.

Go ahead and set the www URL and emails addresses as you see fit.

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

#### Firewall: Poke a hole to the outside world for ports 80 (http) and 443 (https)
####           and maybe port 8181 (turtl-server direct)

```
# If you want to have clients talk to the Turtl Server directly,
# vs. through the webserver...
#sudo firewall-cmd --permanent --add-service=turtl-server
#sudo firewall-cmd --permanent --add-rich-rule='rule service name=turtl-server accept limit value=10/s'
# If you changed the port of Turtl Server, and want to have clients connect
# to it directly, you can do something like this...
#sudo firewall-cmd --permanent --add-port=8188/tcp
#sudo firewall-cmd --permanent --add-rich-rule='rule family=ipv4 port port="8188" protocol=tcp limit value=10/s accept'
# But if you are funneling through the webserver, you only need those ports enabled...
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

We use the fine `acme.sh` utility from Neil Pang to issue ourselves a TLS
certificate from Let's Encrypt.

Reference: <https://en.wikipedia.org/wiki/Let's_Encrypt> and <https://github.com/Neilpang/acme.sh>

Let's Encrypt requires you to prove you have control of the domain you want to
use. The acme.sh utility leverages a mini webserver so that we don't have to
configure nginx in unnatural ways to enable this just yet. We already directed
our domain to our IP address, so we just need to shut down nginx and let acme.sh
do it's thing in "standalone" mode.

Log into root fully. Install `socat` and `acme.sh`.

```
# Login to root
sudo su -
```

```
# Install socat (mini-webserver) and the acme tools. Re-source root's '~/.bashrc' file
dnf install socat -y
curl https://get.acme.sh | sh
. ~/.bashrc
```

> Note that the acme installer will perform 3 actions:
>
> 1. Create and copy `acme.sh` to your home dir ($HOME): `~/.acme.sh/`  
>    All certs will be placed in this folder too.
> 2. Create alias for: `acme.sh=~/.acme.sh/acme.sh`
> 3. Create daily cron job to check and renew the certs if needed.

Set these temp environment variables to make things easier...
```
DOMAIN=example.com
SITE=turtl.${DOMAIN}
```

Issue your TLS certificate (using our turtl.example.com example).
```
# This will populate ~/.acme.sh/$SITE/ with certs and keys and such
# If your DNS is not set up, this will fail.
systemctl stop nginx
acme.sh --issue --standalone -d $SITE
systemctl start nginx
```

**Install your cert and key to an appropriate directory to be used by Nginx...**
```
# We're still root...
mkdir -p /etc/nginx/ssl/$DOMAIN

acme.sh --install-cert -d $SITE \
--fullchain-file /etc/nginx/ssl/$DOMAIN/$SITE.cert.pem \
--key-file       /etc/nginx/ssl/$DOMAIN/$SITE.key.pem  \
--reloadcmd     "systemctl force-reload nginx"
```

**Populate openssl dhparams to `/etc/ssl/`...**

```
# We're still root...
openssl dhparam -out /etc/ssl/dhparam.pem 4096
```

**Edit `crontab` entry to deal with `nginx` being in the way**

```
# We're still root
crontab -e
```
The entry will look something like this:
```
20 0 * * * "/root/.acme.sh"/acme.sh --cron --home "/root/.acme.sh" > /dev/null
```

_Note: This example sets the command to run every day at 12:20am._

But you want to make sure it looks more like this:
```
20 0 * * * { /usr/bin/systemctl stop nginx ; "/root/.acme.sh"/acme.sh --cron --home "/root/.acme.sh" ; /usr/bin/systemctl start nginx } >> /var/log/turtl-server/acme.log 2>&1
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
    listen 80;
    listen [::]:80;

    server_name turtl.example.com;
    types_hash_max_size 4096;

    # Comment out the next line if you wish non-secure port 80 to be available
    # for use by the Turtl remote clients.
    return 302 https://$server_name$request_uri;
    location / {
      proxy_set_header X-Real-IP $remote_addr;
      proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
      proxy_set_header Host $http_host;
      proxy_set_header X-NginX-Proxy true;
      # This is entirely experimental. Stream any content to the next server.
      proxy_request_buffering off;
      # arbitrarily large timeout and filesize support
      fastcgi_read_timeout 9999;
      client_max_body_size 9999M;
      proxy_pass http://turtl;
      proxy_redirect off;
    }
}

server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;

    server_name turtl.example.com;
    types_hash_max_size 4096;

    # SSL requires extra configuration

    ### SSL Stuff
    ## troubleshoot with: openssl s_client -debug -connect turtl.example.com:443
    ssl_certificate /etc/nginx/ssl/example.com/turtl.example.com.cert.pem;
    ssl_certificate_key /etc/nginx/ssl/example.com/turtl.example.com.key.pem;

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
      # This is entirely experimental. Stream any content to the next server.
      proxy_request_buffering off;
      # arbitrarily large timeout and filesize support
      fastcgi_read_timeout 9999;
      client_max_body_size 9999M;
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

Instead of an Nginx default test page you should see rudimentary webpage and a
message that says 'Greeting: "Hi."'

If this does not work, troubleshoot by looking at ....

```
sudo tail -f /var/log/turtl-server/turtl-server.log
sudo tail -f /var/log/nginx/error.log
sudo journalctl -xe
```

## [9] Configure a Turtl client to sync to your server

Install a Turtl desktop application (like, for example, the one provided by
this packager called 'turtl-desktop'). Or the Turtl mobile application (Android
and probably iOS).

When you first open the application, click on "Create account". Enter an email
and password, but then click on "Advanced settings" and change the "Turtl
server" setting to your domain: `http://turtl.example.com` if you didn't set up
TLS yet and make the config file changes I mentioned above, or
`https://turtl.example.com`.

The application should sync right up and ... you can now securely annotate your
life! ;)

## Comments? Suggestions?
Open an issue here, or send me a note via Keybase -- https://keybase.io/toddwarner

---

## Addendum - Backing up your Turtl Server

There is now a backup script included with the turtl-server package and can be
found in /usr/share/turtl-server/

Once your Turl Server is set up, just copy the backup script (and its helper
script) to your local desktop (not on the server itself) and run it
(instructions in the comments of the script.

## Addendum - Configure default Nginx landing pages

Edit the default Nginx landing pages (browse to your server by IP address, for
example) and replace all the default pages with your own or blank pages. This
includes `index.html` and the error pages, `404.html`, etc. By default they are
found in  `/usr/share/nginx/html/`
