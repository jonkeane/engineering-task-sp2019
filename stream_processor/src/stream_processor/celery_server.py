from celery import Celery

app = Celery('processor',
             backend='rpc://',
             # backend = 'db+sqlite:///results.sqlite',
             broker='pyamqp://guest@localhost//',
             include=['stream_processor.tasks'])

app.conf.update(
    result_expires=3600,
)

# for calling from the commandline
if __name__ == '__main__':
    app.start()
