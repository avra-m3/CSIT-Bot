FROM python:jessie-slim
WORKDIR /app
COPY requirements.txt /app
RUN pip install -r /app/requirements.txt
ADD . /app
EXPOSE 80
ARG AUTH
ENV AUTH = $AUTH
CMD ['python', './Bryce.py']

