FROM python:3.10.14-bookworm

WORKDIR /etc/buildtheearth/watchman

COPY . ./

RUN pip install -r requirements.txt

CMD ["python", "watchman.py"]