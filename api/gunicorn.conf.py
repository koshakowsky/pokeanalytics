import os

bind = "0.0.0.0:8000"
workers = int(os.getenv("API_WORKERS", "2"))
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
accesslog = "-"
errorlog = "-"
loglevel = "info"


def on_starting(server):
    """Initialize the DB once, in the arbiter, before workers fork.

    Doing schema creation + seeding here (not in each worker's lifespan)
    avoids a race on the single SQLite file. The flag is inherited by forked
    workers so their lifespan skips re-initializing.
    """
    from bootstrap import INIT_DONE_ENV, initialize_database

    initialize_database()
    os.environ[INIT_DONE_ENV] = "1"
