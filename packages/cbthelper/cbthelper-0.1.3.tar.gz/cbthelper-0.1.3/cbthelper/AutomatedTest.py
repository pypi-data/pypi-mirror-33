from . import globals as G
from .Snapshot import Snapshot
from .Video import Video
import requests, os

class AutomatedTest:
    """
    Helpful representation of a selenium test

    :param testId: the selenium session ID, usually from webdriver
    """
    def __init__(self, testId):
        self.testId = testId
    def setScore(self, score):
        """
        Sets the score for our test in the CBT app

        :param score: should be 'pass', 'fail', or 'unset'. The main module exposes SCORE_PASS, SCORE_FAIL, SCORE_UNSET
        """
        options = {
            'action': 'set_score',
            'score': score
        }
        requests.put(G.api + self.testId, auth=(G.username, G.authkey), data=options)
    def setDescription(self, description):
        """
        Sets the description for our test in the CBT app
        """
        options = {
            'action': 'set_description',
            'description': description
        }
        requests.put(G.api + self.testId, auth=(G.username, G.authkey), data=options)
    def stop(self, score=''):
        # score is optional, will combine setScore and stopTest
        """
        Sends the command to our api to stop the selenium test. Similar to driver.quit()

        :param score: (optional) shortcut for AutomatedTest.setScore
        """
        if score != '':
            self.setScore(score)
        requests.delete(G.api + self.testId, auth=(G.username, G.authkey))
    def takeSnapshot(self, description=''):
        """
        Sends the command to take a snapshot and returns a Snapshot instance

        :param description: (optional) shortcut for Snapshot.setDescription
        :returns: the Snapshot instance for this snapshot
        """
        hash = requests.post(G.api + self.testId + '/snapshots', auth=(G.username, G.authkey)).json()['hash']
        snap = Snapshot(hash, self)
        if description != '':
            snap.setDescription(description)
        return snap
    def getSnapshots(self):
        """
        Gets all snapshots for this test

        :returns: a list of Snapshot objects for this test
        """
        snaps = requests.get(G.api+ self.testId + '/snapshots', auth=(G.username, G.authkey)).json()
        ret = []
        for snap in snaps:
            ret.append(Snapshot(snap['hash'], self))
        return ret
    def saveAllSnapshots(self, directory, prefix='image', useDescription=False):
        """
        Downloads all snapshots for this test into a directory

        :param directory: the directory where the snapshots will be saved
        :param prefix: (optional) defines the prefix used for the filenames
        :param useDescription: (optional) if true, will use the snapshot description instead of the prefix
        """
        snaps = self.getSnapshots()
        self.__makeDirectory(directory)
        for i in range(len(snaps)):
            if useDescription and snaps[i].info['description'] != '':
                img = snaps[i].info['description'] + '.png'
            else:
                img = prefix + str(i) + '.png'
            snaps[i].saveLocally(os.path.join(directory, img))
    def startRecordingVideo(self, description=''):
        """
        Starts recording video for this test

        :param description: shortcut for Video.setDescription
        :returns: the Video instance we started recording
        """
        hash = requests.post(G.api + self.testId + '/videos', auth=(G.username, G.authkey)).json()['hash']
        video = Video(hash, self)
        if description != '':
            video.setDescription(description)
        return video
    def getVideos(self):
        """
        Gets all video recordings for this test

        :returns: a list of Video objects for this test
        """
        videos = requests.get(G.api+ self.testId + '/videos', auth=(G.username, G.authkey)).json()
        ret = []
        for video in videos:
            ret.append(Video(video['hash'], self))
        return ret
    def saveAllVideos(self, directory, prefix='video', useDescription=False):
        """
        Downloads all videos for this test into a directory

        :param directory: the directory where the videos will be saved
        :param prefix: (optional) defines the prefix used for the filenames
        :param useDescription: (optional) if true, will use the video description instead of the prefix
        """
        videos = self.getVideos()
        self.__makeDirectory(directory)
        for i in range(len(videos)):
            if useDescription and videos[i].info['description'] != '':
                vid = videos[i].info['description'] + '.mp4'
            else:
                vid = prefix + str(i) + '.mp4'
            videos[i].saveLocally(os.path.join(directory, vid))
    def __makeDirectory(self, dir):
        if not os.path.exists(dir):
            os.mkdir(dir)
