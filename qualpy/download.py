import argparse
import csv
import logging
import os
from os import path

from cliff.command import Command

from .core import Qualtrics

   
class Download(Command):
    "Download survey data."
    
    log = logging.getLogger(__name__)
    
    def get_parser(self, prog_name):
        parser = argparse.ArgumentParser()
        parser.add_argument('--out', action='store', help='Path to output directory.')
        parser.add_argument('--panel', action='store')
        parser.add_argument('--survey', action='store')
        return parser
    
    def take_action(self, parsed_args):
        
        self.q = Qualtrics(self.app_args.auth)
        self.out = parsed_args.out
        
        if not path.exists(parsed_args.out):
            os.makedirs(parsed_args.out)

        if parsed_args.survey == 'all':
            self.download_surveys()
        elif parsed_args.survey:
            self.download_survey(parsed_args.survey)
            
        if parsed_args.panel == 'all':
            self.download_panels()
        elif parsed_args.panel:
            self.download_panel(parsed_args.panel)

    def download_surveys(self):
        surveys = self.q.get_active_surveys()
        for survey in surveys:
            self.download_survey(survey)
    
    def download_survey(self, survey):
        if isinstance(survey, str):
            surveys = self.q.get_active_surveys()
            survey = [s for s in surveys if s['SurveyID'] == survey][0]
        self.log.info("Downloading {0}".format(survey['SurveyName']))
        data = self.q.get_survey_data(survey['SurveyID'])
        tablename = survey2filename(survey['SurveyName'])
        downloadpath = path.join(self.out, tablename + '.csv')
        write_csv(data, downloadpath)
                        
    def download_panels(self):
        panels = self.q.get_panels()
        for panel in panels:
            self.download_panel(panel)
    
    def download_panel(self, panel):
        if isinstance(panel, str):
            panels = self.q.get_panels()
            panel = [p for p in panels if p['PanelID'] == panel][0]
        self.log.info('Downloading "%s" ...' % panel['Name'])
        data = self.q.get_panel_data(panel['PanelID'])
        tablename = survey2filename(panel['Name'])
        downloadpath = path.join(self.out, tablename + '.csv')
        write_csv(data, downloadpath)


def survey2filename(survey_name):
    return survey_name.replace(' ', '').replace('-', '_')


def write_csv(data, filepath):
    f = open(filepath, 'wb')
    writer = csv.writer(f)
    writer.writerows(data)
    f.close()