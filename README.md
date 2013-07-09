mwlinkscrape.py, a tool for finding sites with MediaWiki wikis
==============================================================

Origins
-------

I wrote this for the [Archive Team](http://www.archiveteam.org).
Archive Team is a loose collective of rogue archivists whose
speciality is rescuing user data on web services before they are
shut down. In the run-up to a shutdown, Archive Team needs to
find as many websites hosted on a given domain name as possible.
Major MediaWiki wikis are one great source of such sites, as
most major MediaWiki installs have the
[Linksearch extension](http://www.mediawiki.org/wiki/Extension:LinkSearch)
installed.

With the --output-format=csv and --use-wikis=WIKI option, this
may also be useful for Wikipedia editors needing machine-readable
lists of links to dead or soon-to-be-dead sites. Have fun.

Requirements
------------

You need [Beautiful Soup 3](http://www.crummy.com/software/BeautifulSoup/)
installed. Pick your favourite of
<code>sudo apt-get install python-beautifulsoup</code> or
<code>pip install BeautifulSoup</code> or
<code>easy_install BeautifulSoup</code>.

Usage
-----

Basic usage goes like this:

	mwlinkscrape.py www.dyingsite.com > sitelist.txt

You may also find stuff on subdomains:
 
	mwlinkscrape.py "*.dyingsite.com" > sitelist.txt

By default, mwlinkscrape will work as follows:

1. Grab [a page on the Archive Team wiki](http://archiveteam.org/index.php?title=List_of_major_MediaWiki_wikis_with_the_LinkSearch_extension), maintained by Archive Team
   volunteers, which contains a list of major MediaWiki installations
   with the LinkSearch extension installed.

2. Scrape each site on the list for external links and dump the
   URLs on stdout, one per-line.

Command-line options:

<pre>
$ python mwlinkscrape.py -h
usage: mwlinkscrape.py [-h] [--default-wikis] [--use-wikis WIKIS]
                     [--output-format FMT] [--verbose]
                     SITE [SITE ...]

Scrape MediaWiki wikis to find links to a given site or domain.

positional arguments:
  SITE                 site or domain to find, may contain wildcards such as
                       *.wikipedia.org

optional arguments:
  -h, --help           show this help message and exit
  --default-wikis      Use a built-in list of 12 major Wikimedia wikis, rather
                       than connecting to the Archive Team wiki to get a list.
  --use-wikis WIKIS    Specify a comma-separated list of wikis to use, rather
                       than grabbing a list from the Archive Team wiki. This
                       must be the path to the MediaWiki index.php script (for
                       example, http://en.wikipedia.org/w/index.php). The
                       LinkSearch extension must be installed on the site.
  --output-format FMT  Use output format FMT, where FMT is either "txt" (plain
                       list of URLs, one per line, the default) or "csv"
                       (comma-separated value files, with the first column
                       being the linked URL, the second being the URL of the
                       wiki article from which it is linked). Default is
                       "txt".
  --verbose            Print uninteresting chatter to stderr for debugging
                       purposes.
</pre>

Bugs
----
There are none that I know of. As it works by scraping HTML,
mwlinkscrape is very prone to breakage if the MediaWiki HTML
changes, and it's also likely to break on custom MediaWiki
templates.

The [list of wikis on the Archive Team wiki](http://archiveteam.org/index.php?title=List_of_major_MediaWiki_wikis_with_the_LinkSearch_extension)
could do with expanding.

License
-------
This was written by [Lewis Collard](http://lewiscollard.com).

The program and this README is in the public domain, to be used,
modified, and/or redistributed with no restrictions.

There are no warranties of any kind; use at your own risk.
