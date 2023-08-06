import requests
import json

class LangAiClient:
    def __init__(self, token):
        self.apiToken = token

    def analyze(self, text, projectId):
        url = "https://api.lang.ai/v1/analyze"
        headers = {
            "Authorization": "Bearer {}".format(self.token),
            "Content-Type": "application/json",
        }
        body = {
            "text": text,
            "projectId": projectId,
        }
        r = requests.post(url, headers=headers, data=json.dumps(body))
        if r.ok:
            return json.loads(r.text)
        else:
            raise Exception("Got error {}. {}".format(r.status_code, r.text))
