from . import globals as G
import requests

class CapsBuilder:
    """
    Builder for generating selenium capabilities

    All of the with... methods return self for method chaining
    """
    def __init__(self):
        self.capsData = requests.get(G.api + 'browsers').json()
        self.platform = None
        self.browser = None
        self.width = None
        self.height = None
        self.name = None
        self.version = None
        self.recordVideo = None
        self.recordNetwork = None
    def withPlatform(self, platform):
        """
        Sets the platform (OS) the user wants to use. Uses fuzzy string comparison to find best match

        :param platform: a string specifying the platform (eg. Windows 7, Mac 10.13)
        """
        self.platform = platform
        return self
    def withBrowser(self, browser):
        """
        Sets the browser the user wants to use. Uses fuzzy string comparison to find best match

        :param browser: as string specifying the browser (eg. Edge 17, Chrome 55x64)
        """
        self.browser = browser
        return self
    def withResolution(self, width, height):
        """
        Sets the screen size for the test
        """
        self.width = width
        self.height = height
        return self
    def withName(self, name):
        """
        Sets the name that will appear in the web app
        """
        self.name = name
        return self
    def withBuild(self, build):
        """
        Sets the build name in the web app
        """
        # cant be build because of method below
        self.version = build
        return self
    def withRecordVideo(self, bool):
        """
        Records a video for the length of the test
        """
        self.recordVideo = bool
        return self
    def withRecordNetwork(self, bool):
        """
        Records network traffice for the length of the test
        """
        self.recordNetwork = bool
        return self
    def build(self):
        """
        Used to generate the capabilites using any options the user specifies

        :returns: a python dict object that can be passed to the selenium webdriver
        """
        return self.__choose()
    def __bestOption(self, options, target):
        target = target.lower()
        for option in options:
            name = option['name'].lower()
            apiName = option['api_name'].lower()
            if target == name or target == apiName:
                return option
        return None
    def __bestBrowserNoPlatform(self, target):
        target = target.lower()
        for platform in self.capsData:
            for browser in platform['browsers']:
                name = browser['name'].lower()
                apiName = browser['api_name'].lower()
                if target == name or target == apiName:
                    return browser
        return None
    def __choose(self):
        data = self.capsData
        caps = {
            'username': G.username,
            'password': G.authkey
        }
        platform = None
        browser = None
        if self.platform:
            platform = self.__bestOption(data, self.platform)
            if platform != None:
                caps.update(platform['caps'])
        if self.browser:
            if platform:
                browser = self.__bestOption(platform['browsers'], self.browser)
            else:
                browser = self.__bestBrowserNoPlatform(self.browser)
            if browser != None:
                caps.update(browser['caps'])
        if self.width and self.height:
            caps['screenResolution'] = str(self.width) + 'x' + str(self.height)
        if self.name:
            caps['name'] = self.name
        if self.version:
            caps['build'] = self.version
        if self.recordVideo:
            caps['record_video'] = self.recordVideo
        if self.recordNetwork:
            caps['record_network'] = self.recordNetwork
        return caps
