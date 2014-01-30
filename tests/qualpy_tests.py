from nose.tools import *
from qualpy import qualpy
from qualpy.core import Qualtrics
import json

def setup():
    print "SETUP!"

def teardown():
    print "TEAR DOWN!"

def test_basic():
    print "I RAN!"

def test_get_panels():
    qualpy.read_auth('auth.txt')
    q = Qualtrics(qualpy.auth['qualtrics_user'], qualpy.auth['qualtrics_token'], qualpy.auth['library_id'])
    panels = q.get_panels()
    with open('panels.json', 'wt') as f:
         f.write(str(panels))
         
def test_get_panel():
    qualpy.read_auth('auth.txt')
    q = Qualtrics(qualpy.auth['qualtrics_user'], qualpy.auth['qualtrics_token'], qualpy.auth['library_id'])
    panels = q.get_panels()
    for panel in panels:
        p = q.get_panel_data(panel['PanelID'])
        with open('panel_{0}.json'.format(panel['PanelID']), 'wt') as f:
             f.write(str(p))

def test_get_recipient():
    qualpy.read_auth('auth.txt')
    q = Qualtrics(qualpy.auth['qualtrics_user'], qualpy.auth['qualtrics_token'], qualpy.auth['library_id'])
    panels = q.get_recipient('MLRP_0AjeSXB0FvvIjwp')
    with open('recipient.json', 'wt') as f:
         f.write(str(panels))

def test_create_distribution():
    qualpy.read_auth('auth.txt')
    q = Qualtrics(qualpy.auth['qualtrics_user'], qualpy.auth['qualtrics_token'], qualpy.auth['library_id'])
    panels = q.create_distribution('ML_d6EIoXwwBaPGVdX', 'SV_cD5WTyytP5oetcp')
    with open('create_distribution.json', 'wt') as f:
         f.write(str(panels))

    