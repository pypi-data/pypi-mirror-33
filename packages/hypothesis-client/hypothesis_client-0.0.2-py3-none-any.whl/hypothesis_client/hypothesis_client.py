import requests

class HypothesisClient(object):

    base_url = 'https://hypothes.is/api'
    annotations = '/search'

    def __init__(self, auth_token):
        self.auth_token = auth_token
        self.session = requests.Session()
        self.session.headers.update({'Authorization': auth_token})

    def annotation(self, **kwargs):
        response = self.session.get('{}{}'.format(self.base_url, self.annotations), params=kwargs)
        return response.json()
