FROM ubuntu:latest
LABEL authors="meyer"

ENTRYPOINT ["top", "-b"]

FROM python:3.12

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

CMD ["python", "main.py"]

