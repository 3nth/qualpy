import json
import os
from os import path
import pprint

from nose.tools import *

from qualpy import Qualtrics

class test_qualtrics(object):
    
    def __init__(self):
        self.q = None
        self.pp = pprint.PrettyPrinter()
    
    def setup(self):
        self.q = Qualtrics('auth.txt')
        if not path.exists('tests_out'):
            os.makedirs('tests_out')

    def teardown(self):
        pass

    def test_get_surveys(self):
        surveys = self.q.get_surveys()
        with open('tests_out/surveys.py', 'wt') as f:
            f.write(self.pp.pformat(surveys))
    
    def test_get_survey(self):
        survey_id = self.q.get_surveys()[0]['SurveyID']
        survey = self.q.get_survey(survey_id)
        with open('tests_out/survey.xml', 'wt') as f:
            f.write(str(survey))
    
    def test_get_panels(self):
        panels = self.q.get_panels()
        with open('tests_out/panels.json', 'wt') as f:
             f.write(str(panels))
         
    def test_get_panel(self):
        panels = self.q.get_panels()
        for panel in panels:
            p = self.q.get_panel_data(panel['PanelID'])
            with open('tests_out/panel_{0}.json'.format(panel['PanelID']), 'wt') as f:
                 f.write(str(p))

    def test_get_recipient(self):
        panels = self.q.get_recipient('MLRP_0AjeSXB0FvvIjwp')
        with open('tests_out/recipient.json', 'wt') as f:
             f.write(str(panels))

    def test_create_distribution(self):
        pass
        panels = self.q.create_distribution('ML_d6EIoXwwBaPGVdX', 'SV_cD5WTyytP5oetcp')
        with open('tests_out/create_distribution.json', 'wt') as f:
             f.write(str(panels))

    