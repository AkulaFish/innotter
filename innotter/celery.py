from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

from innotter import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "innotter.settings")

app = Celery("innotter", broker=settings.CELERY_BROKER_URl)
app.config_from_object("django.conf.settings")

app.autodiscover_tasks()
