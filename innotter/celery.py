from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "innotter.settings")

app = Celery("innotter", broker=os.getenv("CELERY_BROKER_URL"))
app.config_from_object("django.conf.settings")

app.autodiscover_tasks()
