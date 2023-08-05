#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File : pyTweetBot.py
# Description : pyTweetBot main execution file.
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
# along with pyTweetBot.  If not, see <http://www.gnu.org/licenses/>.
#

# Import
import argparse
import logging
import sys
import os
import pkg_resources
import codecs
from config.BotConfig import BotConfig, MissingRequiredField
from db.DBConnector import DBConnector
from executor.ActionScheduler import ActionScheduler
from friends.FriendsManager import FriendsManager
from twitter.TweetBotConnect import TweetBotConnector
from update_statistics import update_statistics
from find_tweets import find_tweets
from find_retweets import find_retweets
from find_follows import find_follows
from find_unfollows import find_unfollows
from find_github_tweets import find_github_tweets
from tweet_dataset import tweet_dataset
from retweet_dataset import retweet_dataset
from model_training import model_training
from model_testing import model_testing
from statistics_generator import statistics_generator
from list_actions import list_actions
from tweet.TweetFactory import TweetFactory
from execute_actions import execute_actions
from stats.TweetStatistics import TweetStatistics
from follower_dataset import follower_dataset
from create_database import create_database
from export_database import export_database
from import_database import import_database
from direct_messages import direct_messages
import tools.strings as pystr


####################################################
# Functions
####################################################


# Add default arguments
def add_default_arguments(p):
    """
    Add default arguments
    :param parser:
    :return:
    """
    # Configuration and log
    p.add_argument("--config", type=str, help="Configuration file", required=True)
    p.add_argument("--log-level", type=int, help="Log level", default=20)
    p.add_argument("--log-file", type=str, help="Log file", default="")
# end add_default_arguments


# Add model argument
def add_model_argument(p, required):
    """
    Add model argument
    :param p: Parser object
    :param required: Is the model argument required?
    """
    # Model
    p.add_argument("--model", type=str, help="Classification model's file", required=required)
    p.add_argument("--threshold", type=float, help="Probability threshold for the prediction to be positive",
                   default=0.5, required=False)
# end add_model_argument


# Create logger
def create_logger(name, log_level=logging.INFO, log_format="%(asctime)s :: %(levelname)s :: %(message)s", log_file=""):
    """
    Create logger
    :param name: Logger's name
    :param log_level: Log level
    :param log_format: Log format
    :param log_file: Where to put the logs
    :return: The logger object
    """
    # New logger
    logging.basicConfig()
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Create a file handler if needed
    if log_file != "":
        handler = logging.FileHandler(log_file)
        handler.setLevel(log_level)

        # Create a logging format
        formatter = logging.Formatter(log_format)
        handler.setFormatter(formatter)

        # Add the handlers to the logger
        logger.addHandler(handler)
    # end if

    return logger
# end create_logger


# Create config file
def create_config(config_filename):
    """
    Create config file
    :param config_filename:
    :return:
    """
    # Get template
    empty_config = pkg_resources.resource_string("config", 'config.json')

    # Write
    file_handler = codecs.open(config_filename, 'w', encoding='utf-8')
    file_handler.write(unicode(empty_config) + u"\n")
    file_handler.close()
# end create_config

####################################################
# Main function
####################################################


