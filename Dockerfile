FROM python:alpine

WORKDIR /usr/src/app
COPY . .

RUN pip install -r requirements.txt

RUN apt-get update && apt-get install -y sqlite3
EXPOSE 80

CMD [ "python", "./app.py" ]