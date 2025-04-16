#!/bin/bash

## Copyright (C) 2019 - 2025 ENCRYPTED SUPPORT LLC <adrelanos@whonix.org>
## Copyright (C) 2019 - 2019 Dipto
## See the file COPYING for copying conditions.

get_password() {
   ## author of contents of get_password function
   ## Dipto
   ## https://askubuntu.com/users/133486/dipto
   ##
   ## source of contents of get_password function
   ##
   ## https://askubuntu.com/a/299469/389275
   ##
   ## license:
   ## licensed under cc by-sa 3.0 with attribution required.

   local char prompt

   password=""
   prompt=""

   while IFS= read -p "${prompt:-}" -r -s -n 1 char; do
      # Enter - accept password
      if [[ $char == $'\0' ]] ; then
         break
      fi
      # Backspace
      if [[ $char == $'\177' ]] ; then
         prompt=$'\b \b'
         password="${password%?}"
      else
         prompt='*'
         password+="$char"
      fi
   done
}
