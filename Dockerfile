<<<<<<< HEAD
FROM python:3.6
=======
FROM python:jessie-slim
>>>>>>> c46bdb4ff9540e7df2689dbbea29418f4689f8c6
WORKDIR /app
COPY requirements.txt /app
RUN pip install -r /app/requirements.txt
ADD . /app
EXPOSE 80
<<<<<<< HEAD
ENV AUTH ""
CMD ["python","-u","./Bryce.py"]
=======
ARG AUTH
ENV AUTH = $AUTH
CMD ['python', './Bryce.py']

>>>>>>> c46bdb4ff9540e7df2689dbbea29418f4689f8c6
