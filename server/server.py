from flask import Flask, request
import influxdb_dashboard

app = Flask(__name__)

@app.route('/', methods=['GET'])
def root():
   return 'hello world', 200

app.run(host='0.0.0.0')

