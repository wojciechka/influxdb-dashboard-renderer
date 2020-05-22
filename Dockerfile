FROM python:3

RUN mkdir /dashboard
COPY arialnb.ttf /usr/share/fonts/truetype/arialnb.ttf
WORKDIR /dashboard

RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install flask influxdb-client Pillow matplotlib tzlocal

COPY ./influxdb_dashboard /dashboard/influxdb_dashboard
COPY server/server.py /dashboard

CMD ["python", "server.py"]
