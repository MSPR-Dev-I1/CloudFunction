import base64
import json
import functions_framework
import jwt

@functions_framework.http
def detect_new_image(cloud_event):
    data = cloud_event.data.decode('UTF-8')
    data = json.loads(data)

    encoded_jwt = data["message"]["data"]
    decoded_jwt = base64.urlsafe_b64decode(encoded_jwt + '=' * (4 - len(encoded_jwt) % 4)).decode('utf-8')
    decoded_message = json.loads(decoded_jwt)
    print(decoded_message['tag'])
    return print(decoded_message['tag'])
