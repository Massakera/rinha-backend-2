
FROM python:3.10


WORKDIR /usr/src/app


COPY ./app /usr/src/app


COPY requirements.txt /usr/src/app/
RUN pip install --no-cache-dir -r requirements.txt


EXPOSE 80


ENV NAME World


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]
