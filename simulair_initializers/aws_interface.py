import requests

class instanceInfoGetters:
    params_url = "http://169.254.169.254/latest/meta-data/"
    def __init__(self):
        self.id = "123"

    @staticmethod
    def getParams():
        return requests.get(url = instanceInfoGetters.params_url)
