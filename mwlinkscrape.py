#!/usr/bin/python
import sys
import time
import urllib, urllib2
import argparse
import csv
import urlparse

from BeautifulSoup import BeautifulSoup
# how long to wait, in seconds, before requesting another page
# from a site
CRAWL_DELAY = 0.5
# how many links to grab from the site at the time, max 500
# decrease for debugging purposes
OFFSET_INC = 500
# user agent string
USER_AGENT = 'Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Ubuntu/10.04 Chromium/10.0.648.133 Chrome/10.0.648.133 Safari/534.16'

HEADERS = {"User-Agent": USER_AGENT}

DEBUG=True

DEFAULT_WIKIS = [
  "http://en.wikipedia.org/w/index.php",
  "http://commons.wikimedia.org/w/index.php",
  "http://de.wikipedia.org/w/index.php",
  "http://pl.wikipedia.org/w/index.php",
  "http://fr.wikipedia.org/w/index.php",
  "http://ja.wikipedia.org/w/index.php",
  "http://es.wikipedia.org/w/index.php",
  "http://ru.wikipedia.org/w/index.php",
  "http://nl.wikipedia.org/w/index.php",
  "http://sv.wikipedia.org/w/index.php",
  "http://ru.wikipedia.org/w/index.php",
  "http://pt.wikipedia.org/w/index.php",
]

def stderr_print(txt):
  sys.stderr.write("%s: %s\n" % (sys.argv[0], txt))

def debug_print(txt):
  if DEBUG:
    stderr_print(txt)

def get_retry(url, attempts=5):
  # gets the specified URL retrying the given number of times
  # returns None if it failed after X attempts, the content
  # of the page otherwise
  for i in range(0, 5):
    try:
      req = urllib2.Request(url, headers=HEADERS)
      u = urllib2.urlopen(req)
      return u.read()
    except Exception, detail:
      stderr_print("could not fetch %s (%s), attempt %s of %s" % (url,
        detail, i+1, attempts))
  stderr_print("gave up fetching %s" % url)
  return None

ap = argparse.ArgumentParser(description=(
  "Scrape MediaWiki wikis to find links to a given site or domain."
))
ap.add_argument("domains", metavar="SITE", type=str, nargs="+",
  help="site or domain to find, may contain wildcards such as *.wikipedia.org"
)
ap.add_argument("--default-wikis", action="store_true",
  help=("Use a built-in list of 12 major Wikimedia wikis, rather than "
        "connecting to the Archive Team wiki to get a list."))
ap.add_argument("--use-wikis", metavar="WIKIS",
  help=("Specify a comma-separated list of wikis to use, rather than "
    "grabbing a list from the Archive Team wiki. This must be the path "
    "to the MediaWiki index.php script (for example, "
    "http://en.wikipedia.org/w/index.php). The LinkSearch extension must "
    "be installed on the site.")
)
      
ap.add_argument("--output-format", metavar="FMT", choices=("csv", "txt"),
  default="txt",
  help=('Use output format FMT, where FMT is either "txt" (plain '
        'list of URLs, one per line, the default) or "csv" '
        '(comma-separated value files, with the first column being the '
        'linked URL, the second being the URL of the wiki article from '
        'which it is linked, and the third being the title of the '
        'article). Default is "txt".')
)
ap.add_argument("--verbose", action="store_true", default=False,
  help = ("Print uninteresting chatter to stderr for debugging purposes.") 
)
args = ap.parse_args()
DEBUG=args.verbose

wikis = []

if args.use_wikis:
  wikis = args.use_wikis.split(",")

elif args.default_wikis:
  wikis = DEFAULT_WIKIS
else:
  debug_print("fetching list of wikis from Archive Team")
  at = get_retry("http://archiveteam.org/index.php?title=List_of_major_MediaWiki_wikis_with_the_LinkSearch_extension")
  if at:
    soup = BeautifulSoup(at)
    pre = soup.find("pre", id="x_wiki_list")
    if not pre:
      stderr_print("got malformed page from Archive Team, using default wikis")
      wikis = DEFAULT_WIKIS
    else:
      text = "".join(pre.contents).strip()
      lines = text.split("\n")
      for line in lines:
        if not line.strip():
          # allow empty lines
          continue
        line = line.strip()
        if line[0] == "#":
          # comment
          continue
        wikis.append(line)
  else:
    stderr_print("warning: can't get wiki list from Archive Team, using default wikis")
    wikis = DEFAULT_WIKIS

debug_print("list of wikis to scan:")
for i in wikis:
  debug_print("* %s" % i)

if args.output_format == "csv":
  csv_out = csv.writer(sys.stdout)
  csv_out.writerow(["URL", "Linked from page", "Linked from title"])
else:
  csv_out = None

# keeps track of URLs we've already found, so we don't output duplicates
# (only applies in --output-format=txt mode)
found_urls = []
for fs in args.domains:
  for wiki in wikis:
    offset = 0
    eurl = urllib.urlencode({"target": fs})
    while True:
      url = "%s?title=Special:LinkSearch&limit=%s&offset=%s&%s" % (
        wiki, OFFSET_INC, offset, eurl)
      debug_print("fetching %s" % url)
      data = get_retry(url)
      if not data:
        stderr_print("unable to grab %s, moving on" % url)
        break
      soup = BeautifulSoup(data)
      debug_print("scraping %s" % url)
      pcontent = soup.find("div", attrs={"class": "mw-spcontent"})
      if not pcontent:
        stderr_print("cannot find div with class=mw-spcontent, malformed?")
        break
      ol = pcontent.find("ol", attrs={"class": "special"})
      if not ol:
        debug_print("no ol class='special', out of links")
        break
      lis = ol.findAll("li")
      for li in lis:
        # External links have the class "external"
        ex_url = li.find("a", attrs={"class": "external"}).renderContents()
        # Now find the first link *without* class="external"
        links = li.findAll("a")
        int_link = None
        for alink in links:
          if alink.has_key("class"):
            if alink["class"] != "external":
              int_link = alink
          else:
            int_link = alink
            break
        if not int_link:
          stderr_print("warning: can't find internal link, malformed?")
          stderr_print("happened on this: %s" % li)
          break
        int_link_url = int_link["href"]
        int_link_title = int_link["title"].encode("utf-8")
        if csv_out:
          # Internal links are in relative format, i.e. /wiki/Archive_Team.
          parts = urlparse.urlparse(wiki)
          rejoined = "%s://%s%s" % (parts.scheme, parts.netloc, int_link_url)
          csv_out.writerow([ex_url, rejoined, int_link_title])
        else:
          if not ex_url in found_urls:
            found_urls.append(ex_url)
            print ex_url        
      next_page = soup.findAll("a", attrs={"class": "mw-nextlink"})
      if not len(next_page):
        break
      offset += OFFSET_INC
      time.sleep(CRAWL_DELAY)
