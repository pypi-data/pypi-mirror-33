# -*- coding: utf-8 -*-

"""
    The OpenApprentice Foundation and GLUG - Gfycat Like Username Generator
    Copyright (C) 2018 The OpenApprentice Foundation - contact@openapprentice.org

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import random
import os.path
import io

from string import capwords


ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
ASSETS_DIR = os.path.join(ROOT_DIR, 'assets')
ADJECTIVES_FILE = os.path.join(ASSETS_DIR, 'adjectives')
NOUNS_FILE = os.path.join(ASSETS_DIR, 'nouns')


def get_random():
    """
    Generates a random username from two adjectives and one noun as follows:

        {adj}{adj}{noun}

    :return: Returns a random username
    """

    with io.open(ADJECTIVES_FILE, "r", encoding="utf-8") as f:
        adjectives = f.read().splitlines()
    with io.open(NOUNS_FILE, "r", encoding="utf-8") as f:
        nouns = f.read().splitlines()
    adjective_1 = capwords(random.choice(adjectives))
    adjective_2 = capwords(random.choice(adjectives))
    noun = capwords(random.choice(nouns))
    return "{}{}{}".format(adjective_1, adjective_2, noun)
