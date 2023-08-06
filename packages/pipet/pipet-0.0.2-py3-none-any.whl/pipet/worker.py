import os

from celery import Celery
from celery.signals import worker_process_init

from pipet import create_app


celery = Celery('pipet')
celery.conf.ONCE = {
    'backend': 'celery_once.backends.Redis',
    'settings': {
        'url': os.getenv('REDIS_URL'),
        'default_timeout': 60 * 60,
    }
}

TaskBase = celery.Task


class ContextTask(TaskBase):
    abstract = True

    def __call__(self, *args, **kwargs):
        with current_app.app_context():
            return TaskBase.__call__(self, *args, **kwargs)


celery.Task = ContextTask


@worker_process_init.connect
def init_celery_flask_app(**kwargs):
    app = create_app()
    app.app_context().push()


# from pipet.sources.stripe.tasks import sync_all as stripe_sync_all


# @celery.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     sender.add_periodic_task(60, stripe_sync_all.s(), name='test')
