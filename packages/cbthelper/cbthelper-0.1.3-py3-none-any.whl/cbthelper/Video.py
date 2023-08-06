from . import globals as G
import requests, sys, time, os, threading

class Video:
    """
    Represents a video recording for a selenium test

    :param hash: the hash for this video, returned by rest api when starting a recording
    :param test: an AutomatedTest object that represents a test currently running
    """
    def __init__(self, hash, test):
        self.hash = hash
        self.testId = test.testId
        self.getInfo()
    def getInfo(self):
        """
        Calls out to api to get updated info for this video

        :returns: a python dict object with all of the info for this video
        """
        self.info = requests.get(G.api + self.testId + '/videos/' + self.hash, auth=(G.username, G.authkey)).json()
        return self.info
    def stopRecording(self):
        """
        Sends the command to stop a video recording
        """
        requests.delete(G.api + self.testId + '/videos/' + self.hash, auth=(G.username, G.authkey))
    def setDescription(self, description):
        """
        Sets the description for this video
        """
        url = G.api + self.testId + '/videos/' + self.hash
        self.info = requests.put(url, auth=(G.username, G.authkey), data={'description':description})
    def saveLocally(self, location):
        """
        Async method to download this video to the location given. Recording will be stopped if active.

        :param location: a string with the location and filename for the video. Should have a .mp4 extension
        """
        t = threading.Thread(target=Video.__saveLocally, args=(self, location))
        t.start()
    def __saveLocally(self, location):
        self.getInfo()
        timeout = 20
        iteration = 1
        #while (iteration < timeout) and (self.info['is_finished'] == False):
        #    time.sleep(2)
        #    iteration += 1
        #    self.getInfo()
        if self.info['is_finished'] == False:
            self.stopRecording
        #iteration = 1
        url = self.info['video']
        r = requests.get(url, stream=True)
        while (iteration < timeout) and (r.status_code != 200):
            time.sleep(2)
            r = requests.get(url, stream=True)
            iteration += 1
        if iteration < timeout:
            path = os.path.split(location)[0]
            if not os.path.exists(path):
                os.mkdir(path)
            with open(location, 'wb') as f:
                for chunk in r.iter_content(chunk_size=128):
                    f.write(chunk)
