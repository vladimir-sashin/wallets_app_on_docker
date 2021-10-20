from api_basics.models import TransactionReport
from celery import shared_task


@shared_task(
    ignore_result=True,
    autoretry_for=(Exception,),
    retry_backoff=10,
    retry_kwargs={"max_retries": 3},
)
def generate_report():
    TransactionReport.calculate_report()
