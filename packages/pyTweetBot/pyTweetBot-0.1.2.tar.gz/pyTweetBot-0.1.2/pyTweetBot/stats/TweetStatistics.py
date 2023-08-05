#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File : stats.TweetStatistics.py
# Description : pyTweetBot tweet statistics managing class.
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

# Imports
import numpy as np
import pickle
import datetime

#######################################
# Exception
#######################################


# Exception: the tweet is already counted in stats
class TweetAlreadyCountedException(Exception):
    """
    Exception: the tweet is already counted in stats
    """
    pass
# end TweetAlreadyCountedException

#######################################
# Class
#######################################


# Tweet statistics managing class
class TweetStatistics(object):
    """
    TWeet statistics managing class
    """

    # Constructor
    def __init__(self, slope=25, beta=5):
        """
        Constructor
        """
        self._statistic_matrix = np.zeros((7, 24), dtype='float64')
        self._counting_matrix = np.zeros((7, 24), dtype='float64')
        self._week_to_string = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self._last_tweet_id = 0
        self._tmp_max_tweet_id = 0
        self._counting = False
        self._slope = slope
        self._beta = 5
    # end __init__

    ##########################################
    # Public
    ##########################################

    # Start statistic counting
    def start(self):
        """
        Start statistic counting
        """
        self._counting = True
    # end start

    # End statistics counting
    def stop(self):
        """
        Stop statistic counting
        """
        self._last_tweet_id = self._tmp_max_tweet_id
        self._counting = False
    # end stop

    # Add a tweet to the stats
    def add(self, tweet):
        """
        Add a tweet to the stats
        :param tweet:
        :return:
        """
        if self._counting:
            if tweet.id > self._tmp_max_tweet_id:
                self._tmp_max_tweet_id = tweet.id
            # end if
            if tweet.id <= self._last_tweet_id:
                raise TweetAlreadyCountedException("Tweet already counted")
            else:
                self._statistic_matrix[
                    tweet.created_at.weekday(), tweet.created_at.hour] += tweet.retweet_count + float(
                    tweet.favorite_count) * 0.5
                self._counting_matrix[tweet.created_at.weekday(), tweet.created_at.hour] += 1.0
            # end if
        # end if
    # end add

    # Get total retweets/likes for a tuple weekday, hour
    def value(self, weekday, hour):
        """
        Get total retweets/likes to a tuple weekday, hour
        :param weekday:
        :param hour:
        :return:
        """
        return self._statistic_matrix[weekday, hour]
    # end value

    # Get total counts for a tuple (weekday, hour)
    def count(self, weekday, hour):
        """
        Get total counts for a tuple (weekday, hour)
        :param weekday:
        :param hour:
        :return:
        """
        return self._counting_matrix[weekday, hour]
    # end count

    # Get expected retweet for a tuple weekday, hour
    def expect(self, weekday, hour):
        """
        Get expected retweet for a tuple weekday, hour.
        :param weekday:
        :param hour:
        :return:
        """
        return self._statistic_matrix[weekday, hour] / self._counting_matrix[weekday, hour]
    # end expect

    # Get expected normalized retweet value for a tuple weekday, hour
    def expect_norm(self, weekday, hour):
        """
        Get expected normalized retweet value for a tuple week, hour
        :param weekday:
        :param hour:
        :return:
        """
        retweet_values = self._statistic_matrix / self._counting_matrix
        for w in range(7):
            for h in range(24):
                if np.isnan(retweet_values[w, h]):
                    retweet_values[w, h] = 0.0
                # end if
            # end for
        # end for
        max_value = np.max(retweet_values)
        retweet_values /= max_value
        return retweet_values[weekday, hour]
    # end expect_norm

    # Save the object to a file
    def save(self, filename):
        """
        Save the object to a file
        :param filename:
        :return:
        """
        with open(filename, 'w') as f:
            pickle.dump(self, f)
        # end with
    # end save

    ##########################################
    # Static
    ##########################################

    # Call and return the waiting time for now
    def __call__(self, time=datetime.datetime.utcnow(), slope=25.0, beta=5.0):
        """
        Call and return the waiting time for now
        :param time:
        :return: Waiting time in seconds
        """
        # Expected retweet counts normalized and inversed
        inv_norm_retweets = (self.expect_norm(time.weekday(), time.hour) * -1.0) + 1.0

        # Apply the function
        waiting_minutes = slope * inv_norm_retweets + beta

        # To seconds
        return waiting_minutes * 60.0
    # end __call__

    ##########################################
    # Static
    ##########################################

    # Load the object
    @staticmethod
    def load(filename):
        """
        Load the object
        :param filename:
        :return:
        """
        with open(filename, 'r') as f:
            obj = pickle.load(f)
            obj.stop()
            return obj
        # end with
    # end load

    ##########################################
    # Private
    ##########################################

    # Integer to weekday string
    def _weekday_to_int(self, weekday):
        """
        Integer to weekday string
        :param weekday:
        :return:
        """
        return self._week_to_string[weekday]
    # end _weekday_to_int

# end TweetStatistics

