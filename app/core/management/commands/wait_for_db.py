"""
Django command to wait for db to be available
"""

import time

from django.core.management.base import BaseCommand
from django.db.utils import OperationalError
from psycopg2 import OperationalError as PsycopgError


class Command(BaseCommand):
	"""Django Command to wait for db """


	def handle(self, *args, **options):
		"""entry point for command"""
		# just logging
		self.stdout.write("Waiting for Database")
		# setting the bool of the database up status
		db_up = False
		# running until the db is up
		while not db_up:
			try:
				# if the db is not up will raise an error
				self.check(databases=['default'])
				# if didn't raise the db is up
				db_up = True
			#  catch the exception and sleeping for a sec before trying again
			except (PsycopgError, OperationalError):
				self.stdout.write('database not available, waiting 1 second')
				time.sleep(1)
		# exiting the while loop because the db is up
		self.stdout.write(self.style.SUCCESS("OK Database available!"))
