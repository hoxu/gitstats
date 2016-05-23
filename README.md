GitStats - git history statistics generator
==================

# About

GitStats is a statistics generator for git (a distributed revision control system) repositories. It examines the repository and produces some interesting statistics from the history of it. Currently HTML is the only output format.

Also see the SourceForge [project page](http://sourceforge.net/projects/gitstats).

# Features
Here is a list of some statistics generated currently:

- **General statistics**: total files, lines, commits, authors.
- **Activity**: commits by hour of day, day of week, hour of week, month of year, year and month, and year.
- **Authors**: list of authors (name, commits (%), first commit date, last commit date, age), author of month, author of year.
- **Files**: file count by date, extensions
- **Lines**: Lines of Code by date

# Usage
`gitstats repository_directory/ output_directory/`

See `man gitstats` for more options.

# Examples

See the [examples directory](http://gitstats.sourceforge.net/examples/) for example statistics generated for various projects.

Requirements
============

- Python (>= 2.6.0)
- Git (>= 1.5.2.4)
- Gnuplot (>= 4.0.0)
- a git repository (bare clone will work as well)

The above versions are not absolute requirements; older versions may work also.


Getting GitStats
================

GitStats repository is hosted on both [GitHub](https://github.com/hoxu/gitstats) and [Gitorious](https://gitorious.org/gitstats/).

## Using git

The recommended way to get GitStats is to clone it with git:

`git clone git://github.com/hoxu/gitstats.git`

The repository also contains the web site in the web branch.

## As a tarball

Alternatively, you can [download a tarball](https://github.com/hoxu/gitstats/tarball/master) of the latest version.

## Distro packaging

### Debian

If you are running Debian Squeeze, Wheezy or Sid, you can install gitstats with:

`apt-get install gitstats`

But note that [the version in Debian](http://packages.debian.org/gitstats) is most likely much older than the latest version available in git.

### Fedora

On Fedora 17 or later and EL6 distributions that have the EPEL repository [[1](https://bugzilla.redhat.com/show_bug.cgi?id=914996)] enabled:

`yum install gitstats`

### OS X

Homebrew contains [a head-only recipe for gitstats](https://github.com/Homebrew/homebrew-head-only/blob/master/gitstats.rb):

`brew install --HEAD homebrew/head-only/gitstats`

License
=======
Both the code and the web site are licensed under [GPLv2](http://www.gnu.org/licenses/gpl-2.0.txt)/[GPLv3](http://www.gnu.org/licenses/gpl-3.0.txt).

Related projects
================

- [git](http://git.or.cz/)
- Projects that generate statistics for other version control systems: [StatCVS](http://statcvs.sourceforge.net/), [StatSVN](http://statsvn.org/). Note that you can use GitStats for other version control systems by importing them to git first.
- [Gource](https://code.google.com/p/gource/), software version control visualization.
- [code_swarm](https://code.google.com/p/codeswarm/), organic software visualisation of project repositories.

Contributions
=============
Patches should be sent under "GPLv2 or later" license - this will allow upgrading to newer GPL versions if they are sensible.
