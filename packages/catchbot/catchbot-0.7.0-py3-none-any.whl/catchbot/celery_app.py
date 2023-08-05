import os

from celery import Celery


def _get_broker():
    return 'pyamqp://{user}:{password}@{host}/{vhost}'.format(
        host='rabbitmq:5672',
        user=os.environ['RABBITMQ_DEFAULT_USER'],
        password=os.environ['RABBITMQ_DEFAULT_PASS'],
        vhost=os.environ['RABBITMQ_DEFAULT_VHOST'],
    )


try:
    broker = _get_broker()
except:
    print('Failed to get celery broker')
    broker = None

app = Celery('tasks', broker=broker)
