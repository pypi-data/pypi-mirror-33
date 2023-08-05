![blacksap](http://www.jacomputing.net/direct_download/blacksap.png)

## Overview

[blacksap][] is a Python based RSS tracker that is designed to watch multiple RSS feeds from torrent sites and download any new
torrent files to a specified location.  If you have your torrent client configured to watch the same directory the files will be automatically picked up!

## License

[blacksap][] is released under the [GNU General Public License v3.0][], see the file LICENSE for the license text.

## Installation

As of version 1.3, blacksap is supported under Python 2.7, 3.6 and PyPy!

The most straightforward way to get blacksap working for you is:

> pip install blacksap

or

> python setup.py install

This will ensure that all the requirements are met.

__NOTE:__

By default, blacksap gets put in __/usr/local/bin/__

## Post Installation
You can get help from blacksap by running

    blacksap --help

in a terminal window.

### Tracking a new feed

To track a new RSS feed run:

    blacksap track <rss_url>

### Viewing tracked feeds

To view all the feeds being tracked, run:

    blacksap tracking

### Untracking a feed

To untrack a feed type:

    blacksap untrack <rss_url>

### Run blacksap

To get blacksap to check all RSS fees and download any new torrent files, simply run:

    blacksap run --output <directory>

__NOTE:__

On its first check of a new feed, blacksap will only download the most recent torrent file.  If you would like to download
more files (or none at all), override the number of files to download with the __--count__ flag!  Don't forget to specify
the URL of the new RSS feed or you will force that number of files to download from every tracked feed!

## Extras

## Preferences

The feeds that blacksap tracks are stored in __~/.blacksap.cfg__.  If you want to reset blacksap you can simply delete
this file.  It is also stored in JSON format, so feel free to edit the file in place if needed.

### App Settings

App specific settings are also stored in this file in an "app" hash.  The following settings are currently available for
configuration

* threads - Integer for number of threads to use (Default is None)
* proxies - Hash of proxies to use for 'http' and 'https' (Default is None)
* ipv6 - Boolean (Default is True)

### Feed Settings

In version 1.5 and later of blacksap you can add a special "rules" key to each feed that contains a list of regular expressions
that torrent files in the feed must match in order to be downloaded by blacksap.  The regular expressions are processed in
order and when the first match is found no other rules are applied.  If no "rules" key exists then any new files will be downloaded.


#### Example Settings

Below is an example blacksap configuration file:

    {
        "app": {
            "threads": 4,
            "ipv6": false,
            "proxies": {
                "http": "socks5://user:pass@fqdn:port",
                "https": "socks5://user:pass@fqdn:port"
            }
        },
        "feeds": [
          {
              "url": "https://example.com/search?q=latest_torrents&fmt=rss",
              "name": "Example Torrents",
              "hash": "51930c6ea13972d61d7783da0910aa89",
              "enabled": true,
              "new": false,
              "last": "My_Awesome_File.torrent",
              "rules": [
                "Awesome_File"
              ]
            }
        ]
    }

### Mac OSX LaunchAgent
If you are running OSX please check out the LaunchAgent in the git repo extras folder.  You can add it to your
__~/Library/LaunchAgents/__ directory and that way blacksap will run every hour and download new torrents automatically!

### UNIX/Linux Cronjob!

Add the following to your user's crontab (using _crontab -e_ command as your user) to schedule blacksap to run every
hour (downloading to a __~/torrents/__ directory):

    # Blacksap cronjob
    0 * * * * /usr/local/bin/blacksap run -o ~/torrents/

## Contributing

Comments and enhancements are very welcome.

Report any issues or feature requests on the [BitBucket bug
tracker](https://bitbucket.org/isaiah1112/blacksap/issues?status=new&status=open). Please include a minimal
(not-) working example which reproduces the bug and, if appropriate, the
 traceback information.  Please do not request features already being worked
towards.

Code contributions are encouraged: please feel free to [fork the
project](https://bitbucket.org/isaiah1112/blacksap) and submit pull requests to the develop branch.


[GNU General Public License v3.0]: http://choosealicense.com/licenses/gpl-3.0/ "GPL v3"

[blacksap]: https://bitbucket.org/isaiah1112/blacksap "blacksap"
