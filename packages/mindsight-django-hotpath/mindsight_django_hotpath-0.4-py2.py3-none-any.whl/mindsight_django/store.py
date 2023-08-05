import json
import requests


class SampleStore(object):
    def __init__(self, server_url, project, environment, send_after=100, send_timeout=0.05):
        self.server_url = server_url
        self.send_after = send_after
        self.send_timeout = send_timeout
        self.params = {'project': project, 'environment': environment}
        self._samples = {}
        self._count = 0


    def record(self, fn_name, ncalls=1):
        if fn_name not in self._samples:
            self._samples[fn_name] = ncalls
        else:
            self._samples[fn_name] += ncalls

        self._count += 1
        if self._count > self.send_after:
            self.send_samples()


    def send_samples(self):
        if len(self._samples) == 0:
            return

        try:
            url = "{}/samples/".format(self.server_url)
            h = {"Content-type": "application/json"}
            data = json.dumps(self._samples)
            r = requests.post(url, params=self.params, headers=h, data=data, timeout=self.send_timeout)
            r.raise_for_status()
            self._samples = {}
            self._count = 0
        except requests.exceptions.RequestException as e:
            print(e)
