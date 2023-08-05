Usage:
    mediathekview_change_downloads_to_http.py

    This little Python script tries to locate the MediathekView XML
    file containing pending downloads, change their protocol from
    https to http and re-writes the XML file accordingly.

    Read
    https://github.com/novoid/mediathekview_change_downloads_to_http
    for further information.

:copyright: (c) by Karl Voit
:license: GPL v3 or any later version
:URL: https://github.com/novoid/mediathekview_change_downloads_to_http
:bugreports: via github or <tools@Karl-Voit.at>

Options:
  -h, --help     show this help message and exit
  -d, --dryrun   enable dryrun mode: just simulate what would happen, do not
                 modify files
  -v, --verbose  enable verbose mode
  -q, --quiet    enable quiet mode
  --version      display version and exit


