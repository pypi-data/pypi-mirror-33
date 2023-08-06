"""Provides ability to (re)load config cache from the command line."""

from django.core.management.base import BaseCommand

from aboutconfig import utils

class Command(BaseCommand):
    """Loads all existing config entries into cache"""

    help = 'Loads all existing config entries into cache'

    def handle(self, *args, **options):
        utils.preload_cache()
