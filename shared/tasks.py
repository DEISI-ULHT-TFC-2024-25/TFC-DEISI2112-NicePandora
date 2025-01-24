from celery import shared_task
from celery_progress.backend import ProgressRecorder
from .models import Attempt
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def run_tests(self, attempt_id):
	logger.info(f"Start processing attempt {attempt_id}")
	progress_recorder = ProgressRecorder(self)
	attempt = Attempt.getByID(attempt_id)
	attempt.run(progress_recorder)
