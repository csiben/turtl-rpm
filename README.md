# Turtl: The Secure Collaborative Notebook, for Fedora Linux

Turtl is a nifty desktop and mobile application for writing and organizing
[markdown](https://en.wikipedia.org/wiki/Markdown)-formatted documents and
storing them securely encrypted on the file system but also synced with a central server and thus allowing your multiple devices to maintain the same set of documents. That Turtl server can be the server run by the primary Turtl developer (apiv3.turtlapp.com) or a server you run and maintain yourself.

## What's in this repository?

Turtl desktop and mobile clients speak and synchronize with Turtl servers. This
repository provides and maintains source packages that can be built to run on
(all I have tested so far) Fedora Linux 29+ on x86_64. Binary (fully
functional) application packages based on these source packages are available
elsewhere (see below) and make running either a Turtl desktop or a Turtl server
relatively easy install and maintain.

The two available applications.

- `turtl-desktop`: This is the graphical notebook application used to write and manage notes, thoughts, lists, files, etc. It stores everything locally, but also on a central server...
- `turtl-server`: This is a headless server that serves as a backend synchronization mechanism for Turtl clients. It enables Turtl clients to backup and store all those notes, thoughts, lists, and files and then make them available to all of the user's devices. It also allows users to share and collaborate with other users leveraging the same server -- friends, family, teammates, etc.

In order to use this application as a normal user, you only need to download and install the `turtl-desktop` application. It will, by default, create an account and synchronize with the Turtl Server run by the primary Turtl developer. If you wish to not rely on a 3rd party, that's why we provide `turtl-server`. You too can manage your own Turtl client-server software stack.

Visit the developers's github -- https://github.com/turtl/ -- or his working
project homepage -- https://turtlapp.com/

## Why github for this sort of thing?

I build RPM packages for various projects. Constructing and maintaining source RPMs is very much like any other software or documentation effort. That effort  for Turtl is maintained with source-control via github. Binaries are provided
[here](https://copr.fedorainfracloud.org/coprs/taw/turtl/). But you don't need to know a whole lot about Fedora's COPR build environment to install and user these RPMs. Just follow the "TL;DR" instructions below to install Turtl.

If you are technically able, you can build your own binary packages from the source RPMs provided in this github repository. Please note that all `src.rpm` files will be signed with my general-purpose GPG key found here:
<https://keybase.io/toddwarner/key.asc>.

Binary RPMs delivered via COPR are signed with a GPG key specific to that
repository. COPR enablement as shown below (TL;DR) will install this key
appropriately when necessary.

## TL;DR - I want to install the desktop version of Turtl!

Open up a terminal and copy and paste these on the commandline of your Fedora
Linux workstation/desktop. Note, I assume you are logged in as a user that has
"sudo" rights.

```
# Initial install...
sudo dnf copr enable taw/turtl
sudo dnf install turtl-desktop
```

```
# Update/upgrade...
sudo dnf upgrade turtl-desktop
```

Now find Turtl in your menus or normal GUI application search and run it.

* Note1: Desktop data for an individual user is, by default, located here:
  `~/.config/Turtl/core`
* Note2: By default, the desktop application will synchronize with an account
  on turtlapp.com (the primary Turtl developer's server). If you want to use a
  different Turtl server, that is configured in "Advanced settings".

## TL;DR - I want to install and host a Turtl Server!

Installation and configuration of a Turtl Server is longer than "TL;DR", but
dive in and set up your own Turtl Server in support of your desktop and mobile
Turtl clients using the RPMs provided here.

<https://github.com/taw00/turtl-rpm/blob/master/README-turtl-server.md>

## Comments? Suggestions?
Open an issue here, or send me a note via Keybase -- https://keybase.io/toddwarner
