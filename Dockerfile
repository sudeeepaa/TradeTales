FROM python:3.9

WORKDIR /APP

COPY . .

RUN pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000", "--app-dir", "RestApi"]
