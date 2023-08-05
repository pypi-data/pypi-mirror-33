from celery import Celery

app = Celery("Micro", backend="rpc://")


class Requests:
    def __init__(self, broker, queue):
        app.conf.update(
            broker_url=broker,
            task_routes={"Micro.*": {"queue": queue}}
        )

    @app.task(name="Micro.plugins")
    def plugins():
        pass

    @app.task(name="Micro.info")
    def info(name):
        pass

    @app.task(name="Micro.help")
    def help(name):
        pass

    @app.task(name="Micro.run")
    def run(plugin_name, **kwargs):
        pass
