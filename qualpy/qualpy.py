#!/usr/bin/env python
# encoding: utf-8
"""
qualy.py

Created by Derek Flenniken on 11/1/2013.
Copyright (c) 2013 Center for Imaging of Neurodegenerative Diseases
"""
import argparse
from os import path
import logging
import os
import csv
from StringIO import StringIO

if __name__ == "__main__" and __package__ is None:
    __package__ = "qualpy"
from .core import Qualtrics

from bs4 import BeautifulSoup
from jinja2 import Environment, PackageLoader
import requests

QUALTRICS_URL= 'https://new.qualtrics.com/WRAPI/ControlPanel/api.php'
QUALTRICS_API_VERSION = '2.0'

auth = {
    "qualtrics_user": "",
    "qualtrics_token": '',
    "base_url": "",
    "library_id": ""
}

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger("qualpy")
# create console handler and set level to debug
ch = logging.StreamHandler()
# create formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# add formatter to ch
ch.setFormatter(formatter)
# add ch to logger
logger.addHandler(ch)


def read_auth(authfile):
    f = open(authfile, 'rt')
    auth["qualtrics_user"] = f.readline().rstrip()
    auth["qualtrics_token"] = f.readline().rstrip()
    auth["library_id"] = f.readline().rstrip()
    f.close()

def document(docpath):
    q = Qualtrics(auth['qualtrics_user'], auth['qualtrics_token'])
    
    env = Environment(loader=PackageLoader("qualpy", ""))
    template = env.get_template("DocumentationTemplate.html")
    surveys = q.get_active_surveys()
    for survey in surveys:
        survey['TableName'] = surveyname2tablename(survey['SurveyName'])
        questions = parse_survey_questions(survey)
        survey['Questions'] = questions

    f = open(docpath, 'wt')
    f.write(template.render(surveys=surveys))
    f.close()
    
def parse_survey_questions(survey):
    questions = []

    xml = BeautifulSoup(survey, 'xml')
    for q in xml.Questions.find_all('Question'):
        question = parse_question(q)
        questions.append(question)
    return questions

def parse_question(q):

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

def count_words():
    q = Qualtrics(auth['qualtrics_user'], auth['qualtrics_token'])
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

def download(downloaddir, survey_id=None):
    q = Qualtrics(auth['qualtrics_user'], auth['qualtrics_token'], auth['library_id'])
    
    if not path.exists(downloaddir):
        os.makedirs(downloaddir)

    if survey_id:
        logger.info("Downloading {0}".format(survey_id))
        data = q.get_survey_data(survey['SurveyID'])
        tablename = surveyname2tablename(survey['SurveyName'])
        downloadpath = path.join(downloaddir, tablename + '.csv')
        write_csv(data, downloadpath)
    
    else:
        surveys = q.get_active_surveys()
        for survey in surveys:
            logger.info('Downloading "%s" ...' % survey['SurveyName'])
            data = q.get_survey_data(survey['SurveyID'])
            tablename = surveyname2tablename(survey['SurveyName'])
            downloadpath = path.join(downloaddir, tablename + '.csv')
            write_csv(data, downloadpath)
        panels = q.get_panels()
        for panel in panels:
            logger.info('Downloading "%s" ...' % panel['Name'])
            data = q.get_panel_data(panel['PanelID'])
            tablename = surveyname2tablename(panel['Name'])
            downloadpath = path.join(downloaddir, tablename + '.csv')
            write_csv(data, downloadpath)

def surveyname2tablename(surveyname):
    return surveyname.replace(' ', '').replace('-', '_')

def write_csv(data, filepath):
    f = open(filepath, 'wb')
    writer = csv.writer(f)
    writer.writerows(data)
    f.close()
    
def list():
    q = Qualtrics(auth['qualtrics_user'], auth['qualtrics_token'])
    surveys = q.get_active_surveys()
    for survey in surveys:
        print "{0}: {1}".format(survey['SurveyID'], survey['SurveyName'])

if __name__ == "__main__":
    parser = argparse.ArgumentParser("qualpy")
    parser.add_argument('--auth', action="store")
    parser.add_argument('action', action="store", choices=('document', 'download', 'list'))
    parser.add_argument('dst', action="store")
    args = parser.parse_args()

    read_auth(args.auth)

    if args.action == 'document':
        document(args.dst)
    elif args.action == 'download':
        download(args.dst)
    elif args.action == 'list':
        list()

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4