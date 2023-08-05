#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File : find_tweet.py
# Description : Find new tweets from various sources
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
import logging
import os
import pickle
import learning
import tools.strings as pystr
import tweet as tw
from executor.ActionScheduler import ActionReservoirFullError, ActionAlreadyExists
from tools.PageParser import PageParser, PageParserRetrievalError
from tweet.GoogleNewsHunter import GoogleNewsHunter
from tweet.RSSHunter import RSSHunter
from tweet.TweetFinder import TweetFinder


# Find new tweets from various sources
def find_tweets(config, model_file, action_scheduler, n_pages=2, threshold=0.5):
    """Find tweet from Google News and RSS streams.

    Examples:
        >>> config = BotConfig.load("config.json")
        >>> action_scheduler = ActionScheduler(config=config)
        >>> find_tweets(config, "model.p", action_scheduler)

    Arguments:
        * config (BotConfig): BotConfig configuration object of type :class:`pyTweetBot.config.BotConfig`
        * model_file (str): Path to model file for classification
        * action_scheduler (ActionScheduler): Scheduler object of type :class:`pyTweetBot.executor.ActionScheduler`
        * n_pages (int): Number of pages to analyze
        * threshold (float): Probability threshold to be accepted as tweet
    """
    # Tweet finder
    tweet_finder = TweetFinder(shuffle=True)

    # Load censor
    censor = learning.CensorModel.load_censor(config)

    # Load model
    if os.path.exists(model_file):
        model = pickle.load(open(model_file, 'rb'))
    else:
        logging.getLogger(pystr.LOGGER).error(u"Cannot find model {}".format(model_file))
        exit()
    # end if

    # Mode loaded
    logging.getLogger(pystr.LOGGER).info(u"Model {} loaded".format(model_file))

    # Add RSS streams
    for rss_stream in config.rss:
        tweet_finder.add(RSSHunter(rss_stream))
    # end for

    # Add Google News
    for news in config.google_news:
        # Add for each tuple language/country
        for language in news['languages']:
            for country in news['countries']:
                tweet_finder.add(GoogleNewsHunter(search_term=news['keyword'], lang=language, country=country,
                                                  hashtags=news['hashtags'], n_pages=n_pages, languages=news['languages']))
            # end for
        # end for

        # Add as a Twitter hunter
        tweet_finder.add(tw.TwitterHunter(search_term=news['keyword'], hashtags=news['hashtags'], n_pages=n_pages,
                                          languages=news['languages']))
    # end for

    # For each tweet
    for tweet in tweet_finder:
        # On title
        on_title = False

        # Get page's text
        try:
            page_info = PageParser(tweet.get_url())
            page_text = page_info.text
        except PageParserRetrievalError as e:
            logging.getLogger(pystr.LOGGER).warning(pystr.WARNING_PAGE_RETRIEVAL.format(e))
            page_text = tweet.get_text()
            on_title = True
        # end try

        # Predict class
        prediction = model.predict([page_text])[0]
        probs = model.predict_proba([page_text])[0]
        censor_prediction, _ = censor(page_text)

        # Debug
        logging.getLogger(pystr.LOGGER).debug(
            pystr.DEBUG_NEW_TWEET_FOUND.format(tweet.get_text())
        )

        # Predicted as tweet?
        if len(page_text) >= 50 and censor_prediction == "pos" and (prediction == "pos" or on_title) and not tweet.already_tweeted():
            if probs[1] >= threshold or on_title:
                if not on_title or probs[1] >= 0.9:
                    # Try to add
                    try:
                        logging.getLogger(pystr.LOGGER).info(pystr.INFO_ADD_TWEET_SCHEDULER.format(
                            tweet.get_tweet()))
                        action_scheduler.add_tweet(tweet)
                    except ActionReservoirFullError:
                        logging.getLogger(pystr.LOGGER).error(pystr.ERROR_RESERVOIR_FULL)
                        exit()
                        pass
                    except ActionAlreadyExists:
                        logging.getLogger(pystr.LOGGER).error(pystr.ERROR_TWEET_ALREADY_DB.format(
                            tweet.get_tweet().encode('ascii', errors='ignore')))
                        pass
                    # end try
                else:
                    logging.getLogger(pystr.LOGGER).debug(
                        pystr.DEBUG_ON_TITLE_TOO_LOW.format(tweet.get_text(), prediction)
                    )
                # end if
            else:
                logging.getLogger(pystr.LOGGER).debug(
                    pystr.DEBUG_TWEET_BELOW_THRESHOLD.format(tweet.get_text(), prediction))
            # end if
        else:
            # Debug
            logging.getLogger(pystr.LOGGER).debug(
                pystr.DEBUG_TWEET_NEGATIVE.format(tweet.get_text(), prediction, censor_prediction, tweet.already_tweeted())
            )
        # end if
    # end for
# end if
