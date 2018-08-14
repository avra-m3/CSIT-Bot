FROM python:3
WORKDIR /app
COPY requirements.txt /app
RUN pip install -r /app/requirements.txt
ADD . /app
EXPOSE 80
ENV AUTH ''

