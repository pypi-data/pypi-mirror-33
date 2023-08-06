Usage:
    guessfilename.py [<options>] <list of files>

This little Python script tries to rename files according to pre-defined rules.

It does this with several methods: first, the current file name is analyzed and
any ISO date/timestamp and filetags are re-used. Secondly, if the parsing of the
file name did not lead to any new file name, the content of the file is analyzed.

You have to adapt the rules in the Python script to meet your requirements.
The default rule-set follows the filename convention described on
http://karl-voit.at/managing-digital-photographs/


:copyright: (c) by Karl Voit
:license: GPL v3 or any later version
:URL: https://github.com/novoid/guess-filename.py
:bugreports: via github or <tools@Karl-Voit.at>

Options:
  -h, --help     show this help message and exit
  -d, --dryrun   enable dryrun mode: just simulate what would happen, do not
                 modify files
  -v, --verbose  enable verbose mode
  -q, --quiet    enable quiet mode
  --version      display version and exit


