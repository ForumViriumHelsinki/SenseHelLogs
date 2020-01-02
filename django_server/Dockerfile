# pull base image
FROM python:3.7-alpine

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

# copy project
COPY . /app/

# copy Pipfile
COPY Pipfile /app/
COPY Pipfile.lock /app/

# install dependencies
RUN pip install pipenv
RUN pipenv install --system

# run entrypoint.sh
ENTRYPOINT ["/app/entrypoint.sh"]
