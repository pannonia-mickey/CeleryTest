import os
import random
import time
import uuid

from celery import Celery, chain
from celery.exceptions import Retry, MaxRetriesExceededError
from celery.utils.log import get_task_logger
from dotenv import load_dotenv

from celerytest.database import SessionLocal, PaymentRecord, OrderRecord, InvoiceRecord, ErrorRecord

load_dotenv()

celery_app = Celery(
    'worker',
    broker=os.getenv("CELERY_BROKER"),
    backend=os.getenv("CELERY_BACKENDS"),
    worker_prefetch_multiplier=1,
    task_acks_late=True
)

logger = get_task_logger(__name__)

def random_behavior():
    outcomes = [
        lambda: "Sikeres futás",
        lambda: "Sikeres futás",
        lambda: (_ for _ in ()).throw(ValueError("Érvénytelen érték!")),
        lambda: "Sikeres futás",
        lambda: "Sikeres futás",
        lambda: (_ for _ in ()).throw(RuntimeError("Futásidejű hiba!")),
        lambda: "Sikeres futás",
        lambda: "Sikeres futás",
        lambda: (_ for _ in ()).throw(KeyError("Hiányzó kulcs!"))
    ]
    return random.choice(outcomes)()

@celery_app.task(bind=True, max_retries=3)
def generate_invoice(self, order_id):
    logger.info(f"Generate invoice: {order_id}")
    db = SessionLocal()
    try:
        time.sleep(1)
        random_behavior()

        record = OrderRecord(order_id=order_id)
        db.add(record)
        db.commit()

        return f"{order_id}.pdf"
    except MaxRetriesExceededError:
        db.rollback()
        record = ErrorRecord(message=f"Unable to generate invoice for order {order_id}")
        db.add(record)
        db.commit()
        raise
    except Exception as e:
        db.rollback()
        raise self.retry(exc=e, countdown=2 * self.request.retries)
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=10)
def check_pdf_status(self, invoice_ref):
    logger.info(f"Check PDF status: {invoice_ref}")

    db = SessionLocal()
    try:
        if random.choice([True, False, True]):
            raise self.retry(countdown=2 * self.request.retries)

        invoice_id = uuid.uuid4()

        record = InvoiceRecord(invoice_ref=invoice_ref, invoice_id=invoice_id)
        db.add(record)
        db.commit()

        return f"{invoice_id}"
    except Retry:
        raise
    except MaxRetriesExceededError:
        db.rollback()
        record = ErrorRecord(message=f"Unable to create invoice {invoice_ref}")
        db.add(record)
        db.commit()
        raise
    except Exception as e:
        db.rollback()
        raise self.retry(exc=e, countdown=2 * self.request.retries)
    finally:
        db.close()


@celery_app.task(bind=True, max_retries=3)
def record_payment(self, invoice_id):
    logger.info(f"Record payment: {invoice_id}")

    db = SessionLocal()
    try:
        payment_id = uuid.uuid4()
        random_behavior()

        record = PaymentRecord(invoice_id=invoice_id, payment_id=payment_id)
        db.add(record)
        db.commit()

        return f"{payment_id}"
    except MaxRetriesExceededError:
        db.rollback()
        record = ErrorRecord(message=f"Unable to record payment for invoice {invoice_id}")
        db.add(record)
        db.commit()
        raise
    except Exception as e:
        db.rollback()
        raise self.retry(exc=e, countdown=2 * self.request.retries)
    finally:
        db.close()

def start_invoice_workflow(order_id):
    workflow = chain(
        generate_invoice.s(order_id),
        check_pdf_status.s(),
        record_payment.s(),
    )
    workflow.apply_async()
