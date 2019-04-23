from django.conf import settings
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import json
import http.client, urllib.request, urllib.parse, urllib.error, base64

def face_detect(filePath):
    headers = {
        # Request headers
        'Content-Type': 'application/octet-stream',
        'Ocp-Apim-Subscription-Key': settings.FACE_API_KEY,
    }

    params = urllib.parse.urlencode({
        # Request parameters
        'returnFaceId': 'true',
        'returnFaceLandmarks': 'false'
    })

    data = {}

    try:
        body = open(filePath, 'rb').read()
        conn = http.client.HTTPSConnection(settings.FACE_API_URL)
        conn.request("POST", "/face/v1.0/detect?%s" % params, body, headers)
        response = conn.getresponse()
        if response.status == 200:
            resBytes = response.read()
            jsonstr = resBytes.decode('utf8').replace("'", '"')
            data = json.loads(jsonstr)
        print(data)
        conn.close()
    except Exception as e:
        print(e)
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

    return data

def face_verify(faceId1, faceId2):
    headers = {
        # Request headers
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': settings.FACE_API_KEY,
    }

    params = urllib.parse.urlencode({
    })

    body = {
        "faceId1": faceId1,
        "faceId2": faceId2
    }

    data = {}

    try:
        conn = http.client.HTTPSConnection(settings.FACE_API_URL)
        conn.request("POST", "/face/v1.0/verify?%s" % params, json.dumps(body), headers)
        response = conn.getresponse()
        if response.status == 200:
            resBytes = response.read()
            jsonstr = resBytes.decode('utf8').replace("'", '"')
            data = json.loads(jsonstr)
        print(data)
        conn.close()
    except Exception as e:
        print("[Errno {0}] {1}".format(e.errno, e.strerror))

    return data
