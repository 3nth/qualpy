# encoding: utf-8
"""
core.py

Created by Derek Flenniken on 1/2/2014.
Copyright (c) 2014 Center for Imaging of Neurodegenerative Diseases
"""
from ConfigParser import SafeConfigParser
import csv
import logging
from os import path
from StringIO import StringIO

from bs4 import BeautifulSoup
import requests

QUALTRICS_URL= 'https://new.qualtrics.com/WRAPI/ControlPanel/api.php'
QUALTRICS_API_VERSION = '2.0'

logger = logging.getLogger(__name__)

class Qualtrics(object):
    
    def __init__(self, config=None):
        self._read_config(config)
        self._init_session()
    
    def _read_config(self, config=None):
        parser = SafeConfigParser()

        if config:
            logger.info('Parsing config file %s' % config)
            parser.read(config)
        elif path.exists('qualpy.ini'):
            logger.info('Parsing config file %s' % path.abspath('qualpy.ini'))
            parser.read('qualpy.ini')
        elif path.exists(path.expanduser("~/qualpy.ini")):
            logger.info('Parsing config file %s' % path.abspath(path.expanduser('~/qualpy.ini')))
            parser.read('qualpy.ini')
        else:
            raise Exception("No configuration file found!")

        self._user = parser.get('account', 'user')
        self._token = parser.get('account', 'token')
        self._library_id = parser.get('account', 'library_id')
        
    def _init_session(self):
        payload = { 
            'User': self._user, 
            'Token': self._token, 
            'Version': QUALTRICS_API_VERSION
            }
        self._session = requests.Session()
        self._session.params = payload
        
    def get_surveys(self):
        """Gets all surveys in account
        
        Args:
            None
            
        Returns:
            list: a list of all surveys
        """
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

def count_words():
    q = Qualtrics()
    for survey in q.get_surveys():
        if survey['SurveyStatus'] is not None: # == u'Active':
            questions = get_survey_questions(survey['SurveyID'])
            word_count = 0
            for q in questions:
                question = questions[q]
                q_count = len(question['Text'].split()) if question['Text'] else 0
                word_count += q_count
                for answer in question['Answers']:
                    a_count = len(answer['Description'].split()) if answer['Description'] else 0
                    word_count += a_count
                for choice in question['Choices']:
                    c_count = len(choice['Description'].split()) if choice['Description'] else 0
                    word_count += c_count

            print "%s: %s" % (survey['SurveyName'], word_count)
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4