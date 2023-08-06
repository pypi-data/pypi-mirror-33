from . import globals as G
import requests, sys, time, os, threading

class Snapshot:
    """
    Represents a snapshot for selenium tests

    :param hash: the hash for this image, returned by rest api when taking a screenshot
    :param test: an AutomatedTest object that represents a test currently running
    """
    def __init__(self, hash, test):
        self.hash = hash
        self.testId = test.testId
        self.getInfo()
    def getInfo(self):
        """
        Calls out to api to get updated info for this snapshot

        :returns: a python dict object with all of the info for this Snapshot
        """
        self.info = requests.get(G.api + self.testId + '/snapshots/' + self.hash, auth=(G.username, G.authkey)).json()
        return self.info
    def setDescription(self, description):
        """
        Sets the description for this snapshot
        """
        url = G.api + self.testId + '/snapshots/' + self.hash
        self.info = requests.put(url, auth=(G.username, G.authkey), data={'description':description})
    def saveLocally(self, location):
        """
        Async method to download this snapshot to the location given

        :param location: a string with the location and filename for the image. Should have a .png extension
        """
        t = threading.Thread(target=Snapshot.__saveSnapshot, args=(self, location))
        t.start()
    def __saveSnapshot(self, location):
        url = self.getInfo()['image']
        r = requests.get(url, stream=True)
        timeout = 15
        iteration = 1
        while (iteration < timeout) and (r.status_code != 200):
            r = requests.get(url, stream=True)
            iteration += 1
            time.sleep(1)
        if iteration < timeout:
            path = os.path.split(location)[0]
            if not os.path.exists(path):
                os.mkdir(path)
            with open(location, 'wb') as f:
                for chunk in r.iter_content(chunk_size=128):
                    f.write(chunk)
