FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt --no-cache-dir
COPY api_foodgram/ .
CMD ["gunicorn", "api_foodgram.wsgi:application", "--bind", "0:8000" ]