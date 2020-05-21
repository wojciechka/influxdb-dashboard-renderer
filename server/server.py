from flask import Flask, request, send_file
from influxdb_dashboard import InfluxDBDashboardView, InfluxDBDashboardOutput
from werkzeug.wsgi import FileWrapper
from influxdb_client import InfluxDBClient
from io import BytesIO

app = Flask(__name__)

@app.route('/', methods=['POST'])
def root():
    data = request.get_json()
    token=data['token']
    org_id=data["org_id"]
    label=data["label"]
    url=data["url"]
    width=data["width"]
    height=data["height"]
    c = InfluxDBClient(url=url, token=token, org=org_id)
    d = InfluxDBDashboardView.find_by_label(c, label)


    # render to an image - defaults to 1920x1080 pixels image, but this can be customized
    o = InfluxDBDashboardOutput(dpi=150, rows=d.height, width=width, height=height)
    img = o.draw(d)
    img_io = BytesIO()
    img.save(img_io, format='PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')


app.run(host='0.0.0.0')

