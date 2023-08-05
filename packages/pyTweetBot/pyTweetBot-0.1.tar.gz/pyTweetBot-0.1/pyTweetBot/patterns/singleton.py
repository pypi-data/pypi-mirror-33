#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# File : pyTweetBot.py
# Description : pyTweetBot action in the DB.
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


# Singleton design pattern
def singleton(class_):
    """
    Singleton design pattern
    :param class_:
    :return:
    """

    # Properties
    instances = {}

    # Get instance
    def getinstance(*args, **kwargs):
        """
        Get instance
        :param args:
        :param kwargs:
        :return:
        """
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        # end if
        return instances[class_]
    # end getinstance

    return getinstance

# end singleton
