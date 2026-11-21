FROM python:3.11-slim
WORKDIR /app
RUN useradd -m -u 10001 chronofact
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=chronofact:chronofact . .
RUN mkdir -p /app/data && chown -R chronofact:chronofact /app/data
USER chronofact
ENV CHRONOFACT_DATA_DIR=/app/data
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:8000/api/health')"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
