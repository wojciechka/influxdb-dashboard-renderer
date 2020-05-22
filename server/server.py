from flask import Flask, request, Response, send_file
from influxdb_dashboard import InfluxDBDashboardView, InfluxDBDashboardOutput
from werkzeug.wsgi import FileWrapper
from influxdb_client import InfluxDBClient

from io import BytesIO
import os
import re

app = Flask(__name__)

# ensure GET requests are not cached
@app.after_request
def set_response_headers(response):
  response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
  response.headers['Pragma'] = 'no-cache'
  response.headers['Expires'] = '0'
  return response

@app.route('/', methods=['GET', 'POST'])
@app.route('/render', methods=['GET', 'POST'])
def render():
  if request.method == 'POST':
    data = request.get_json()
  else:
    data = request.args

  # InfluxDB parameters
  token=data.get('token', os.environ.get('INFLUXDB_TOKEN'))
  org_id=data.get('org_id', os.environ.get('INFLUXDB_ORG_ID'))
  url=data.get('url', os.environ.get('INFLUXDB_URL'))
  dashboard_label=data.get('label', os.environ.get('INFLUXDB_DASHBOARD_LABEL'))
  dashboard_id=data.get('id', os.environ.get('INFLUXDB_DASHBOARD_ID'))

  # dashboard time range
  start_offset=int(data.get('start_offset', -7*24*60))
  end_offset=int(data.get('end_offset', 0))
  window_period=int(data.get('window_period', 15))
  offset_unit=data.get('offset_unit', 'm')

  # Image output parameters
  width=int(data.get('width', 1920))
  height=int(data.get('height', 1080))
  mode=data.get('mode', os.environ.get('INFLUXDB_DASHBOARD_MODE', 'color'))
  dpi=int(data.get('dpi', os.environ.get('INFLUXDB_DASHBOARD_DPI', '150')))

  c = InfluxDBClient(url=url, token=token, org=org_id)

  if token == None or org_id == None or url == None or (dashboard_label == None and dashboard_id == None):
    return Response('{"status": "error", "message": "not all arguments were provided"}', status=422, mimetype='application/json')

  # TODO: support passing arbitrary variables to dashboards

  if dashboard_id != None:
    d = InfluxDBDashboardView(c, dashboard_id)
  elif dashboard_label != None:
    d = InfluxDBDashboardView.find_by_label(c, dashboard_label)
  else:
    # TODO: throw error
    None

  variables = {}
  if data.get('variables') != None:
    # if variables is passed as a JSON object, use that, expecting the object to be
    # { value: "value" }
    variables = data.get('variables')
  else:
    # otherwise assume literal values as variable_* parameters
    for key in filter(lambda k: re.match('^variable_', k), data.keys()):
      # extract key suffix
      variables[key[9:]] = { 'value': data[key] }

  d.set_time_range(start_offset=start_offset, end_offset=end_offset, window_period=window_period, offset_unit=offset_unit)
  for key in variables.keys():
    try:
      value = variables[key]['value']
    except:
      return Response('{"status": "error", "message": "variable value not provided"}', status=422, mimetype='application/json')
    # TODO: support other types of values for variables
    d.set_string_literval_variable(key, value)

  o = InfluxDBDashboardOutput(dpi=dpi, rows=d.height, width=width, height=height, mode=mode)
  img = o.draw(d)
  img_io = BytesIO()
  img.save(img_io, format='PNG')
  img_io.seek(0)

  return send_file(img_io, mimetype='image/png')

app.run(host='0.0.0.0')
