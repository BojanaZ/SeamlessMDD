class MyTaskExtension(object):
    def __init__(self, outfolder=None):
        self._outfolder = outfolder

    @property
    def outfolder(self):
        return self._outfolder

    @outfolder.setter
    def outfolder(self, outfolder):
        self._outfolder = outfolder
