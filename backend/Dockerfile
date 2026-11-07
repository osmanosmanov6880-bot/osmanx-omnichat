FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/srv/backend
WORKDIR /srv
RUN useradd --system --create-home --shell /usr/sbin/nologin omnichat
COPY backend/requirements.txt /srv/backend/requirements.txt
RUN pip install --no-cache-dir -r /srv/backend/requirements.txt
COPY backend /srv/backend
COPY frontend/public /srv/frontend/public
RUN chown -R omnichat:omnichat /srv
USER omnichat
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c 'import urllib.request;urllib.request.urlopen("http://127.0.0.1:8000/api/health/ready", timeout=4).read()'
CMD ["sh", "-c", "alembic -c /srv/backend/alembic.ini upgrade head && exec uvicorn app.main:app --app-dir /srv/backend --host 0.0.0.0 --port 8000 --workers 1 --no-proxy-headers"]
