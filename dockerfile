FROM python:3

RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install flask 
RUN pip install influxdb-client 
RUN pip install Pillow
RUN pip install matplotlib
RUN pip install tzlocal

RUN mkdir /dashboard
WORKDIR /dashboard

COPY ./influxdb_dashboard /dashboard/influxdb_dashboard
COPY server/server.py /dashboard

CMD ["python", "server.py"]