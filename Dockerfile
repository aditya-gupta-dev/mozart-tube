FROM python:3.11-slim

RUN apt-get update && apt-get install -y

COPY src/requirements.txt .
COPY src/main.py .

RUN pip install -r requirements.txt

EXPOSE 8000

CMD [ "python", "main.py" ]