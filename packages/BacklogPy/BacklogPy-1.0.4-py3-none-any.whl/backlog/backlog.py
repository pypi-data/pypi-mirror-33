# coding: utf-8

"""
    This file was created by Backlog APIGenerator
"""


from __future__ import unicode_literals, absolute_import

from .api import *


class Backlog(Projects, Issues, Groups, Stars, Users, Watchings,
              Wikis, Notifications, Priorities, Space, Resolutions, Statuses):
    pass
