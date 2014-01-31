import argparse
import logging
from os import path

from bs4 import BeautifulSoup
from cliff.command import Command
from jinja2 import Environment, PackageLoader

from .core import Qualtrics

def surveyname2tablename(surveyname):
    return surveyname.replace(' ', '').replace('-', '_')
    
class Document(Command):
    "Generate html documentation of active surveys."
    log = logging.getLogger(__name__)
    
    
    def get_parser(self, prog_name):
        parser = argparse.ArgumentParser() #super(Command, self).get_parser(prog_name)
        parser.add_argument('--out', action='store', help='Path to output file.')
        return parser
    
    
    def take_action(self, parsed_args):
        q = Qualtrics(self.app_args.auth)
    
        env = Environment(loader=PackageLoader("qualpy", ""))
        template = env.get_template("DocumentationTemplate.html")
        surveys = q.get_active_surveys()
        for s in surveys:
            self.log.info('Now documenting: %s' % s['SurveyName'])
            s['TableName'] = surveyname2tablename(s['SurveyName'])
            survey = q.get_survey(s['SurveyID'])
            questions = self.parse_survey_questions(survey)
            s['Questions'] = questions

        f = open(parsed_args.out, 'wt')
        f.write(template.render(surveys=surveys))
        f.close()

    def parse_survey_questions(self, survey):
        questions = []

        xml = BeautifulSoup(survey, 'xml')
        for q in xml.Questions.find_all('Question'):
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