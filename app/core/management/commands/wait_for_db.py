"""
Django command to wait for the database to be available.
"""
import time
from psycopg2 import OperationalError as Psycopg2Error
from django.core.management.base import BaseCommand

from django.db.utils import OperationalError

""" This is the error Django throws when the database is nor ready"""


class Command(BaseCommand):
    """
    Django command to wait for database.

    Whenever we call our Command class it will call handle method.
    """

    def handle(self, *args, **options):
        """
        Entrypoint for command.

        stdout is Standart output we can use to log things on the
        screen when our command is executed.
        """
        self.stdout.write('Waiting for database...')
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (Psycopg2Error, OperationalError):
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database available!'))
        """ style.SUCCESS will make green output  - Does not work on Gitbash """
