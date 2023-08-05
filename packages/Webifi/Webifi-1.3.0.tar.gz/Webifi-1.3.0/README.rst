Control Your Way Python Library
===============================

This project contains the library files Python V2.7 and V3. For examples on how to use this library please check out our other repositories on https://github.com/webifi-me

The latest library uses WebSocket for communication. This means websocket client needs to be installed for it to work. Please use the following command to install websocket client:
pip install websocket-client

The library documentation can be found at:
https://www.webifi.me/python-library-documentation/

V1.0.0
- First release

V1.1.0
- Fix problem with reconnect using WebSocket when encryption on/off changes

V1.1.1
- Fix problem with installer to import CreateSendData

V1.2.0
- Put all websocket send functions in try blocks
- If a websocket connection is already active and we receive new credentials then ignore it, otherwise it is not the same as the active connection. This can be a problem when the server restarts and multiple connection requests are sent. When multiple return then we must only use the first one.
- Check the upload queue when requesting credentials. If there are already one or more requests queued then don't add more, otherwise credentials are requested many times

V1.3.0
- Fix problem for Python 3 library, if WebSocket error then wrong field is used to log error message