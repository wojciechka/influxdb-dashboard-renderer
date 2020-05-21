from flask import Flask, request, send_file
from influxdb_dashboard import InfluxDBDashboardView, InfluxDBDashboardOutput
from werkzeug.wsgi import FileWrapper
from influxdb_client import InfluxDBClient
from io import BytesIO

app = Flask(__name__)

@app.route('/', methods=['GET'])
def root():
    token='replace me'
    org_id='844910ece80be8bc'
    label='rick'
    url="https://influxdb.aws.influxdata.io"
    c = InfluxDBClient(url=url, token=token, org=org_id)
    d = InfluxDBDashboardView.find_by_label(c, label)


    # render to an image - defaults to 1920x1080 pixels image, but this can be customized
    o = InfluxDBDashboardOutput(dpi=150, rows=d.height)
    img = o.draw(d)
    img_io = BytesIO()
    img.save(img_io, format='PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')


app.run(host='0.0.0.0')

