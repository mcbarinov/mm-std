import logging

from mm_std import Scheduler


def test_scheduler():
    logger = logging.getLogger()
    scheduler = Scheduler(logger)
    scheduler.add_job(lambda x: x, 5)
    scheduler.start()
    scheduler.stop()
