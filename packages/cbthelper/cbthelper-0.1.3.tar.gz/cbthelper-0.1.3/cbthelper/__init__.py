import requests

from . import globals as G
from .CapsBuilder import CapsBuilder
from .TestHistoryBuilder import TestHistoryBuilder
from .AutomatedTest import AutomatedTest
from .Snapshot import Snapshot
from .Video import Video

SCORE_PASS = 'pass'
SCORE_FAIL = 'fail'
SCORE_UNSET = 'unset'
hub = "http://hub.crossbrowsertesting.com:80/wd/hub"

def getCapsBuilder():
    """
    Used to get the selenium capability builder

    Generating the CapsBuilder pulls in a large amount of data, so user should not call the constrcutor manually
    """
    G.capsBuilder = G.capsBuilder or CapsBuilder()
    return G.capsBuilder

def login(username, authkey):
    """
    Sets the username and authkey used to make the HTTP requests
    """
    G.username = username
    G.authkey = authkey

def getTestHistoryBuilder():
    """
    Used to get the TestHistoryBuilder

    Can also just call the constructor. Method created to match getCapsBuilder()
    """
    return TestHistoryBuilder()

def getTestHistory(options):
    """
    Returns a python dictionary with the test history, filtering based on the options given.

    :param options: a python dictionary created by the TestHistoryBuilder
    """
    return requests.get(G.api, auth=(G.username, G.authkey), data=options).json()

def getTestFromId(sessid):
    """
    Creates an automated test from the selenium session id

    :param sessid: string for the seleneium session/test id. Should come from WebDriver
    """
    return AutomatedTest(sessid)
