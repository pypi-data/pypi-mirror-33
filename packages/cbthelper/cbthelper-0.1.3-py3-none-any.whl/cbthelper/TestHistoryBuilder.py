class TestHistoryBuilder:
    """
    Builder to generate options for getting test history

    All of the with... methods return self for method chaining
    """
    def __init__(self):
        self.options = {}
    def withLimit(self, limit):
        """
        Sets the max number of tests to return
        """
        self.options['num'] = limit
        return self
    def withActive(self, active):
        """
        If set, will only return active or inactive tests

        :param active: boolean value
        """
        self.options['active'] = active
        return self
    def withName(self, name):
        """
        Will only return tests that match the name given
        """
        self.options['name'] = name
        return self
    def withBuild(self, build):
        """
        Will only return tests that match the build given
        """
        self.options['build ']= build
        return self
    def withUrl(self, url):
        """
        Will only return tests that navigate to the same url
        """
        self.options['url'] = url
        return self
    def withScore(self, score):
        """
        Will only return tests with the score specified ('pass', 'fail', 'unset')

        The library contains helpful enums cbthelper.(SCORE_PASS, SCORE_FAIL, SCORE_UNSET)
        """
        self.options['score'] = score
        return self
    def withPlatform(self, platform):
        """
        Will only return tests with the same platform (OS)

        :param platform: string with the platform (eg. 'Windows 10', 'Mac OS 10.13')
        """
        self.options['platform'] = platform
        return self
    def withPlatformType(self, platformType):
        """
        Will only return tests with the same platformType (OS Family)

        :param platformType: string with the platform type (eg. 'Windows', 'Mac', 'Android')
        """
        self.options['platformType'] = platformType
        return self
    def withBrowser(self, browser):
        """
        Will only return tests that used the same browser

        :param browser: a string with the browser name and version: (eg. Chrome 65)
        """
        self.options['browser'] = browser
        return self
    def withBrowserType(self, browserType):
        """
        Will only return tests that used the same browser type

        :param browserType: a string representing the browser family (eg. 'Chrome', 'Edge', 'Safari')
        """
        self.options['browserType'] = browserType
        return self
    def withResolution(self, resolution):
        """
        Will only return tests that used the same resolution

        :param resolution: a string with the form 'WIDTHxHEIGHT' (eg. '1024x768')
        """
        self.options['resolution']= resolution
        return self
    def withStartDate(self, startDate):
        self.options['startDate'] = startDate
        return self
    def withEndDate(self, endDate):
        self.options['endDate'] = endDate
        return self
    def build(self):
        """
        Generates the test history options

        :returns: a python dict to pass to cbthelper.getTestHistory()
        """
        return self.options
