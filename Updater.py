from Resolvers import PathResolver
from Driver import Driver

class DriverUpdater:
    def __init__(self):
        self._get_driver()

    def _get_driver(self):
        download_pr = PathResolver(['download'], mkdir=True)
        self.driver = Driver(
            download_directory=download_pr.path()
        )