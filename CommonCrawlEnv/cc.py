# Name      :  Akhil Amit Senroy
# UBIT      :  akhilami
# Person#   :  50288588
#
# Ref       :   https://www.bellingcat.com/resources/2015/08/13/using-python-to-mine-common-crawl/

import requests
import argparse
import time
import json
import StringIO
import gzip
import csv
import codecs
from bs4 import BeautifulSoup
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

# list of available indices
index_list = ["2019-13"]
# domain = "https://www.allmusic.com/blog"
# domain = "https://pitchfork.com"
domain = "http://blog.fortunes.io"

# Searches the Common Crawl Index for a domain.
def search_domain(domain):
    record_list = []
    print("[*] Trying target domain: %s" % (domain))
    for index in index_list:

        print ("[*] Trying index %s" % (index))
        cc_url  = "http://index.commoncrawl.org/CC-MAIN-2019-13-index?"
        cc_url += "url=http://blog.fortunes.io&matchType=domain&output=json"

        response = requests.get(cc_url)
        if response.status_code == 200:
            records = response.content.splitlines()
            for record in records:
                record_list.append(json.loads(record))

            print ("[*] Added %d results." % (len(records)))

    print ("[*] Found a total of %d hits." % (len(record_list)))

    return record_list

def download_page(record):

    offset, length = int(record['offset']), int(record['length'])
    offset_end = offset + length - 1

    # We'll get the file via HTTPS so we don't need to worry about S3 credentials
    # Getting the file on S3 is equivalent however - you can request a Range
    prefix = 'https://commoncrawl.s3.amazonaws.com/'

    # We can then use the Range header to ask for just this set of bytes
    resp = requests.get(prefix + record['filename'], headers={'Range': 'bytes={}-{}'.format(offset, offset_end)})

    # The page is stored compressed (gzip) to save space
    # We can extract it using the GZIP library
    raw_data = StringIO.StringIO(resp.content)
    f = gzip.GzipFile(fileobj=raw_data)

    # What we have now is just the WARC response, formatted:
    data = f.read()
    response = ""

    if len(data):
        try:
            warc, header, response = data.strip().split('\r\n\r\n', 2)
        except:
            pass

    return response

# Extract links from the HTML
def extract_external_links(html_content,link_list):

    parser = BeautifulSoup(html_content,features="html.parser")
    links = parser.find_all("a")

    if links:
        for link in links:
            href = link.attrs.get("href")

            if href is not None:

                if domain not in href:
                    if href not in link_list and href.startswith("http"):
                        # print ("[*] Discovered external link: %s" % (href))
                        link_list.append(href)

        f= open('links.txt', 'w')
        for link in link_list:
            f.write("\n\n"+str(link.encode('utf-8')))

    return link_list

record_list = search_domain("http://blog.fortunes.io")
link_list   = []

for record in record_list:

    html_content = download_page(record)
    print ("[*] Retrieved %d bytes for %s" % (len(html_content),record['url']))
    link_list = extract_external_links(html_content,link_list)

print ("[*] Total external links discovered: %d" % len(link_list))
try:
    with codecs.open("%s-links.csv" % domain,"wb",encoding="utf-8") as output:

        fields = ["URL"]

        logger = csv.DictWriter(output,fieldnames=fields)
        logger.writeheader()

        for link in link_list:
            logger.writerow({"URL":link})
except IOError:
    print()
