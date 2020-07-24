import flask
from flask_cors import CORS
import sys
import os
from flask import request, jsonify
from drivers.Waveshare_ADDA import WAVESHARE_ADDA
from drivers.waveshare_definitions import *

app = flask.Flask(__name__)
CORS(app)
app.config["DEBUG"] = True

PI_HOST = 'klabs.local'
# To run on the Pi itself (instead of connecting over pipe), leave PI_HOST blank.
#PI_HOST = ''
ws = None

html_response_header = '''
<html>
    <head>
    <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
    </head>
    <body>
    <div class="container">
        <div class="row">
            <div class="column mt-5">
                <h1>Kennedy Labs Eval H/W Server</h1>
                <p>Please see documentation for usage.</p>
'''

html_response_footer = '''
    </div></div></div>
    </body>
    </html>
'''

@app.route('/', methods=['GET'])
def home():
    # yeah, not DRY, whatever Python is a shite language
    connString = '<span class="text-success">connected</span>' if ws else '<span class="text-danger">not connected</span>'
    body = "<p>PIGPIO server is <bold>" + connString + "</bold>.</p>"
    return html_response_header + body + html_response_footer

@app.route('/status', methods=['GET'])
def status():
    if not ws:
        return jsonify({ 'status': 'offline'})
    else:
        return jsonify({'status': 'online'})

@app.route('/connect', methods=['POST'])
def connect():
    global ws
    if not ws:
        try:
            ws = WAVESHARE_ADDA(pi_host=PI_HOST)
            return jsonify({'status': 'online'})
        except OSError:
            return jsonify({ 'error': 'could not connect to ' + PI_HOST}), 503
        except:
            # this is almost certainly "out of handles"
            # err = sys.exc_info()[0]
            # print(err)
            if not PI_HOST:
                # this means most likely, there is a lack of handles, so we need to restart and we're running on the Pi, so...
                os.system('systemctl restart pigpiod')
            return jsonify({ 'error': 'Unknown error occurred. Try again and if that does not work, you should restart the pigpiod service on the Pi.'}), 406
    else:
        return jsonify({'status', 'online'})

@app.route('/disconnect', methods=['POST'])
def disconnect():
    global ws
    if ws:
        ws.close()
        ws = None
    return jsonify({'status': 'offline'})


@app.route('/setv/<channel_num>/<voltage>', defaults={'tolerance': '0.01'}, methods=['POST'])
@app.route('/setv/<channel_num>/<voltage>/<tolerance>', methods=['POST'])
def set_voltage(channel_num, voltage, tolerance):
    if ws:
        if channel_num == '0':
            set_v, raw = ws.seek_voltage_auto_A(target_v = float(voltage), delta_v = float(tolerance))
            return jsonify({"channel": channel_num, "voltage": set_v, "raw": raw})
        if channel_num == '1':
            set_v, raw = ws.seek_voltage_auto_B(target_v=float(voltage), delta_v=float(tolerance))
            return jsonify({"channel": channel_num, "voltage": set_v, "raw": raw})
        return jsonify({ 'error': 'No such channel ' + channel_num})
    return jsonify({ 'error': 'hardware offline'}), 500

@app.route('/getv/<channel_num>', methods=['GET'])
def get_voltage(channel_num):

    if not ws:
        return jsonify({'error': 'hardware offline'}), 500

    if channel_num == 'all':
        readings = ws.read_all()
        results = []
        for r in readings:
            results.append({"voltage": r[0], "raw": r[1]})
        return jsonify(results)

    channel = AD_CHANNEL_MAP[channel_num]
    if not channel:
        return jsonify({"error": "No such channel " + channel_num}), 406

    voltage, hexValue = ws.read_voltage(channel)
    return jsonify({"voltage": voltage, "raw": hexValue})


# @app.route('/test', methods=['GET'])
# def test():
#     return jsonify(test_data)
#
# @app.route('/temp', methods=['GET'])
# def temp():
#     return jsonify({ 'temp1': temp1, 'temp2': temp2})

# @app.route('/temp', methods=['POST'])
# def set_temp():
#     global temp1
#     temp1 = request.json['temp1']
#     return jsonify(request.json)

app.run(host='0.0.0.0', port='5000')