#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File : TwitterHunter.py
# Description : Hunter class to find new tweets directly from other tweets.
# Auteur : Nils Schaetti <n.schaetti@gmail.com>
# Date : 11.12.2017 09:00:00
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

from .Hunter import Hunter
from .Tweet import Tweet
import logging
import time
import re
import pyTweetBot.twitter.TweetBotConnect
from textblob import TextBlob
import pyTweetBot.tools
import pyTweetBot.tools.strings as pystr
import urllib2


# Find new tweets from tweets coming form
# search on Twitter.
class TwitterHunter(Hunter):
    """
    This class of hunter will find new tweets by scanning
    URLs in other user's tweets found in research results.
    """

    # Constructor
    def __init__(self, search_term, hashtags, n_pages=2, polarity=0.0, subjectivity=0.5, languages=['en']):
        """
        Constructor
        :param search_term: The term to search on Twitter.
        :param hashtags: The list of hashtags to add to new tweets.
        :param n_pages: Number of pages to analyze for this search.
        :param polarity: Minimum polarity threshold (< 0 negative, > 0 positive)
        :param subjectivity: Maximum subjectivity threshold.
        :param languages: Accepted languages.
        """
        self._search_term = search_term
        self._hashtags = hashtags
        self._cursor = pyTweetBot.twitter.TweetBotConnector().search_tweets(search_term, n_pages)
        self._current = 0
        self._tweets = list()
        self._polarity = polarity
        self._subjectivity = subjectivity
        self._languages = languages
    # end __init__

    # Get hashtags
    def get_hashtags(self):
        """
        Get hashtags
        """
        return self._hashtags
    # end get_stream

    # To unicode
    def __unicode__(self):
        """
        To unicode
        :return:
        """
        return u"TwitterHunter(hashtag={})".format(self._search_term)
    # end __unicode__

    ############################################
    # Override
    ############################################

    # Iterator
    def __iter__(self):
        """
        Iterator
        :return: The object's iterator.
        """
        return self
    # end __iter__

    # Next
    def next(self):
        """
        Next
        :return: The next tweet found.
        """
        # Load if needed
        while len(self._tweets) == 0:
            self._load_tweets()
        # end if

        # Current tweet
        current_tweet = self._tweets[0]

        # Remove
        self._tweets.remove(current_tweet)

        # Return
        return current_tweet
    # end next

    ############################################
    # Private
    ############################################

    # Get tweets
    def _load_tweets(self):
        """
        Load new tweets from the search stream.
        """
        # Get page
        page = self._cursor.next()

        # Get all tweets
        for tweet in page:
            # Get urls
            urls = re.findall(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", tweet.text)

            # If there is URLs in the tweet
            if len(urls) > 0:
                # Analyze text
                tweet_blob = TextBlob(tweet.text)

                # Pass level of pol & sub
                if tweet_blob.sentiment.polarity >= self._polarity and \
                                tweet_blob.sentiment.subjectivity <= self._subjectivity and \
                                tweet_blob.detect_language() in self._languages:
                    # Retrieve page each URL
                    for url in urls:
                        # Get page info
                        try:
                            page_parser = pyTweetBot.tools.PageParser(url)
                        except Exception as e:
                            logging.getLogger(pystr.LOGGER).warning(
                                pystr.ERROR_RETRIEVING_PAGE.format(url, e)
                            )
                            continue
                        # end try

                        # Load true URL if not from Twitter
                        if "twitter.com" not in page_parser.raw_title and (
                                "http://" in page_parser.raw_title or "https://" in page_parser.raw_title):
                            # Get true page info
                            try:
                                true_page_parser = pyTweetBot.tools.PageParser(page_parser.raw_title)
                            except Exception as e:
                                logging.getLogger(pystr.LOGGER).warning(
                                    pystr.ERROR_RETRIEVING_PAGE.format(page_parser.raw_title, e)
                                )
                                continue
                            # end try

                            # Text longer than 3
                            if len(true_page_parser.text) > 3:
                                # Blog
                                true_text_blob = TextBlob(true_page_parser.text)

                                try:
                                    # Add to tweets
                                    if len(true_page_parser.raw_title) > 0 and true_text_blob.detect_language() in self._languages:
                                        self._tweets.append(Tweet(true_page_parser.raw_title, page_parser.raw_title, self._hashtags))
                                    else:
                                        logging.getLogger(pystr.LOGGER).warning(
                                            pystr.ERROR_TITLE_TOO_SHORT_BAD_LANGUAGE.format(
                                                len(true_page_parser.raw_title),
                                                true_text_blob.detect_language()
                                            )
                                        )
                                # end if
                                except urllib2.HTTPError:
                                    pass
                                # end if
                            else:
                                logging.getLogger(pystr.LOGGER).warning(
                                    pystr.ERROR_NOT_ENOUGH_PAGE_DATA.format(
                                        len(true_page_parser.text)
                                    )
                                )
                            # end if
                        # end if
                    # end for
                # end if
            # end if
        # end for

        # Wait
        logging.getLogger(pystr.LOGGER).info(pystr.INFO_TWITTER_WAIT)
        time.sleep(60)
    # end _load_tweets

# end RSSHunter
