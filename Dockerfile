FROM python:3.6
EXPOSE 8000


RUN apt-get update && apt-get install -y ghostscript imagemagick libfreetype6

WORKDIR /app

COPY requirements.txt /app
RUN pip3 install -r requirements.txt
COPY . /app
RUN chmod +x bash/run-prod.sh
CMD bash/run-prod.sh