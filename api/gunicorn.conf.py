import os

bind = "0.0.0.0:8000"
workers = int(os.getenv("API_WORKERS", "2"))
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
accesslog = "-"
errorlog = "-"
loglevel = "info"
