import time

from celerytest.tasks import start_invoice_workflow


def main():
    for i in range(1,1000):
        start_invoice_workflow(f'2025-01-{i}')
        print(f'2025-{i}')
        time.sleep(1)
