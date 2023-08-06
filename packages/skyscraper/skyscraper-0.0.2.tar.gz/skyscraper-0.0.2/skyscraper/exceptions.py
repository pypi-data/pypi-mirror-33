class SkyscraperError(Exception):
    pass


class ExtractFailed(SkyscraperError):
    def __init__(self, err):
        super(ExtractFailed, self).__init__(
            'Extraction failed: {}'.format(err))
