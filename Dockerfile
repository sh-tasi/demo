FROM python:3.11.0a7-slim-bullseye
WORKDIR /app
ADD . /app
RUN pip install -r requirements.txt 
EXPOSE 80
CMD ["python","app.py"] docker build -t demo Dockerfilepath 