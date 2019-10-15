FROM python:3.6
WORKDIR /app
COPY requirements.txt /app
RUN pip install -r /app/requirements.txt
ADD . /app
CMD ["python","-u","./Bryce.py"]
