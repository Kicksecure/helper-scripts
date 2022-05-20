# Helper scripts useful for Linux Distributions #

Contains a script for curl progress bar in terminal. Includes another script
to convert curl exit codes to curl status messages. Implemented in bash.
Common code that can be used by other scripts.

Library that can be used by other (anonymity related) packages that want to
programmatically get information about states of Tor. Common code, that is
often required. Includes bash and Python helper scripts.

Leak Test for Anonymity Distribution Workstations
Integrated leak test.
Needs to be manually run.
See: https://www.whonix.org/wiki/Dev/Leak_Tests

Translatable GUI Messages
Generic modules guimessage.py and translations.py.
Called with two parameters: .yaml file path and yaml section. Return
translations according to distribution local language (Python 'locale').

Provides the ld-system-preload-disable wrapper to disable /etc/ld.so.preload
per application via bubblewrap. Useful if hardened_malloc is being globally
preloaded and needs to be disabled for some applications.

## How to install `helper-scripts` using apt-get ##

1\. Download the APT Signing Key.

```
wget https://www.kicksecure.com/derivative.asc
```

Users can [check the Signing Key](https://www.kicksecure.com/wiki/Signing_Key) for better security.

2\. Add the APT Signing Key..

```
sudo cp ~/derivative.asc /usr/share/keyrings/derivative.asc
```

3\. Add the derivative repository.

```
echo "deb [signed-by=/usr/share/keyrings/derivative.asc] https://deb.kicksecure.com bullseye main contrib non-free" | sudo tee /etc/apt/sources.list.d/derivative.list
```

4\. Update your package lists.

```
sudo apt-get update
```

5\. Install `helper-scripts`.

```
sudo apt-get install helper-scripts
```

## How to Build deb Package from Source Code ##

Can be build using standard Debian package build tools such as:

```
dpkg-buildpackage -b
```

See instructions.

NOTE: Replace `generic-package` with the actual name of this package `helper-scripts`.

* **A)** [easy](https://www.kicksecure.com/wiki/Dev/Build_Documentation/generic-package/easy), _OR_
* **B)** [including verifying software signatures](https://www.kicksecure.com/wiki/Dev/Build_Documentation/generic-package)

## Contact ##

* [Free Forum Support](https://forums.kicksecure.com)
* [Professional Support](https://www.kicksecure.com/wiki/Professional_Support)

## Donate ##

`helper-scripts` requires [donations](https://www.kicksecure.com/wiki/Donate) to stay alive!
