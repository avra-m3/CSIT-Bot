FROM python:3
ADD Bryce.py /
RUN pip install -r requirements.txt
CMD [ "python", "./Bryce.py" ]



