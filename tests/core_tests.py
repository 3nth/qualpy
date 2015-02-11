import os
from os import path
import pprint
import csv

from qualpy.core import Qualtrics

here = path.dirname(__file__)
output = path.join(here, '..', 'tests_out')

class test_qualtrics(object):

    def __init__(self):
        self.q = None
        self.pp = pprint.PrettyPrinter()

    def setup(self):
        self.q = Qualtrics()
        if not path.exists(output):
            os.makedirs(output)

    def teardown(self):
        pass

    def test_get_surveys(self):
        surveys = self.q.get_surveys()
        with open(path.join(output, 'surveys.py'), 'wt') as f:
            f.write(self.pp.pformat(surveys))

    def test_get_survey(self):
        survey_id = self.q.get_surveys()[0]['SurveyID']
        survey = self.q.get_survey('SV_bODTUvp9Bn7s3eR')
        with open(path.join(output, 'survey.xml'), 'wt') as f:
            f.write(str(survey))

    def test_get_survey_data(self):
        survey_id = self.q.get_surveys()[0]['SurveyID']
        data = self.q.get_survey_data('SV_bODTUvp9Bn7s3eR')
        self.write_csv(data, path.join(output, 'survey.csv'))


    def test_get_panels(self):
        panels = self.q.get_panels()
        with open(path.join(output, 'panels.json'), 'wt') as f:
            f.write(str(panels))

    def test_get_panel(self):
        panels = self.q.get_panels()
        for panel in panels:
            p = self.q.get_panel_data(panel['PanelID'])
            with open(path.join(output, 'panel_{0}.json'.format(panel['PanelID'])), 'wt') as f:
                f.write(str(p))

    def test_get_recipient(self):
        panel = self.q.get_panels()[0]
        id = self.q.get_panel_data(panel['PanelID'])[1][0]
        recipient = self.q.get_recipient(id)
        with open(path.join(output, 'recipient.json'), 'wt') as f:
            f.write(str(recipient))

    def test_create_distribution(self):
        pass
        panels = self.q.create_distribution('', '')
        with open(path.join(output, 'create_distribution.json'), 'wt') as f:
            f.write(str(panels))

    def write_csv(self, data, filepath):
        f = open(filepath, 'wb')
        writer = csv.writer(f)
        writer.writerows(data)
        f.close()
