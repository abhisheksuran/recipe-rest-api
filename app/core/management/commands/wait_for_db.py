"""
Django command to wait for  the database to be available.
"""
from django.core.management.base import BaseCommand
from psycopg2 import OperationalError as Psycopg2Error
import time
from django.db.utils import OperationalError



class Command(BaseCommand):
    """Django command to wait for database"""

    def handle(self, *args, **options):
        """handle command"""
        self.stdout.write('Waiting for database...')
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (OperationalError, Psycopg2Error):
                self.stdout.write('Database unavailable waiting for 1 sec ...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database Available!'))