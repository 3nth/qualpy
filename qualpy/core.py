# encoding: utf-8
"""
core.py

Created by Derek Flenniken on 1/2/2014.
Copyright (c) 2014 Center for Imaging of Neurodegenerative Diseases
"""
import requests

QUALTRICS_URL= 'https://new.qualtrics.com/WRAPI/ControlPanel/api.php'
QUALTRICS_API_VERSION = '2.0'

class Qualtrics(object):
    
    def __init__(self, user, token):
        self._user = user
        self._token = token
        self._init_session()
        
    def _init_session(self):
        payload = { 
            'User': self._user, 
            'Token': self._token, 
            'Version': QUALTRICS_API_VERSION
            }
        self._session = requests.Session()
        self._session.params = payload
        
    def get_surveys(self):
        payload = { 
            'Request': 'getSurveys',
            'Format': 'JSON'
            }
        r = self._session.get(QUALTRICS_URL, params=payload)
        output = r.json()
        return output['Result']['Surveys']
    
    def get_active_surveys(self):
        return [s for s in self.get_surveys() if s['SurveyStatus'] == u'Active' and not "test" in s['SurveyName'].lower()]
    
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4