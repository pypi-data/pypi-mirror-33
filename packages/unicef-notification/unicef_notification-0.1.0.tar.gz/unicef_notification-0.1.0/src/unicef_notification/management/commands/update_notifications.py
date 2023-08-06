import logging
import os
from importlib import import_module

from django.apps import apps
from django.conf import settings
from django.core.management import BaseCommand
from django.db import transaction
from post_office.models import EmailTemplate

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Create Notifications command'

    @transaction.atomic
    def handle(self, *args, **options):
        logger.info('Command started')

        # loop through apps
        for app in apps.get_app_configs():
            # check if notification template dir exists
            notification_dir = "{}/{}".format(
                app.path,
                settings.UNICEF_NOTIFICATION_TEMPLATE_DIR
            )
            if os.path.isdir(notification_dir):
                # walk through notification templates
                filenames = [
                    f for f in os.listdir(notification_dir)
                    if os.path.isfile(os.path.join(notification_dir, f))
                ]
                for filename in filenames:
                    if filename.startswith("__"):
                        continue
                    n = import_module("{}.{}.{}".format(
                        app.name,
                        settings.UNICEF_NOTIFICATION_TEMPLATE_DIR,
                        filename.rsplit(".")[0]
                    ))
                    # creating email template objects
                    logger.info(n.name)
                    EmailTemplate.objects.update_or_create(
                        name=n.name,
                        defaults=n.defaults
                    )

        logger.info('Command finished')
