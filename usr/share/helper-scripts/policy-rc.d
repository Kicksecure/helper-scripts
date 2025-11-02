#!/bin/sh

## Copyright (C) 2012 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## See the file COPYING for copying conditions.

## Can prevent daemons from starting while using 'apt-get' or 'apt-get-noninteractive'.
## Takes care of chroot mount from getting locked.

## 'apt-get-noninteractive' sets environment variable 'POLICYRCD'.
## Package 'policyrcd-script-zg2' supports environment variable 'POLICYRCD'.

## Therefore, for example, prevents connecting to the public Tor network while
## building the images. This is interesting for (obfuscated) bridge users and
## also prevents sensitive data from the build machine, such as the Tor
## consensus files in '/var/lib/tor' folder, from leaking into the image.

## Thanks to
## http://lifeonubuntu.com/how-to-prevent-server-daemons-from-starting-during-apt-get-install/

exit 101
