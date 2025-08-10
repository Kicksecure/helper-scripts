#!/bin/sh

## Copyright (C) 2012 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## Prevents daemons from starting while using apt-get.
## Takes care of chroot mount from getting locked.

## Therefore for example prevents connecting to the public Tor network while
## building the images. This is interesting for (obfuscated) bridge users and
## also prevents sensitive data from the build machine, such as the Tor
## consensus /var/lib/tor leaking into the image.

## This file gets deleted by the build script at the end.

## Thanks to
## http://lifeonubuntu.com/how-to-prevent-server-daemons-from-starting-during-apt-get-install/

exit 101
