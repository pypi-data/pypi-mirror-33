import re
from urlparse import urlparse
from twisted.internet import defer
from helga_bugzilla.utils import describe_bugs
from helga_bugzilla.exceptions import UnknownTrackerError, NoBugFoundError
from helga import log

logger = log.getLogger(__name__)


def match(message):
    """
    Match a comment asking about external trackers.
    """
    pattern = re.compile(r"""
       (?:
            which
          | what
          | whats
          | whats\sthe
          | what's
          | what's\sthe
          | what\sis
          | what\sis\sthe
          | where
          | wheres
          | wheres\sthe
          | where's
          | where's\sthe
          | where\sis
          | where\sis\sthe
       )
       \s+
       (?:
            bz
          | bug
          | rhbz
          | bugzilla
       )
       \s+
       (?:
            is
          | matches
          | tracks
          | relates\sto
          | corresponds\sto
          | for
          | that\sis
          | that\smatches
          | that\stracks
          | that\scorresponds\sto
       )
       \s+
       (\S+)
       """, re.VERBOSE | re.IGNORECASE)
    return [url.rstrip('?') for url in pattern.findall(message)]


def find_tracker_url(ticket_url):
    """
    Given http://tracker.ceph.com/issues/16673 or
    tracker.ceph.com/issues/16673, return "http://tracker.ceph.com".

    Return None if ticket_url does not look like a URL.
    """
    if ticket_url.startswith('http://') or ticket_url.startswith('https://'):
        o = urlparse(ticket_url)
        scheme, netloc = o.scheme, o.netloc
    else:
        try:
            (netloc, _) = ticket_url.split('/', 1)
        except ValueError:
            return None
        if netloc == 'tracker.ceph.com':
            scheme = 'http'
        else:
            scheme = 'https'
    return '%s://%s' % (scheme, netloc)


def find_tracker_id(ticket_url):
    matches = None
    if 'code.engineering.redhat.com' in ticket_url:
        matches = re.findall('\d+$', ticket_url)
    elif 'github.com' in ticket_url:
        matches = re.findall('github\.com/(.+)', ticket_url)
    elif 'launchpad.net' in ticket_url:
        matches = re.findall('\d+$', ticket_url)
    elif 'projects.engineering.redhat.com' in ticket_url:
        regex = 'projects.engineering.redhat.com/browse/(.+)'
        matches = re.findall(regex, ticket_url)
    elif 'review.gerrithub.io' in ticket_url:
        matches = re.findall('\d+$', ticket_url)
    elif 'tracker.ceph.com' in ticket_url:
        matches = re.findall('\d+$', ticket_url)
    elif 'trello.com' in ticket_url:
        matches = re.findall('trello\.com/c/([^/]+)', ticket_url)
    if matches:
        return matches[0]
    raise UnknownTrackerError(ticket_url)


@defer.inlineCallbacks
def get_bz_for_externals(bz, links, client, channel, nick):
    ticket_url = links[0]
    external_tracker_url = find_tracker_url(ticket_url)
    if external_tracker_url is None:
        defer.returnValue(False)
    external_tracker_id = find_tracker_id(ticket_url)
    logger.debug('searching tracker: %s id: %s' % (external_tracker_url,
                                                   external_tracker_id))
    bugs = yield bz.find_by_external_tracker(external_tracker_url,
                                             external_tracker_id)
    defer.returnValue((ticket_url, bugs))


def send_message(ticket_and_bugs, links, client, channel, nick):
    # If we could figure out a ticket and list of bugs, then send a message.
    if ticket_and_bugs:
        (ticket, bugs) = ticket_and_bugs
        msg = construct_message(ticket, bugs, nick)
        client.msg(channel, msg)


def construct_message(ticket, bugs, nick):
    if bugs:
        descriptions = describe_bugs(bugs)
        return '%s, %s is %s' % (nick, ticket, descriptions)
    raise NoBugFoundError(ticket, nick)


callbacks = (get_bz_for_externals, send_message)
