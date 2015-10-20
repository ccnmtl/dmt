FROM ubuntu:trusty
RUN apt-get update
RUN apt-get install python-ldap libldap2-dev libsasl2-dev \
    python-all-dev libxml2-dev libxslt1-dev libjpeg-dev \
    python-tk liblcms1 libexif-dev libexif12 libfontconfig1-dev \
    libfreetype6-dev liblcms1-dev libxft-dev python-imaging \
    python-beautifulsoup python-dev libssl-dev gcc \
    build-essential binutils libpq-dev postgresql-client -y
ENV PYTHONUNBUFFERED 1
RUN apt-get install nodejs npm python-setuptools -y
RUN easy_install pip
RUN pip install --upgrade virtualenv
RUN ln -s /usr/bin/nodejs /usr/local/bin/node
RUN mkdir -p /var/www/dmt/dmt
COPY requirements.txt /var/www/dmt/dmt/
RUN pip install --no-deps -r /var/www/dmt/dmt/requirements.txt
WORKDIR /var/www/dmt/dmt
COPY . /var/www/dmt/dmt/
RUN python manage.py test
EXPOSE 8000
ADD docker-run.sh /run.sh
ADD docker-worker.sh /worker.sh
ADD docker-beat.sh /beat.sh
CMD ["/run.sh"]
