# Onepanel Command Line Interface

## Publish PIP Package

```bash
python3 setup.py sdist  # create distribution
twine upload dist/*
```

### Testing

#### Testing Code:

```bash
BASE_API_URL=<api-url> python3 -m onepanel.cli
```

#### Local Package Installation

Make sure that `$PATH` contains paths for both Pythons, for example on macOS:

```bash
export PATH=~/Library/Python/3.6/bin:~/Library/Python/2.7/bin:$PATH
```

Install packages locally:

```bash
python setup.py install --user --record files.txt   # Install Python 2.7.x
python3 setup.py install --user --prefix= --record files.txt  # Install Python 3.6.x
```

Uninstall local packages:

```bash
tr '\n' '\0' < files.txt | xargs -0 rm -f --        # Uninstall
```

## Git integration
For the transparent integration onepanel with a git and avoiding asking git passwords every time we need to store git usernames and passwords in some secured storage. Git provides API to interact with such storages via `storage.helper` interface.

The general workflow is described in https://github.com/Microsoft/Git-Credential-Manager-for-Windows/wiki/How-the-Git-Credential-Managers-works.

For any platform git `storage.helper` interface is the same, but the storage itself is different, see https://help.github.com/articles/caching-your-github-password-in-git/ for details. But this GitHub instructions is little bit outdated and in latest git distributions for Windows and Mac platforms storages are configured by default and we do not need to change anything. For the Linux we may be need to instal storage manually. See below

### Windows
Run the command
```
> git config credential.helper
```
If the output is
```
manager
```
everything is configured.

### Mac
Run the command
```
$ git config credential.helper
```
If the output is
```
osxkeychain
```
everything is configured.

### Linux Ubuntu 16.04
There is no credential helper under Ubuntu 16.04 by default. But Git version > 2.11 support libsecret credential helper

Upgrade git to the version > 2.11
```
$ sudo apt-get update
$ sudo add-apt-repository ppa:git-core/ppa
$ sudo apt-get update
$ sudo apt-get install git
```

Build libsecret
```
$ sudo apt-get install libsecret-1-0 libsecret-1-dev
$ cd /usr/share/doc/git/contrib/credential/libsecret
$ make
```

Configure git
```
$ git config --global credential.helper /usr/share/doc/git/contrib/credential/libsecret/git-credential-libsecret
```
