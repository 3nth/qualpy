from __future__ import print_function
import argparse
import logging
from os import path

from bs4 import BeautifulSoup
from cliff.command import Command
from jinja2 import Environment, PackageLoader

from .core import Qualtrics

import HTMLParser
html_parser = HTMLParser.HTMLParser()

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

def surveyname2tablename(surveyname):
    return surveyname.replace(' ', '').replace('-', '_')


class Document(Command):
    "Generate html documentation of active surveys."
    log = logging.getLogger(__name__)

    
    def get_parser(self, prog_name):
        parser = argparse.ArgumentParser() #super(Command, self).get_parser(prog_name)
        parser.add_argument('--out', action='store', help='Path to output file.')
        parser.add_argument('--survey', action='append')
        return parser
    
    def take_action(self, parsed_args):
        q = Qualtrics(self.app_args.config)
    
        env = Environment(loader=PackageLoader("qualpy", ""))
        template = env.get_template("DocumentationTemplate.html")


        surveys = []
        for id in parsed_args.survey:
            survey = self.document_survey(q, id)
            surveys.append(survey)

        # surveys = q.get_active_surveys()
        # for s in surveys:
        #     self.log.info('Now documenting: %s' % s['SurveyName'])
        #     s['TableName'] = surveyname2tablename(s['SurveyName'])
        #     survey = q.get_survey(s['SurveyID'])
        #     questions = self.parse_survey_questions(survey)
        #     s['Questions'] = questions

        f = open(parsed_args.out, 'wb')
        rendered = template.render(surveys=surveys).encode('utf-8')
        f.write(rendered)
        f.close()

    def document_survey(self, q, survey_id):
        if isinstance(survey_id, str):
            surveys = q.get_active_surveys()
            s = [s for s in surveys if s['SurveyID'] == survey_id][0]
        self.log.info("Documenting {0}".format(s['SurveyName']))
        s['TableName'] = surveyname2tablename(s['SurveyName'])
        survey = q.get_survey(s['SurveyID'])
        questions = self.parse_survey_questions(survey)
        s['Questions'] = questions
        return s

    def parse_survey_questions(self, survey):
        questions = []

        xml = BeautifulSoup(survey, 'xml')
        for q in xml.Questions.find_all('Question'):

            question = self.parse_question(q)
            if question:
                questions.extend(question)
        return questions

    def parse_question(self, q):
        t = q.Type.string
        selector = q.Selector.string
        self.log.info("Parsing " + q['QuestionID'] + "[" + t + ": " + selector + "]")
        self.log.debug(q.prettify())
        if q.QuestionText.string == "Click to write the question text" or t == "DB":
            return None

        if t in ["Matrix", "TE", "Slider", "HotSpot"]:
            return self.parse_matrix(q, selector)
        if t == "MC" and selector == "MAVR":
            return self.parse_matrix(q, selector)
        return self.parse_mc(q)


    def parse_mc(self, q):
        questions = []
        choices = []
        if q.Choices:
            for choice in q.Choices.find_all('Choice'):
                choices.append({
                    "ID": choice['ID'],
                    "Recode": choice['Recode'],
                    "Description": choice.Description.text.encode()
                })

        answers = []
        if q.Answers:
            for answer in q.Answers.find_all('Answer'):
                answers.append({
                    "ID": answer['ID'],
                    "Recode": answer['Recode'],
                    "Description": answer.Description.text.encode()
                })

        questions.append( {
            "ID": q['QuestionID'],
            "Type": q.Type,
            "Text": self.html_decode(q.QuestionText.text.encode()),
            "Choices": choices,
            "Answers": answers
        })
        return questions

    def html_decode(self, s):
        """
        Returns the ASCII decoded version of the given HTML string. This does
        NOT remove normal HTML tags like <p>.
        """
        htmlCodes = (
                ("'", '&#39;'),
                ('"', '&quot;'),
                ('>', '&gt;'),
                ('<', '&lt;'),
                ('&', '&amp;')
            )
        for code in htmlCodes:
            s = s.replace(code[1], code[0])
        return s

    def parse_matrix(self, q, selector):
        questions = []

        qid = q['QuestionID']
        ctags = q.find("ChoiceExportTags")
        tag = q.find("ExportTag")
        if ctags != None and tag != None:
            qid = tag.string.encode()
        
        qtext = self.html_decode(q.QuestionText.text.encode())
        answers = []

        if not q.Answers and len(q.Choices.find_all('Choice')) == 0:

            question = {
                "ID": qid,
                 "Text": qtext
            }
            questions.append(question)

        if q.Answers:
            for answer in q.Answers.find_all('Answer'):
                answers.append({
                    "ID": answer['ID'],
                    "Recode": answer['Recode'],
                    "Description": answer.Description
                })

        if q.Choices:
            for choice in q.Choices.find_all('Choice'):
                cid =  qid + "_" + choice['Recode']
                
                if selector == "Likert":
                    question = {
                        "ID": cid,
                        "Text": qtext + '\n' + choice.Description.string,
                        "Choices": answers
                    }

                    questions.append(question)

                    if choice.has_attr('TextEntry'):
                        question = {
                            "ID": cid + "_TEXT",
                            "Text": qtext + '\n' + choice.Description.string,
                            "Choices": []
                        }
                        questions.append(question)
                else:
                    if choice.has_attr('TextEntry'):
                        question = {
                            "ID": cid + "_TEXT",
                            "Text": qtext + '\n' + choice.Description.string,
                            "Choices": []
                        }
                    
                    else:
                        question = {
                            "ID": cid,
                            "Text": qtext + '\n' + choice.Description.string,
                            "Choices": answers
                        }
                
                    questions.append(question)





        return questions