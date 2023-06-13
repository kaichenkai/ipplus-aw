# debian 10
FROM python:3.10.9-slim-buster
MAINTAINER chenk7@knownsec.com

RUN echo " " > /etc/apt/sources.list \
    && echo "deb http://mirrors.aliyun.com/debian/ buster main non-free contrib" >> /etc/apt/sources.list \
    && echo "deb-src http://mirrors.aliyun.com/debian/ buster main non-free contrib" >> /etc/apt/sources.list \
    && echo "deb http://mirrors.aliyun.com/debian-security buster/updates main" >> /etc/apt/sources.list \
    && echo "deb-src http://mirrors.aliyun.com/debian-security buster/updates main" >> /etc/apt/sources.list \
    && echo "deb http://mirrors.aliyun.com/debian/ buster-updates main non-free contrib" >> /etc/apt/sources.list \
    && echo "deb-src http://mirrors.aliyun.com/debian/ buster-updates main non-free contrib" >> /etc/apt/sources.list \
    && echo "deb http://mirrors.aliyun.com/debian/ buster-backports main non-free contrib" >> /etc/apt/sources.list \
    && echo "deb-src http://mirrors.aliyun.com/debian/ buster-backports main non-free contrib" >> /etc/apt/sources.list \
    && apt-get clean \
    && apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && apt-get install -y --no-install-recommends gcc python3-dev libsasl2-dev libldap2-dev libssl-dev \
    && apt-get install -y --no-install-recommends build-essential libigraph0v5 libigraph0-dev libxml2-dev libz-dev \
    && apt-get install -y --no-install-recommends libmariadb-dev-compat libmariadb-dev curl \
    && apt-get install -y --no-install-recommends supervisor nginx git vim dnsmasq nmap ssh nodejs \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /src/*.deb

ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip virtualenv -i https://pypi.douban.com/simple/ --trusted-host pypi.douban.com
RUN virtualenv /venv
ENV VIRTUAL_ENV /venv
ENV PATH /venv/bin:$PATH

RUN mkdir /app
WORKDIR /app

COPY ./requirements/base.txt /app/requirements/base.txt
COPY ./requirements/production.txt /app/requirements/production.txt
RUN pip install --no-cache-dir -r /app/requirements/production.txt -i https://pypi.douban.com/simple/ --trusted-host pypi.douban.com

COPY config /app/config
COPY ipplus /app/ipplus
COPY server_config /app/server_config
COPY manage.py /app/manage.py

RUN groupadd -r django && useradd -r -g django django
RUN chown -R django /app
RUN mkdir /data && chown -R django /data /etc/nginx /etc/supervisor /var /run
# for pocsuite
RUN mkdir /home/django && chown -R django /home/django
RUN mkdir /tmp/daphne && chown -R django /tmp/daphne
RUN echo "daemon off;" >> /etc/nginx/nginx.conf
COPY ./compose/django/entrypoint /entrypoint
#RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint
RUN chown django /entrypoint

COPY ./compose/django/start /start
#RUN sed -i 's/\r$//g' /start
RUN chmod +x /start
RUN chown django /start

VOLUME /data
USER django
WORKDIR /app
EXPOSE 8080

ENTRYPOINT ["/entrypoint"]

