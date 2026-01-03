import sys

import logging

from celerytest.main import main

logger = logging.getLogger()
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

def run_app():
    main()

def run_celery_worker():
    import subprocess
    subprocess.run(["celery", "-A", "celerytest.tasks.celery_app", "worker", "--loglevel=info"])
