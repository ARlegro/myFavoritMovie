FROM python:3.9-slim 

WORKDIR /app

COPY . /app/

RUN pip install --no-cache-dir flask pymongo bs4 requests 

CMD [ "sh", "-c", "python init_db.py && python app.py" ]