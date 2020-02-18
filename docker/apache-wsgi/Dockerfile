FROM debian:latest

ARG PATH=/usr/local/bin:$PATH
RUN apt-get update && apt-get install -y build-essential \
    vim zip tzdata \
    apache2 \
    libapache2-mod-wsgi-py3 \
    python3 python3-dev \
    python3-pip \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*
ENV TZ Asia/Tokyo
RUN pip3 install awscli Flask
COPY ./flask /var/www/flask
COPY ./flask.conf /etc/apache2/sites-available/flask.conf
RUN chown -R www-data. /var/www/flask
RUN ln -s /etc/apache2/sites-available/flask.conf /etc/apache2/sites-enabled/flask.conf
RUN rm /etc/apache2/sites-enabled/000-default.conf
EXPOSE 80
CMD ["apachectl", "-D", "FOREGROUND"]