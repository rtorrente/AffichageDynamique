FROM python:3.7
EXPOSE 8000

RUN apt-get update && apt-get install -y ghostscript imagemagick libfreetype6 cron

WORKDIR /app
COPY requirements.txt /app
RUN pip3 install -r requirements.txt
COPY . /app
RUN mkdir /app/tmp
ENV DATABASE_URL postgres://ad@db/ad
ENV SECRET_KEY ''
ENV DJANGO_ENV 'dev'
ENV MAILGUN_KEY ''
ENV MAILGUN_DOMAIN ''
ENV DEFAULT_FROM_EMAIL ''
ENV DEFAULT_GROUP_PK 0
ENV ALLOWED_HOSTS "affichage.bde-insa-lyon.fr"
ENV RECAPTCHA_PUBLIC_KEY ''
ENV RECAPTCHA_PRIVATE_KEY ''
ENV RESTAURANTS_FEED_PK ''
ENV RESTAURANTS_GROUP_PK ''
ENV EMAIL_SUBJECT_PREFIX '[Affichage Dynamique]'
ENV GOOGLE_ANALYTICS_PROPERTY_ID ''
RUN chmod +x bash/run-prod.sh
CMD bash/run-prod.sh