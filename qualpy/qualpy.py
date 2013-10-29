#!/usr/bin/env python
import urllib2
import json
import xml.etree.ElementTree as ET
from jinja2 import Environment, PackageLoader
import argparse
from os import path
import logging
import os
import csv
from StringIO import StringIO


qualtrics_url= 'https://new.qualtrics.com/WRAPI/ControlPanel/api.php'
qualtrics_api_version = '2.0'

auth = {
    "qualtrics_user": "",
    "qualrics_token": '',
    "base_url": ""
}


logger = logging.getLogger("qualpy")
logger.setLevel(logging.DEBUG)
# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
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
    f.close()
    auth["base_url"] = '{0}?User={1}&Token={2}&Version={3}'.format(
        qualtrics_url,
        urllib2.quote(auth["qualtrics_user"]),
        urllib2.quote(auth["qualtrics_token"]),
        qualtrics_api_version
    )
    logging.debug(auth["base_url"])

def get_surveys():
    url = '{0}&Request=getSurveys&Format=JSON'.format(auth["base_url"])
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    output = json.loads(response.read())
    return output['Result']['Surveys']

def get_active_surveys():
    return [s for s in get_surveys() if s['SurveyStatus'] == u'Active' and not "test" in s['SurveyName'].lower()]

def get_survey(survey_id):
    logger.debug("fetching survey '%s'" % survey_id)
    url = '{0}&Request=getSurvey&SurveyID={1}'.format(auth["base_url"], urllib2.quote(survey_id))
    logger.debug(url)
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    survey = response.read()
    return survey


def get_survey_questions(survey_id):
    details = get_survey(survey_id)
    tree = ET.fromstring(details)
    questions = []
    for node in tree.findall('.//Questions/Question'):
        question = parse_question(node)
        questions.append(question)

    return questions


def parse_question(node):
    q_id = node.attrib.get('QuestionID')
    q_text = node.findtext('./QuestionText')
    q_type = node.findtext('./Type')
    q_choices = []
    q_answers = []

    for choice in node.findall('./Choices/Choice'):
        c_id = choice.attrib.get('ID')
        c_recode = choice.attrib.get('Recode')
        c_description = choice.findtext('./Description')
        q_choices.append({"ID": c_id, "Recode": c_recode, "Description": c_description})

    for answer in node.findall('./Answers/Answer'):
        a_id = answer.attrib.get('ID')
        a_recode = answer.attrib.get('Recode')
        a_description = answer.findtext('./Description')
        q_answers.append({"ID": a_id, "Recode": a_recode, "Description": a_description})
    return {"ID": q_id, "Type": q_type, "Text": q_text, "Choices": q_choices, "Answers": q_answers}

def get_data(survey_id):
    url = '{0}&Request=getLegacyResponseData&SurveyID={1}&Format=CSV&ExportQuestionIDs=1'.format(auth["base_url"], urllib2.quote(survey_id))
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    rread = response.read()
    return rread

def write_csv(data, filepath):
    reader = csv.reader(StringIO(data))
    rows = [row for row in reader]
    header1 = rows[0]
    header2 = rows[1]
    data = rows[2:]
    header = clean_header(header1, header2)
    data.insert(0, header)

    f = open(filepath, 'wb')
    writer = csv.writer(f)
    writer.writerows(data)
    f.close()

def clean_header(header1, header2):
    logging.debug("Header1: %s" % len(header1))
    logging.debug("Header2: %s" % len(header2))
    return [h1 if h1.startswith('QID') else h2 for h1, h2 in zip(header1,  header2)]


def count_words():
    for survey in get_surveys():
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


def surveyname2tablename(surveyname):
    return surveyname.replace(' ', '').replace('-', '_')


def document(docpath):
    env = Environment(loader=PackageLoader("qualpy", ""))
    template = env.get_template("DocumentationTemplate.html")
    surveys = get_active_surveys()
    for survey in surveys:
        survey['TableName'] = surveyname2tablename(survey['SurveyName'])
        questions = get_survey_questions(survey['SurveyID'])
        survey['Questions'] = questions

    f = open(docpath, 'wt')
    f.write(template.render(surveys=surveys))
    f.close()

def download(downloaddir):
    if not path.exists(downloaddir):
        os.makedirs(downloaddir)

    surveys = get_active_surveys()
    for survey in surveys:
        logger.info('Downloading "%s" ...' % survey['SurveyName'])
        data = get_data(survey['SurveyID'])
        tablename = surveyname2tablename(survey['SurveyName'])
        downloadpath = path.join(downloaddir, tablename + '.csv')
        write_csv(data, downloadpath)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("qualpy")
    parser.add_argument('--auth', action="store")
    parser.add_argument('action', action="store", choices=('document', 'download'))
    parser.add_argument('dst', action="store")
    args = parser.parse_args()

    read_auth(args.auth)

    if args.action == 'document':
        document(args.dst)
    elif args.action == 'download':
        download(args.dst)