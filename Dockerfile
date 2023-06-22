FROM python:3.11

ENV PYTHONUNBUFFERED 1
RUN mkdir -p /opt/services/app/src /opt/services/app/database

COPY jiraworkflow/Pipfile jiraworkflow/Pipfile.lock /opt/services/app/src/
WORKDIR /opt/services/app/src
RUN pip install pipenv && pipenv install --system

COPY . /opt/services/app/src
RUN cd jiraworkflow && python manage.py collectstatic --no-input

EXPOSE 8000
CMD ["gunicorn", "-c", "config/gunicorn/conf.py", "--bind", ":8000", "--chdir", "jiraworkflow", "jiraworkflow.wsgi:application"]
