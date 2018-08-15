FROM python:3.6
WORKDIR /app
COPY requirements.txt /app
RUN pip install -r /app/requirements.txt
ADD . /app
EXPOSE 5012
ENV AUTH ""
CMD ["python","-u","./Bryce.py"]