if __name__ == "__main__":

    # Argument parser
    parser = argparse.ArgumentParser(prog="pyTweetBot", description="pyTweetBot - A smart Twitter bot to replace yourself")

    # Command subparser
    command_subparser = parser.add_subparsers(dest="command")

    # Database parser
    tools_parser = command_subparser.add_parser("tools")
    add_default_arguments(tools_parser)
    tools_parser.add_argument("--create-database", action='store_true',
                              help="Create the database structure on the MySQL host", default=False)
    tools_parser.add_argument("--export-database", action='store_true',
                              help="Export tweets, tweeted and followers/friends to a file", default=False)
    tools_parser.add_argument("--import-database", action='store_true',
                              help="Import tweets, tweeted and followers/friends from a file", default=False)
    tools_parser.add_argument("--output", type=str,
                              help="Direction to import / to export to", default=".")
    tools_parser.add_argument("--create-config", action='store_true',
                              help="Create an empty configuration file", default=False)

    # Update statistics parser
    update_stats_parser = command_subparser.add_parser("user-statistics")
    add_default_arguments(update_stats_parser)

    # Find tweets
    find_tweet_parser = command_subparser.add_parser("find-tweets")
    add_default_arguments(find_tweet_parser)
    add_model_argument(find_tweet_parser, True)
    find_tweet_parser.add_argument("--n-pages", type=int, help="Number of pages on Google News", default=5)
    find_tweet_parser.add_argument("--text-size", type=int, help="Minimum test size to take into account for the test",
                                   default=2000)

    # Find retweets
    find_retweet_parser = command_subparser.add_parser("find-retweets")
    add_default_arguments(find_retweet_parser)
    add_model_argument(find_retweet_parser, True)
    find_retweet_parser.add_argument("--n-pages", type=int, help="Number of pages in hashtags feed", default=10)
    find_retweet_parser.add_argument("--text-size", type=int, help="Minimum test size to take into account for the test",
                              required=True)

    # Find likes
    find_like_parser = command_subparser.add_parser("find-likes")
    add_default_arguments(find_like_parser)
    add_model_argument(find_like_parser, True)
    find_like_parser.add_argument("--n-pages", type=int, help="Number of pages in hashtags feed", default=10)

    # Find follow
    find_follow_parser = command_subparser.add_parser("find-follows")
    add_default_arguments(find_follow_parser)
    add_model_argument(find_follow_parser, True)
    find_follow_parser.add_argument("--text-size", type=int,
                                     help="Minimum test size to take into account for the test",
                                     default=50)

    # Find unfollow
    find_unfollow_parser = command_subparser.add_parser("find-unfollows")
    add_default_arguments(find_unfollow_parser)
    add_model_argument(find_unfollow_parser, True)

    # Send private messages
    send_pm_parser = command_subparser.add_parser("send-private-message")
    add_default_arguments(send_pm_parser)
    add_model_argument(send_pm_parser, True)

    # Create data set and train models
    train_parser = command_subparser.add_parser("train")
    add_default_arguments(train_parser)
    add_model_argument(train_parser, False)
    train_parser.add_argument("--action", type=str,
                              help="Create a data set (dataset), train or test a model (train/test)")
    train_parser.add_argument("--dataset", type=str, help="Input/output data set file")
    train_parser.add_argument("--n-pages", type=int, help="Number of pages on Google News", default=2)
    train_parser.add_argument("--rss", type=str, help="Specific RSS stream to capture", default="")
    train_parser.add_argument("--news", type=str, help="Specific Google News research to capture", default="")
    train_parser.add_argument("--info", action='store_true', help="Show information about the dataset?", default=False)
    train_parser.add_argument("--classifier", type=str, help="Classifier type (NaiveBayes, MaxEnt, TFIDF, etc)",
                              default="NaiveBayes")
    train_parser.add_argument("--source", type=str,
                              help="Information source to classify (news, tweets, friends, followers, home)")
    train_parser.add_argument("--search", type=str, help="Tweet search term", default="")
    train_parser.add_argument("--text-size", type=int, help="Minimum test size to take into account for the test",
                              required=True)

    # User's statistics
    user_statistics_parser = command_subparser.add_parser("statistics")
    add_default_arguments(user_statistics_parser)
    add_model_argument(user_statistics_parser, False)
    user_statistics_parser.add_argument("--info", action='store_true', help="Show dataset informations", default=False)
    user_statistics_parser.add_argument("--stats-file", type=str, help="Twitter statistics file")
    user_statistics_parser.add_argument("--stream", type=str, help="Stream (timeline, user)", default="timeline")
    user_statistics_parser.add_argument("--n-pages", type=int, help="Number of page to take into account", default=-1)

    # List command
    list_actions_parser = command_subparser.add_parser("actions")
    add_default_arguments(list_actions_parser)
    list_actions_parser.add_argument("--type", type=str, help="Action type (tweet, retweet, like, follow, unfollow",
                                     default="")

    # List and update followers/friends list
    list_friends_parser = command_subparser.add_parser("friends")
    add_default_arguments(list_friends_parser)
    list_friends_parser.add_argument("--update", action='store_true', help="Update followers/friends in the DB")
    list_friends_parser.add_argument("--obsolete", action='store_true', help="Show only obsolete friends")
    list_friends_parser.add_argument("--friends", action='store_true', help="Show only friends")

    # Executor
    executor_parser = command_subparser.add_parser("execute")
    add_default_arguments(executor_parser)
    executor_parser.add_argument("--stats-file", type=str, help="Twitter statistics file", required=False, default=None)
    executor_parser.add_argument("--daemon", action='store_true', help="Run executor in daemon mode", default=False)
    executor_parser.add_argument("--break-time", action='store_true',
                                 help="Show break duration between execution for the current time", default=False)
    executor_parser.add_argument("--no-follow", action='store_true', help="Do not execute follow actions",
                                 default=False)
    executor_parser.add_argument("--no-unfollow", action='store_true', help="Do not execute unfollow actions",
                                 default=False)
    executor_parser.add_argument("--no-tweet", action='store_true', help="Do not execute tweet actions", default=False)
    executor_parser.add_argument("--no-retweet", action='store_true', help="Do not execute retweet actions",
                                 default=False)
    executor_parser.add_argument("--no-like", action='store_true', help="Do not execute like actions", default=False)

    # GitHub tweets
    github_tweets_parser = command_subparser.add_parser("find-github-tweets")
    add_default_arguments(github_tweets_parser)
    github_tweets_parser.add_argument("--depth", type=int, help="Number of contributions to tweet per repo", default=-1)
    github_tweets_parser.add_argument("--event-type", type=str, help="Event type to tweet (push, create)", default="push")
    github_tweets_parser.add_argument("--instantaneous", action='store_true', help="Directly post tweets?", default=False)
    github_tweets_parser.add_argument("--waiting-time", type=int, help="Waiting time between each tweets (default=0)", default=0)

    # Direct message
    direct_messages_parser = command_subparser.add_parser("direct-messages")
    add_default_arguments(direct_messages_parser)

    # Parse
    args = parser.parse_args()

    # Logging
    logger = create_logger(pystr.LOGGER, log_level=args.log_level, log_file=args.log_file)

    # Need config and connect?
    if args.command != "tools" or not args.create_config:
        # Load configuration file
        try:
            config = BotConfig.load(args.config)
        except MissingRequiredField as e:
            sys.stderr.write(pystr.ERROR_PARSING_CONFIG_FILE.format(e))
        # end try

        # Connection to MySQL
        dbc = config.database
        mysql_connector = DBConnector(host=dbc["host"], username=dbc["username"], password=dbc["password"],
                                      db_name=dbc["database"])

        # Connection to Twitter
        twitter_connector = TweetBotConnector(config)

        # Friends
        friends_manager = FriendsManager()

        # Load stats file?
        stats_manager = None
        if 'stats_file' in args.__dict__.keys() and args.stats_file is not None:
            if os.path.exists(args.stats_file):
                stats_manager = TweetStatistics.load(args.stats_file)
            else:
                sys.stderr.write(u"Can not load stat file {}!\n".format(args.stats_file))
                exit()
            # end if
        # end if

        # Action scheduler
        action_scheduler = ActionScheduler(config=config, stats=stats_manager)

        # Tweet factory
        tweet_factory = TweetFactory(config.hashtags)
    # end if

    # Different possible command
    if args.command == "tools":
        # Create database
        if args.create_database:
            create_database(config)
        elif args.create_config:
            create_config(args.config)
        elif args.export_database:
            export_database(args.output, mysql_connector)
        elif args.import_database:
            import_database(args.output, mysql_connector)
        # end if
    # Update statistics
    elif args.command == "user-statistics":
        update_statistics(config=config)
    # Find tweets
    elif args.command == "find-tweets":
        find_tweets(config, args.model, action_scheduler, args.n_pages, args.threshold)
    # Find retweets
    elif args.command == "find-retweets":
        find_retweets(config, args.model, action_scheduler, args.text_size, args.threshold)
    # Find follows
    elif args.command == "find-follows":
        find_follows(config, args.model, action_scheduler, friends_manager, args.text_size, args.threshold)
    # Find unfollows
    elif args.command == "find-unfollows":
        find_unfollows(config, friends_manager, args.model, action_scheduler, args.threshold)
    # Training
    elif args.command == "train":
        # Action
        if args.action == u"dataset":
            if args.source == u"news":
                tweet_dataset(config, args.dataset, args.n_pages, args.info, args.rss)
            elif args.source == u"tweets":
                retweet_dataset(config, args.dataset, args.search, args.info, args.source)
            elif args.source == u"friends":
                follower_dataset(twitter_connector, args.dataset, args.info, u"following")
            else:
                sys.stderr.write(pystr.ERROR_UNKNOWN_SOURCE.format(args.source))
                exit()
            # end if
        elif args.action == u"test":
            model_testing\
            (
                data_set_file=args.dataset,
                model_file=args.model,
                text_size=args.text_size,
                threshold=args.threshold
            )
        elif args.action == u"train":
            model_training\
            (
                data_set_file=args.dataset,
                model_file=args.model,
                model_type=args.classifier
            )
        else:
            sys.stderr.write(pystr.ERROR_UNKNOWN_TRAINING.format(args.action))
            exit()
        # end if
    # Statistics generator
    elif args.command == "statistics":
        statistics_generator(twitter_connector, args.stats_file, args.n_pages, args.stream, args.info)
    # Executor
    elif args.command == "execute":
        execute_actions(
            config,
            action_scheduler,
            args.no_tweet,
            args.no_retweet,
            args.no_like,
            args.no_follow,
            args.no_unfollow
        )
    # List future action
    elif args.command == "actions":
        list_actions(action_scheduler, args.type)
    # List friends
    elif args.command == "friends":
        # Update friends
        if args.update:
            friends_manager.update()
        # end if
    # Find Github tweets
    elif args.command == "find-github-tweets":
        find_github_tweets(config, action_scheduler, args.event_type, args.depth, args.instantaneous, args.waiting_time)
    # Direct message
    elif args.command == "direct-messages":
        direct_messages(config)
    # Unknown command
    else:
        sys.stderr.write(pystr.ERROR_UNKNOWN_COMMAND.format(args.command))
    # end if

# end if