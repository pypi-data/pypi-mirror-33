#!/usr/bin/env python

import feedparser
import datetime
import urllib
import urllib2
import httplib
import shutil
import urlparse
import os
import sys

from lxml import etree, html
from cStringIO import StringIO

from ebooklib import epub


def downloadFile(url):
    """
    Downloads file from the URL. Returns None in case of any error.
    """

    try:
        r = urllib2.urlopen(urllib2.Request(url))
    except httplib.HTTPException:
        return None
    except ValueError:
        return None
    except urllib2.HTTPError:
        return None
    except IOError:
        return None

    try:
        data = r.read()
    except:
        return None
    finally:
        r.close()

    return data

def importFeed(document):

    book = epub.EpubBook()

    book.set_identifier(document.feed.link)
    book.set_title(document.feed.title)
    book.set_language(document.feed.language)
    
    book.add_author('Aleksandar Erkalovic')

    wpLink = document['feed']['link']

    attachments = []
    book.spine = []

    for n, item in enumerate(document['items']):
        # We only care about posts which have "publish" status. Ignore everything else for now.
        if item['wp_status'] !=  u'publish':
            continue

        chapterTitle = item['title']
        print '>> ', chapterTitle

        # So... let's clean our Wordpress post a bit. Here we ASSUME that empty line is used to separate paragraphs in Wordpress post.
        content = item['content'][0]['value'].replace('\r\n', '\n')
        content = '\n'.join(['<p>%s</p>' % p  for p in content.split('\n\n') if p.strip() != ''])

        # Every Booktype chapter starts with Chapter title embded in H2 tag. 
        content = u'<h2>%s</h2>%s' % (chapterTitle, content)

        tree = html.document_fromstring(content)

        for e in tree.iter():
            # We only care about images now
            if e.tag == 'img':
                src = e.get('src')
            
                if src:
                    if src.startswith('/'):
                        src = wpLink+src

                    # We don't need to download picture if it was already downloaed
                    if not src in attachments:
                        attachments.append(src)

                        u = urlparse.urlsplit(src)

                        # Get the file name and take care of funny stuff like %20 in file names
                        fileName = os.path.basename(urllib.unquote(u.path))
                    
                        print '      >> ', fileName
                        
                        # Download image
                        data = downloadFile(src)
                        
                        # Let us create this attachment if we managed to download something
                        if data:
                            pass
                            # We use standard method for saving the data.
                            #f2 = File(StringIO(data))
                            #f2.size = len(data)
                            #att.attachment.save(fileName, f2, save=True)
                            
                            #fileName = os.path.basename(att.attachment.path)

                            # Set whatever we got as a new attachment name. Also notice all images are referenced as
                            # "static/image.jpg" in Booktype so we have to change the source also.
                            #e.set('src', 'static/%s' % fileName)


        content =  etree.tostring(tree, encoding='UTF-8', method='html')

        c = epub.EpubHtml(title=chapterTitle, file_name='article_%d.xhtml' % n, lang='hr')
        c.set_content(content)

        book.add_item(c)
        book.spine.append(c)

    book.add_item(epub.EpubNcx())
    book.toc = ['cover']
        
    nav = epub.EpubNav()
    book.add_item(nav)

    epub.write_epub('wordpress.epub', book)


if __name__ == '__main__':
    document = feedparser.parse(sys.argv[1])

    # So we don't spend best years of our lives waiting

    import socket
    socket.setdefaulttimeout(10)

    # Import the feed
    importFeed(document)
    
