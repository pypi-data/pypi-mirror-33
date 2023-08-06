import re
from twisted.internet import defer
from helga_bugzilla.utils import describe_bugs

""" Match possible Bugzilla tickets, return links and summary info """


def match(message):
    """
    Simple matching for "bz#123" comments.

    returns: a (possibly empty) list of BZ IDs.
    """
    tickets = []
    pattern = re.compile(r"""
       (?:               # Prefix to trigger the plugin:
            bzs?         #   "bz" or "bzs"
          | bugs?        #   "bug" or "bugs"
          | bugzilla?    #   "bugzilla" or "bugzillas"
       )                 #
       \s*               #
       [#]?[0-9]+        # Number, optionally preceded by "#"
       (?:               # The following pattern will match zero or more times:
          ,?             #   Optional comma
          \s+            #
          (?:and\s+)?    #   Optional "and "
          [#]?[0-9]+     #   Number, optionally preceded by "#"
       )*
       """, re.VERBOSE | re.IGNORECASE)
    for bzmatch in re.findall(pattern, message):
        if re.search(r'http\S+%s' % bzmatch, message):
            # Skip "bz" strings in URLs.
            continue
        if '-%s' % bzmatch in message or '.%s' % bzmatch in message:
            # Skip "-bz" or ".bz" strings (git branches or NVRs).
            continue
        for ticket in re.findall(r'[0-9]+', bzmatch):
            if ticket == '2' and 'bz2' in bzmatch:
                continue  # False positive, like ".tar.bz2".
            if ticket not in tickets:
                tickets.append(ticket)
    return tickets


@defer.inlineCallbacks
def get_summaries(bz, matches, client, channel, nick):
    """
    Get all our bugs' summaries
    """
    bugs = yield bz.get_bugs_summaries(matches)
    defer.returnValue(bugs)


def send_message(bugs, matches, client, channel, nick):
    """
    Send a message to channel.
    """
    if bugs is not None:
        msg = construct_message(bugs, nick)
        client.msg(channel, msg)


def construct_message(bugs, nick):
    """
    Return a string about a nick and a list of tickets' URLs and summaries.
    """
    description = describe_bugs(bugs)
    return '%s might be talking about %s' % (nick, description)


# List of callbacks to fire on a match:
callbacks = (get_summaries, send_message)
