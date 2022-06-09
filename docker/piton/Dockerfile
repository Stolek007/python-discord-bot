FROM python:latest

WORKDIR /piton

COPY requirements.txt /piton/.

RUN pip install -r requirements.txt

CMD [ "python3", "main.py" ]
