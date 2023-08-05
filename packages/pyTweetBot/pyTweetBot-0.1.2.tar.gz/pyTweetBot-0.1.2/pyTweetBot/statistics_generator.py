#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File : pyTweetBot.py
# Description : pyTweetBot, generate statistics about tweets.
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
import time
import os
import tweepy
import sys
from stats.TweetStatistics import TweetStatistics, TweetAlreadyCountedException

####################################################
# Main function
####################################################


# Statistics generator
def statistics_generator(twitter_connector, stats_file, n_pages, stream, info):
    """
    Statistics generator
    """
    # Stats for each day of the week
    if not os.path.exists(stats_file):
        stats_manager = TweetStatistics()
    else:
        stats_manager = TweetStatistics.load(stats_file)
    # end if

    # Display info?
    if info:
        for weekday in range(7):
            for hour in range(24):
                if stats_manager.count(weekday, hour) > 0:
                    sys.stdout.write(u"Expected number of retweets/likes "
                                     u"for weekday {}, hour {} : {} ({}/{})\n".
                                     format(weekday, hour, stats_manager.expect_norm(weekday, hour),
                                            stats_manager.count(weekday, hour), stats_manager.expect(weekday, hour)))
                # end if
            # end for
        # end for
        exit()
    # end if

    # Loop control
    cont = True
    main_loop = True

    # Start statistics
    stats_manager.start()

    # Main loop
    while main_loop:
        # Cursor
        if stream == "timeline":
            cursor = twitter_connector.get_time_line(n_pages=n_pages)
        else:
            cursor = twitter_connector.get_user_timeline(screen_name="nschaetti", n_pages=n_pages)
        # end if

        # Start statistics
        stats_manager.start()

        try:
            # For each of my tweets
            for index_page, page in enumerate(cursor):
                logging.info(u"Analyzing page number {}".format(index_page))

                # For each tweet
                for index_tweet, tweet in enumerate(page):
                    # Count
                    if not tweet.retweeted:
                        try:
                            stats_manager.add(tweet)
                            logging.info(u"{} more retweets and {} more likes for day {} hour {}".format(tweet.retweet_count,
                                                                                                         float(
                                                                                                             tweet.favorite_count) * 0.5,
                                                                                                         tweet.created_at.weekday(),
                                                                                                         tweet.created_at.hour))
                        except TweetAlreadyCountedException:
                            logging.info(u"Last tweet in stats reached... Exiting")
                            cont = False
                            break
                        # end try
                    # end if
                # end for

                # Control
                if not cont:
                    break
                # end if

                # Wait
                logging.info(u"Waiting 60 seconds for next page...")
                time.sleep(60)
            # end for
        except KeyboardInterrupt:
            main_loop = False
            pass
        except tweepy.error.TweepError as e:
            logging.error(u"Tweepy error while retrieving page : {}".format(e))
            if e.api_code == 429:
                time.sleep(600)
            # end if
            pass
        # end try

        # Stop & save statistics
        stats_manager.stop()
        stats_manager.save(stats_file)

        # Waiting 60 seconds to get new tweets
        logging.info(u"Waiting 60 seconds to get new tweets...")
        time.sleep(600)
    # end while

    # Save statistics
    stats_manager.save(stats_file)

    # Stop statistics
    stats_manager.stop()

# end if
