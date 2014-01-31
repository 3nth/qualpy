import logging
import sys

from cliff.app import App
from cliff.commandmanager import CommandManager
from cliff.lister import Lister

from .core import Qualtrics


class QualpyApp(App):

    log = logging.getLogger(__name__)

    def __init__(self):
        super(QualpyApp, self).__init__(
            description='qualpy',
            version='0.1',
            command_manager=CommandManager('qualpy'),
            )

    def build_option_parser(self, description, version, argparse_kwargs=None):
        parser = super(QualpyApp, self).build_option_parser(description, version, argparse_kwargs)
        parser.add_argument('--config', action='store', default=None, help='Path to auth file.')
        return parser
        
    def initialize_app(self, argv):
        self.log.debug('initialize_app')

    def prepare_to_run_command(self, cmd):
        self.log.debug('prepare_to_run_command %s', cmd.__class__.__name__)

    def clean_up(self, cmd, result, err):
        self.log.debug('clean_up %s', cmd.__class__.__name__)
        if err:
            self.log.debug('got an error: %s', err)


class List(Lister):
    "List all surveys."

    log = logging.getLogger(__name__)
 
    def take_action(self, parsed_args):
        q = Qualtrics(self.app_args.config)
        surveys = q.get_surveys()
        columns = ('ID',
                    'Name',
                    'Status'
                    )
        data = ((s['SurveyID'], s['SurveyName'], s['SurveyStatus']) for s in surveys)
        return (columns, data)


def main(argv=sys.argv[1:]):
    myapp = QualpyApp()
    return myapp.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))