FROM python:3.6.5-alpine
WORKDIR /et
ADD . /et
RUN set -e;
RUN apk update
RUN apk upgrade
RUN apk add build-base
COPY requirements.txt /et
RUN pip install -r requirements.txt
CMD ["python","app.py"]