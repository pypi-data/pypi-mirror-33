#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File : news.GoogleNewsClient.py
# Description : Google News client.
# Auteur : Nils Schaetti <n.schaetti@gmail.com>
# Date : 01.05.2017 17:59:05
# Lieu : Nyon, Suisse
#
# This file is part of the pyTweetBot.
# The pyTweetBot is a set of free software:
# you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyTweetBot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with pyTweetBar.  If not, see <http://www.gnu.org/licenses/>.
#

# Import
import urllib2
from urlparse import urlparse
from HTMLParser import HTMLParser
from bs4 import BeautifulSoup
import time
import random
from .NewsParser import NewsParser
import logging
import httplib
import socket
import ssl
import brotli
import gzip
from StringIO import StringIO


#
# This is a Google News client
# Which return an array containing the urls and titles
#
class GoogleNewsClient(object):
    """
    This a a Google News client.
    Which returns an array containing the URLs and titles.
    """

    # Header
    _headers = {
        u'authority': u"",
        u'method': u"GET",
        u'path': u"",
        u'scheme': u"http",
        u'accept': u"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        u'accept-encoding': u"gzip, deflate, sdch, br",
        u'accept-language': u"fr,en;q=0.8",
        u'cache-control': u"no-cache",
        u'pragma': u"no-cache",
        u'upgrade-insecure-requests': 1,
        u'user-agent': u"Mozilla/5.0 (X11; Linux x86_64) "
                       u"AppleWebKit/537.36 (KHTML, like Gecko) "
                       u"Chrome/56.0.2924.87 "
                       u"Safari/537.36"
        # u'Accept-Charset': u'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        # u'Connection': u'keep-alive'
    }

    # Time out
    _timeout = 20

    # constructor
    def __init__(self, keyword, lang, country):
        """
        Constructor
        :param keyword:
        :param lang:
        :param country:
        """
        # Parameters
        self.keyword = keyword
        self.lang = lang
        self.country = country
    # end constructor

    ###############################################
    # Public
    ###############################################

    # Get news
    def get_news(self, page=0):
        """
        Get news
        :param page: Page to get
        :return: Array of news
        """
        # Init
        news = []

        # Logging
        logging.getLogger(u"pyTweetBot").debug(u"Getting page {}".format(page))

        # Add page's news
        news += self._get_page(page)

        # Wait for random time
        time.sleep(random.randint(15, 35))

        return news
    # end get_news

    # Get page's title
    def get_page_title(self, url):
        """
        Get page's title
        :param url:
        :return:
        """
        return self._get_news_title(url)
    # end get_page_title

    ###############################################
    # Private
    ###############################################

    # Request page
    def _request_page(self, url):
        """
        Request page
        :param url:
        :return:
        """
        # URL parser
        url_parse = urlparse(url)

        # Final header
        final_header = self._headers
        final_header[u'authority'] = url_parse.netloc
        final_header[u'path'] = url_parse.path
        if u"https:" in url:
            final_header[u'scheme'] = u"https"
        else:
            final_header[u'scheme'] = u"http"
        # end if

        # Call URL
        request = urllib2.Request(url, None, self._headers)

        # Request server
        response = urllib2.urlopen(request, timeout=self._timeout)

        # Data
        response_data = response.read()

        # Content encoding
        content_encoding = response.info().getheader('Content-Encoding')

        # Content encoding
        if content_encoding == 'br':
            return brotli.decompress(response_data)
        elif content_encoding == 'gzip':
            try:
                buf = StringIO(response_data)
                f = gzip.GzipFile(fileobj=buf)
                return f.read()
            except IOError as e:
                logging.getLogger(u"pyTweetBot").error(u"Invalid GZip data : {} for {}".format(e, url))
            # end try
        elif content_encoding is None or 'text/html' in content_encoding:
            return response_data
        else:
            logging.getLogger(u"pyTweetBot").error(u"Unknown encoding : {}".format(url))
        # end if
    # end _request_page

    # Get news' title
    def _get_news_title(self, url):
        """
        Get the news' title
        :param url: The news' URL.
        :return: The title
        """
        # HTML parser
        pars = HTMLParser()

        # Get HTML
        html = self._request_page(url)

        # Get URL's content
        soup = BeautifulSoup(html, "lxml")

        # Get and clean data
        new_title = unicode(soup.title.string.strip())
        new_title = new_title.replace(u'\n', u'').replace(u'\t', u'').replace(u"'", u"\'").replace(u"&amp;",
                                                                                                   u"&").replace(u'\r',
                                                                                                                 u'')
        new_title = new_title.replace(u'â&euro;&trade;', u"\'").replace(u'&#8217;', u"\'").replace(u'&#39;',
                                                                                                   u"\'").replace(
            u'&#039;', u"\'")
        new_title = new_title.replace(u'&#x27;', u'\\').replace(u'&rsquo;', u"\'").replace(u"  ", u" ")
        new_title = pars.unescape(new_title)

        # Return
        return new_title
    # end get_news_title

    # Get page
    def _get_page(self, page):
        """
        Get a page
        :param page: Page number
        :return: Page's news as an array.
        """
        # Init
        news = []

        # URL
        url = u"https://www.google.ch/search?hl=" + self.lang + u"&gl=" + self.country + u"&q=" + unicode(
                self.keyword.replace(u" ", u"+")) + u"&tbm=nws&start=" + unicode(page * 10)

        # Log
        logging.getLogger(u"pyTweetBot").info(u"Retrieving {}".format(url))

        # Get HTML
        cont = True
        counter = 0
        while cont:
            try:
                html = self._request_page(url)
                cont = False
            except urllib2.URLError as e:
                logging.getLogger(u"pyTweetBot").error(u"URL error while retrieving page {} : {}".format(url, e))
                time.sleep(20)
                pass
            except UnicodeEncodeError as e:
                logging.getLogger(u"pyTweetBot").error(u"Error while encoding request to unicode {} : {}".format(url, e))
                return news
            # end try
            counter += 1
            if counter >= 10:
                return news
            # end if
        # end while

        # instantiate the parser and fed it some HTML
        parser = NewsParser()
        parser.feed(html.decode('utf-8', errors='ignore'))

        # Get news
        urls = parser.get_news()

        # For each url
        for url in urls:
            # Get title
            try:
                title = self._get_news_title(url)
                news.append((url, title))
            except urllib2.HTTPError as e:
                logging.getLogger(u"pyTweetBot").error(u"HTTP Error while retrieving page {} : {}".format(url, e))
            except AttributeError as e:
                logging.getLogger(u"pyTweetBot").error(u"AttributeError while retrieving page {} : {}".format(url, e))
            except httplib.BadStatusLine as e:
                logging.getLogger(u"pyTweetBot").error(u"Bad status line error while retrieving page {} : {}".format(url, e))
            except socket.timeout as e:
                logging.getLogger(u"pyTweetBot").error(u"Socket error while retrieving page {} : {}".format(url, e))
            except httplib.IncompleteRead as e:
                logging.getLogger(u"pyTweetBot").error(u"Incomplete read error while retrieving page {} : {}".format(url, e))
            except urllib2.URLError as e:
                logging.getLogger(u"pyTweetBot").error(u"Error while retrieving page {} : {}".format(url, e))
            except ssl.CertificateError as e:
                logging.getLogger(u"pyTweetBot").error(u"Error with SSL Certificate while retrieving {} : {}".format(url, e))
            except ssl.SSLError as e:
                logging.getLogger(u"pyTweetBot").error(u"Error with SSL while retrieving {} : {}".format(url, e))
            except ValueError as e:
                logging.getLogger(u"pyTweetBot").error(u"Error with URL value while retrieving {} : {}".format(url, e))
            except TypeError as e:
                logging.getLogger(u"pyTweetBot").error(u"Type error while retrieving {} : {}".format(url, e))
            # end try
        # end for
        return news
    # end _get_page
# end GoogleNewsClient
