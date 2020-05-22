from flask import Flask, request, send_file
from influxdb_dashboard import InfluxDBDashboardView, InfluxDBDashboardOutput
from werkzeug.wsgi import FileWrapper
from influxdb_client import InfluxDBClient

from io import BytesIO
import os

app = Flask(__name__)

@app.route('/', methods=['POST'])
@app.route('/render', methods=['POST'])
def render():
  data = request.get_json()

  # InfluxDB parameters
  token=data.get('token', os.environ.get('INFLUXDB_TOKEN'))
  org_id=data.get('org_id', os.environ.get('INFLUXDB_ORG_ID'))
  url=data.get('url', os.environ.get('INFLUXDB_URL'))
  dashboard_label=data.get('label', os.environ.get('INFLUXDB_DASHBOARD_LABEL'))
  dashboard_id=data.get('id', os.environ.get('INFLUXDB_DASHBOARD_ID'))

  # Image output parameters
  width=int(data.get('width', 1920))
  height=int(data.get('height', 1080))
  mode=data.get('mode', os.environ.get('INFLUXDB_DASHBOARD_MODE', 'color'))
  dpi=int(data.get('dpi', os.environ.get('INFLUXDB_DASHBOARD_DPI', '150')))

  c = InfluxDBClient(url=url, token=token, org=org_id)

  # TODO: validate connection details and arguments and return error early if needed
  # TODO: support setting start/stop time, default to 1h or 7d
  # TODO: support passing arbitrary variables to dashboards

  if dashboard_id != None:
    d = InfluxDBDashboardView(c, dashboard_id)
  elif dashboard_label != None:
    d = InfluxDBDashboardView.find_by_label(c, dashboard_label)
  else:
    # TODO: throw error
    None

  o = InfluxDBDashboardOutput(dpi=dpi, rows=d.height, width=width, height=height, mode=mode)
  img = o.draw(d)
  img_io = BytesIO()
  img.save(img_io, format='PNG')
  img_io.seek(0)
  return send_file(img_io, mimetype='image/png')


app.run(host='0.0.0.0')

