from celery import group
from celery_once import QueueOnce

from pipet.models import db
from pipet.sources.stripe import StripeAccount
from pipet.worker import celery


@celery.task(base=QueueOnce, once={'graceful': True})
def sync(account_id):
    account = StripeAccount.query.get(account_id)
    if account.backfilled:
        account.update()
    else:
        account.backfill()


@celery.task
def sync_all():
    job = group([sync.s(account.id) for account in StripeAccount.query.all()])
    job.apply_async()
