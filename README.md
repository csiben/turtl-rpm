# turtl-rpm
Source RPMs for Fedora Linux builds of... Turtl: The Secure Collaboritive Notebook

At the moment, only the desktop version is included. `turtl-desktop`, by
default, plugs into <https://turtlapp.com/> and synchronizes with that server
and allows you to collaborate with others who also use that server as a central
synchronization point.

You can also run your own server, but at the moment that is not enabled by the
software included in this repository.

## TL;DR

### I want to install the desktop version of Turtl!
```
# Initial install instructions...
sudo dnf copr enable taw/turtl
sudo dnf install turtl-desktop
```

```
# Update/upgrade instructions...
sudo dnf upgrade turtl-desktop
```

Desktop data for an individual user is, by default, located here: `~/.config/Turtl/core`

## Turtl? What the heck is Turtl?

Visit the developers's github -- https://github.com/turtl/ -- or his working
webapp version of the application -- https://turtlapp.com/

Turtl is a nifty application for writing
[markdown](https://en.wikipedia.org/wiki/Markdown)-formated documents and
storing them encrypted on the file system but synced to a central server.

## What is this github repo for?

I build RPMs here and there. I construct and maintain source RPMs and all that
data is stored in github repositories like this one. Building the binaries
(useable applications) is either up to the user, or you can use mine that I
build using [Fedora's COPR build cloud](https://copr.fedorainfracloud.org).
Follow the "TL;DR" instructions above to install Turtl.

Source RPMs found here should be signed with my general GPG key found here:
<https://keybase.io/toddwarner/key.asc>

Binary RPMs delivered via COPR are signed with a GPG specific to that
repository. COPR enablement as shown above will install this key appropriately
when ncessary.

## Comments? Suggestions?
Open an issue here, or send me a note via Keybase -- https://keybase.io/toddwarner
