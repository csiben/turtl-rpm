# turtl-rpm
Source RPMs for Fedora Linux builds of... Turtl: The Secure Collaboritive Notebook

Note: At the moment, only the desktop version of Turtl is provided. The webapp may come at a later date.

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

## Turtl? What the heck is Turtl?

Visit the developers's github -- https://github.com/turtl/ -- or his working
webapp version of the application -- https://turtlapp.com/

Turtl is a nifty application for writing
[markdown](https://en.wikipedia.org/wiki/Markdown)-formated documents and
storing them encrypted on the file system. You can run the application locally
as a single user, or collaboratively from a webapp that you set up, or using
the developers example webapp (see above).

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
