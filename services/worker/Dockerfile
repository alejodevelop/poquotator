FROM python:3.11-slim
WORKDIR /worker
COPY worker/requirements.txt /worker/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY worker /worker
CMD ["celery", "-A", "tasks.app", "worker", "--loglevel=INFO"]