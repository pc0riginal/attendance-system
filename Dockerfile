FROM python:3.12-slim

WORKDIR /app

COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt

COPY . .

RUN python manage.py collectstatic --noinput --settings=temple_attendance.production_settings

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "temple_attendance.wsgi:application"]