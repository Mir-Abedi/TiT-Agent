# Use official Python image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /code

# Install dependencies
COPY requirements.txt /code/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project
COPY . /code/

# Collect static files (optional)
# RUN python manage.py collectstatic --noinput

# Command to run the app
CMD ["gunicorn", "myproject.wsgi:application", "--bind", "0.0.0.0:8000"]
