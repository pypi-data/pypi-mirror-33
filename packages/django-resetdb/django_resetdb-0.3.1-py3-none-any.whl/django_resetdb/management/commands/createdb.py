#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Drop the Django DB"""

from __future__ import print_function, unicode_literals

import logging
import subprocess
import sys

from django.core.management.base import BaseCommand

from django_resetdb.util import DB
from django_resetdb.dbops import createdb

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Creates your database"""

    help = "Creates your database"

    def handle(self, *args, **options):
        if options["verbosity"] > 1:
            logging.getLogger(__name__.split(".")[0]).setLevel(logging.DEBUG)

        print("Creating your database '{}'".format(DB["NAME"]))
        try:
            createdb()
        except subprocess.CalledProcessError as error:
            print("ERROR: {}".format(error), file=sys.stderr)
            sys.exit(1)
