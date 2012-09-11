class ParserError(StandardError):
    def __init__(self, msg, response=None):
        StandardError.__init__(self, msg)