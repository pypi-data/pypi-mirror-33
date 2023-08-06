from txbugzilla import connect
from txbugzilla import BugzillaNotFoundException
from txbugzilla import BugzillaNotAuthorizedException
from txbugzilla import BugzillaTokenExpiredException
from helga.plugins import match, ResponseNotReady
from helga import log, settings
from helga_bugzilla.actions import describe, search_external
from helga_bugzilla.exceptions import HelgaBugzillaError

__version__ = '1.3.2'


logger = log.getLogger(__name__)


def match_bugzilla(message):
    for action in (describe, search_external):
        matches = action.match(message)
        if matches:
            return (action, matches)


@match(match_bugzilla)
def helga_bugzilla(client, channel, nick, message, action_and_matches):
    """
    Match information related to Bugzilla.
    """
    connect_args = {}
    if hasattr(settings, 'BUGZILLA_XMLRPC_URL'):
        connect_args['url'] = settings.BUGZILLA_XMLRPC_URL
    d = connect(**connect_args)

    (action, matches) = action_and_matches
    for callback in action.callbacks:
        d.addCallback(callback, matches, client, channel, nick)
        d.addErrback(send_err, client, channel)
    raise ResponseNotReady


def send_err(e, client, channel):
    if isinstance(e.value, BugzillaNotFoundException):
        client.msg(channel, str(e.value))
        return
    if isinstance(e.value, BugzillaNotAuthorizedException):
        not_authorized(e.value.id, client, channel)
        return
    if isinstance(e.value, BugzillaTokenExpiredException):
        logger.error('My bugzilla token is incorrect or expired. '
                     'Please re-authenticate')
        return
    client.msg(channel, str(e.value))
    # Provide the file and line number if this was an an unexpected error.
    if not isinstance(e.value, HelgaBugzillaError):
        tb = e.getBriefTraceback().split()
        client.msg(channel, str(tb[-1]))


def not_authorized(id_, client, channel):
    if hasattr(settings, 'BUGZILLA_TICKET_URL'):
        url = settings.BUGZILLA_TICKET_URL % {'ticket': id_}
    else:
        url = 'bug #%s' % id_
    summary = 'could not read subject (not authorized)'
    msg = '%s [%s]' % (url, summary)
    client.msg(channel, msg)
