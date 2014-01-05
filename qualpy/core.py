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

    def get_survey_questions(self, survey_id):
        details = self.get_survey(survey_id)
        questions = []

        survey = BeautifulSoup(details, 'xml')
        for q in survey.Questions.find_all('Question'):
            question = self.parse_question(q)
            questions.append(question)
        return questions

    def parse_question(self, q):

        choices = []
        if q.Choices:
            for choice in q.Choices.find_all('Choice'):
                choices.append({
                    "ID": choice['ID'], 
                    "Recode": choice['Recode'], 
                    "Description": choice.Description
                })

        answers = []
        if q.Answers:
            for answer in q.Answers.find_all('Answer'):
                answers.append({
                    "ID": answer['ID'], 
                    "Recode": answer['Recode'], 
                    "Description": answer.Description
                })
            
        return {
            "ID": q['QuestionID'], 
            "Type": q.Type, 
            "Text": q.QuestionText, 
            "Choices": choices, 
            "Answers": answers
        }

    def get_data(self, survey_id):
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

    def _clean_header(self, header1, header2):
        logger.debug("Header1: %s" % len(header1))
        logger.debug("Header2: %s" % len(header2))
        header = [h1 if h1.startswith('QID') else h2 for h1, h2 in zip(header1,  header2)]
        logger.debug("Header: %s" % len(header))
        return header
        
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4