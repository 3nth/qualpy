# encoding: utf-8
"""
core.py

Created by Derek Flenniken on 1/2/2014.
Copyright (c) 2014 Center for Imaging of Neurodegenerative Diseases
"""
from StringIO import StringIO
import csv
import logging

import requests
from bs4 import BeautifulSoup

QUALTRICS_URL= 'https://new.qualtrics.com/WRAPI/ControlPanel/api.php'
QUALTRICS_API_VERSION = '2.0'

logger = logging.getLogger(__name__)

class Qualtrics(object):
    
    def __init__(self, user, token, library_id):
        self._user = user
        self._token = token
        self._library_id = library_id
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
    
    def create_distribution(self, panel_id, survey_id):
        payload = { 
            'Request': 'createDistribution',
            'Format': 'JSON',
            'PanelID': panel_id,
            'LibraryID': self._library_id,
            'SurveyID': survey_id
            }
        r = self._session.get(QUALTRICS_URL, params=payload)
        return r
        
    def get_survey(self, survey_id):
        logger.debug("fetching survey '%s'" % survey_id)
        payload = { 
            'Request': 'getSurvey',
            'SurveyID': survey_id
            }
        r = self._session.get(QUALTRICS_URL, params=payload)
        logger.debug(r.url)
        logger.debug(r.status_code)
        r.raise_for_status()
        survey = r.content
        return survey

    def get_survey_data(self, survey_id):
        """
        """
        payload = { 
            'Request': 'getLegacyResponseData',
            'Format': 'CSV',
            'ExportQuestionIDs': 1,
            'SurveyID': survey_id
            }
        r = self._session.get(QUALTRICS_URL, params=payload)
        data = r.content
    
        reader = csv.reader(StringIO(data))
        rows = [row for row in reader]
        header1 = rows[0]
        header2 = rows[1]
        data = rows[2:]
        header = self._clean_header(header1, header2)
        data.insert(0, header)

        return data

    def get_panels(self):
        payload = { 
            'Request': 'getPanels',
            'Format': 'JSON',
            'LibraryID': self._library_id
            }
        r = self._session.get(QUALTRICS_URL, params=payload)
        output = r.json()
        return output['Result']['Panels']
        
    def get_panel_data(self, panel_id):
        payload = { 
            'Request': 'getPanel',
            'Format': 'CSV',
            'LibraryID': self._library_id,
            'PanelID': panel_id
            }
        r = self._session.get(QUALTRICS_URL, params=payload)
        reader = csv.reader(StringIO(r.content))
        rows = [row for row in reader]
        return rows
        
    def _clean_header(self, header1, header2):
        logger.debug("Header1: %s" % len(header1))
        logger.debug("Header2: %s" % len(header2))
        header = [h1 if h1.startswith('QID') else h2 for h1, h2 in zip(header1,  header2)]
        logger.debug("Header: %s" % len(header))
        return header
    
    def get_recipient(self, recipient_id):
        payload = { 
            'Request': 'getRecipient',
            'Format': 'JSON',
            'LibraryID': self._library_id,
            'RecipientID': recipient_id
            }
        r = self._session.get(QUALTRICS_URL, params=payload)
        return r.content
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4