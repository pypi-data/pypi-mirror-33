from helga import settings


def describe_bugs(bugs):
    """
    Return a string that describes a set of bugs (one, or more than one, etc)
    """
    msgs = []
    for bug in bugs:
        if hasattr(settings, 'BUGZILLA_TICKET_URL'):
            url = settings.BUGZILLA_TICKET_URL % {'ticket': bug.id}
        else:
            url = bug.weburl
        msgs.append('%s [%s]' % (url, bug.summary))
    if len(msgs) == 1:
        return msgs[0]
    else:
        return "{} and {}".format(", ".join(msgs[:-1]), msgs[-1])
