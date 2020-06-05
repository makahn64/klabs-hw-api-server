# Hardware API Server for Kennedy Labs Graphene Development System

This is a tiny Flask-based server meant as a shim between the real server written in NodeJS/React and the the
hardware drivers written in Python. I am by no means a Python pro, in fact, I am not a fan. So this API is as minimal as possible for now
and only has a few methods.

## Installation
1. Clone the repo into the `/opt/klabs` folder. Folder must have root permission. You will end up
with a path `/opt/klabs/klabs-hw-api-server`
2. Copy the `klabsapi.service` file to /etc/systemd/system folder (as root). `cp klabsapi.service /etc/systemd/system/`
3. `chmod u+rwx /etc/systemd/system/klabsapi.service` as root.
4. `systemctl enable klabsapi` then reboot.

From a browser, check the install by browsing to the Pi's address port 5000.

## GET /
Returns an HTML page showing the server is running and the connection status to the underlying PIGPIO daemon on the Pi.

## GET /status
Returns JSON showing the status of the connection to the PGPIO daemon. 
```json
{
"status": "offline"
}
```

## POST /connect
Tells the Flask server to connected to the PGPIO daemon. JSON reponse if successful/not-successful. If not successful, this
usually means the daemon is down or out of handles. In this case, the Flask server tries to restart the daemon silently.
```json
{
"status": "online"
}
```

## POST /disconnect
Opposite of /connect. Surprise! Response is JSON:
```json
{
"status": "offline"
}
```

## POST /setv/:channel/:voltage/:tolerance
Set a specific channel (either 0 or 1) to a voltage with an optional tolerance. Default tolerance is 0.01V.

Examples:
`POST /setv/0/1.25`

Sets channel 0 to 1.25V +/- 0.01V

`POST /setv/1/0.1/0.001`

Sets channel 1 to 0.1V +/- 0.001V.

Response is JSON with the actual set value and the value of the DAC register in base 10.
```json
{
  "channel": "0",
  "raw": 24629,
  "voltage": 1.2500919401755262
}
```

### Note on Hardware!
For the `setv` to work correctly, the following signals MUST MUST MUST be tied together:
- DAC0 and ADC0 (EXT0 in the code)
- DAC1 and ADC1 (EXT1 in the code)

If this is not done, then the algortihm that makes sure the voltage is correct will not work because it is not
sensing the output volatge from the DAC.

To do this, you will have to remove the jumpers on the Waveshare board that ties ADC0 and ADC1 to the potentiometer and photo resistor. You will also need to pull the jumpers that
connect DAC0/DAC1 to the on-board LEDs.

## GET /getv/:channel
Gets the voltage (and integer representation of the hex value) of a specific ADC channel (0..7).

Examples:
`GET /getv/6`

Response is JSON:
```json
{
  "raw": 2096971,
  "voltage": 1.2498922645917254
}
```

