FROM python:3.9-slim 

WORKDIR /app

COPY . /app/

CMD [ "sh", "c", "python init_db.py && python app.py" ]