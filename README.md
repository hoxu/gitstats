# GitStats - git history statistics generator

## About

GitStats is a statistics generator for [git](http://git-scm.com/) (a distributed revision control system) repositories. It examines the repository and produces some interesting statistics from the history of it. Currently HTML is the only output format.

Also see the SourceForge [project page](http://sourceforge.net/projects/gitstats).

## Features

Here is a list of some statistics generated currently:

* General statistics: total files, lines, commits, authors.
* Activity: commits by hour of day, day of week, hour of week, month of year, year and month, and year.
* Authors: list of authors (name, commits (%), first commit date, last commit date, age), author of month, author of year.
* Files: file count by date, extensions
* Lines: Lines of Code by date

## Examples

See the [examples directory](http://gitstats.sourceforge.net/examples/) for example statistics generated for various projects.

## Requirements

* Git
* Python
* Gnuplot

## Getting GitStats

GitStats repository is hosted on both [GitHub](https://github.com/hoxu/gitstats) and [Gitorious](https://gitorious.org/gitstats/).

## Using git

The recommended way to get GitStats is to clone it with git:

    git clone git://github.com/hoxu/gitstats.git

The repository also contains the web site in the web branch.

## As a tarball

Alternatively, you can [download a tarball](https://github.com/hoxu/gitstats/tarball/master) of the latest version.

## Distro packaging

If you are running Debian Squeeze, Wheezy or Sid, you can install gitstats with:

    apt-get install gitstats

But note that [the version in Debian](http://packages.debian.org/gitstats) is most likely much older than the latest version available in git.

## License

Both the code and the web site are licensed under GPLv2/GPLv3.

## Related projects

[git](http://git.or.cz/)
Projects that generate statistics for other version control systems: StatCVS, StatSVN. Note that you can use GitStats for other version control systems by importing them to git first.
[Gource](https://code.google.com/p/gource/), software version control visualization.
[code_swarm](https://code.google.com/p/codeswarm/), organic software visualisation of project repositories.
