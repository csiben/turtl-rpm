# Turtl: The Secure Collaborative Notebook - for Fedora Linux

Turtl is a nifty desktop and mobile application for writing and organizing
[markdown](https://en.wikipedia.org/wiki/Markdown)-formatted documents and then
storing, fully encrypted, on the local filesystem as well as synced to the
cloud, thus allowing your multiple devices to maintain the same set of
documents. Turtl also enables you to collaborating with other users on
selectively shared documents.

You can read more about what Turtl is [here](https://turtlapp.com).

# What's in this repository?

`turtl-desktop` and `turtl-server`

This repository provides and maintains source packages that can be built to run
on Fedora Linux 29+ on x86_64. Binary (fully functional) application packages
based on these source packages are available elsewhere (see below) and make
running either a Turtl desktop or a Turtl server relatively easy install and
maintain.

The two available applications.

- `turtl-desktop`: This is the graphical notebook application used to write and
  manage notes, thoughts, lists, files, etc. It stores everything locally, but
  syncs those documents to a central server...
- `turtl-server`: This is a headless server that serves as a backend
  synchronization mechanism for Turtl clients. It enables Turtl clients to
  backup and store all those notes, thoughts, lists, and files and then make them
  available to all of the user's devices. It also allows users to share and
  collaborate with other users leveraging the same server -- friends, family,
  teammates, etc. You do not need to install a Turtl Server in order to use Turtl
  on the desktop or mobile. By default, your devices will synchronize with the
  Turtl Server kindly provided by the project's lead developer. But if you want
  to bring the backend server in house? `turtl-server` will enable you to do just
  that.

In order to use this application, you only need to download and install the
`turtl-desktop` application. It will, by default, create an account and
synchronize with the Turtl Server run by the primary Turtl developer. If you
wish to not rely on a 3rd party, that's why we provide `turtl-server`. You too
can manage your own Turtl client-server software stack.

Visit the developers's github -- https://github.com/turtl/ -- or his working
project homepage -- https://turtlapp.com/

## Why github for this sort of thing?

I build RPM packages for various projects. Constructing and maintaining source
RPMs is very much like any other software or documentation effort. That effort
for Turtl is maintained with source-control via github. Binaries are provided
[here](https://copr.fedorainfracloud.org/coprs/taw/turtl/). But you don't need
to know a whole lot about Fedora's COPR build environment to install and user
these RPMs. Just follow the "TL;DR" instructions below to install Turtl.

If you are technically able, you can build your own binary packages from the
source RPMs provided in this github repository. Please note that all `src.rpm`
files will be signed with my general-purpose GPG key found here:
<https://keybase.io/toddwarner/key.asc>.

Binary RPMs delivered via COPR are signed with a GPG key specific to that
repository. COPR enablement as shown below (TL;DR) will install this key
appropriately when necessary.

## TL;DR - I want to install the desktop version of Turtl!

Open up a terminal and copy and paste these on the commandline of your Fedora
Linux workstation/desktop. Note, I assume you are logged in as a user that has
"sudo" rights.

**For Fedora users...**
```
# Initial install...
sudo dnf copr enable taw/turtl
sudo dnf install -y turtl-desktop
```
```
# Update/upgrade...
sudo dnf upgrade -y turtl-desktop
```

Now find Turtl in your menus or normal application search and run it.

* Note1: desktop data for an individual user is, by default, located here:
  `~/.config/Turtl/core`
* Note2: By default, the desktop application will synchronize with an account
  on turtlapp.com (the primary Turtl developer's server). If you want to use a
  different Turtl server, that is configured in "Advanced settings".

## TL;DR - I want to install and host a Turtl Server!

Installation and configuration of a Turtl Server is longer than "TL;DR", but
dive in and set up your own Turtl Server in support of your desktop and mobile
Turtl clients using the RPMs provided here.

<https://github.com/taw00/turtl-rpm/blob/master/README-turtl-server.md>

## A comment about how Turtl Desktop word-wraps paragraphs of text

**A soft break:** When line breaks in a paragraph of text are ignored upon
rendering the final published content. The markdown interpreter will freely flow the
paragraph of text as needed to fit the dimensions of the document. Hard breaks
can still be forced with <br/> or a double-space at the end of a line.
Traditional markdown assumes 'soft breaking' behavior.

**A hard break:** When every line break in a paragraph of text is treated as a
carriage return in the final published content, regardless of the dimensions
and margin spacing of the output medium.

Included with the turtl-desktop RPM package is a utilty to toggle between the
two behaviors: `sudo /usr/share/turtl-desktop/toggle-break-behavior.sh`

You can read more about a "soft line-breaks", otherwise known as a "soft breaks" or "soft
returns" here:
<https://en.wikipedia.org/wiki/Line_wrap_and_word_wrap#Soft_and_hard_returns>

---

## Comments? Suggestions?
Open an issue here, or send me a note via Keybase -- https://keybase.io/toddwarner

## Joplin, that other notebook application

I also build packages for Joplin. Another encrypted multi-device opensource
notebook application.  You can find more information about that
[here](https://github.com/taw00/joplin-rpm).

The two projects overlap in functionality, but Turtl is more geared for the
Google Keep-like user experience whereas Joplin aims more at the Evernote use
case.  Joplin has more robust editing features, which make it more useful for
lengthier documents, while Turtl's interface is optimized for shorter notes and
a postit-note feel. Turtl has a more powerful security model and enables
sharing of documents making it very collaborative.

Both are great projects. And yes, there are a lot of great markdown
notebook-ish applications out there, but only a few with full end-to-end
security like Turtl and Joplin. Definitely my two favorite projects in this
application space.

