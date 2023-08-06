class HelgaBugzillaError(Exception):
    pass


class UnknownTrackerError(HelgaBugzillaError):
    def __init__(self, ticket):
        message = "I don't know how to parse %s for searching" % ticket
        HelgaBugzillaError.__init__(self, message)


class NoBugFoundError(HelgaBugzillaError):
    def __init__(self, ticket, nick=None):
        message = "I couldn't find a BZ for %s" % ticket
        if nick is not None:
            message = '%s, %s' % (nick, message)
        HelgaBugzillaError.__init__(self, message)
