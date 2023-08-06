import getpass
import logging
import netrc
import os
import uuid

import sleekxmpp

__all__ = ('LVAlertClient',)

log = logging.getLogger(__name__)

DEFAULT_SERVER = 'lvalert.cgca.uwm.edu'


class _Netrc(netrc.netrc):
    """Subclass Python standard library :class:`~netrc.netrc` class to add
    some custom behaviors.

    1.   If the ``NETRC`` environment variable is defined, then use it as
         the default netrc file path.

    2.   Apply permissions checks whether or or not we are reading from the
         default netrc file.
    """

    def __init__(self, file=None):
        # Copied and adapted from netrc.py from Python 3.7
        if file is None:
            file = os.environ.get('NETRC')
        if file is None:
            file = os.path.join(os.path.expanduser("~"), ".netrc")
        self.hosts = {}
        self.macros = {}
        with open(file) as fp:
            self._parse(file, fp, True)


def _get_default_login(netrcfile, server):
    try:
        netrcfile = _Netrc(netrcfile)
    except (OSError, netrc.NetrcParseError):
        log.exception('Cannot load netrc file: %s', netrc)
        return None, None

    auth = netrcfile.authenticators(server)
    if auth is None:
        log.warn('No netrc entry found for server: %s', server)
        return None, None

    default_username, _, default_password = auth
    return default_username, default_password


def _get_login(username, password, netrc, interactive, server):
    default_username, default_password = _get_default_login(netrc, server)
    prompt = 'password for {}@{}: '.format(username, server)

    if username is not None and password is not None:
        return username, password
    elif username is None and default_username is None:
        raise RuntimeError('Username not specified')
    elif username is None or username == default_username:
        return default_username, default_password
    elif interactive:
        return username, getpass.getpass(prompt)
    else:
        raise RuntimeError('Password not specified')


class LVAlertClient(sleekxmpp.ClientXMPP):
    """An XMPP client configured for LVAlert.

    Parameters
    ----------
    username : str (optional)
        The XMPP username, or :obj:`None` to look up from the netrc_ file.
    password : str (optional)
        The XMPP password, or :obj:`None` to look up from the netrc_ file.
    resource : str (optional)
        The XMPP resource ID, or :obj:`None` to generate a random one.
    netrc : str (optional)
        The netrc_ file. The default is to consult the ``NETRC`` environment
        variable or use the default path of ``~/.netrc``.
    interactive : bool (optional)
        If :obj:`True`, then fall back to asking for the password on the
        command line if necessary.
    server : str (optional)
        The LVAlert server hostname.

    Example
    -------
    .. code-block:: python

        def process_alert(node, payload):
            if node == 'cbc_gstlal':
                alert = json.loads(payload)
                ...

        client = LVAlertClient()
        client.listen(process_alert)
        client.connect()
        client.process(block=True)
    """

    def __init__(self, username=None, password=None, resource=None, netrc=None,
                 interactive=False, server=DEFAULT_SERVER):
        username, password = _get_login(
            username, password, netrc, interactive, server)
        if resource is None:
            resource = uuid.uuid4().hex
        jid = '{}@{}/{}'.format(username, server, resource)

        super(LVAlertClient, self).__init__(jid, password)

        self.register_plugin('xep_0060')  # Activate PubSub plugin
        self.add_event_handler("session_start", self._session_start)
        self.use_tls = True

    def _session_start(self, event):
        self.send_presence()
        self.get_roster()

    def listen(self, callback):
        """Set a callback to be executed for each pubsub item received.

        Parameters
        ----------
        callback : callable
            A function of two arguments: the node and the alert payload.
        """
        self._callback = callback
        self.add_event_handler('pubsub_publish', self._pubsub_publish)

    def _pubsub_publish(self, msg):
        self._callback(msg['pubsub_event']['items']['node'],
                       msg['pubsub_event']['items']['item']['payload'].text)

    @property
    def _pubsub_server(self):
        return 'pubsub.{}'.format(self.boundjid.server)

    def get_nodes(self):
        """Get a list of all available pubsub nodes."""
        result = self['xep_0060'].get_nodes(self._pubsub_server)
        return [item for _, item, _ in result['disco_items']['items']]

    def get_subscriptions(self):
        """Get a list of your subscriptions."""
        result = self['xep_0060'].get_subscriptions(self._pubsub_server)
        return sorted({stanza['node'] for stanza in
                       result['pubsub']['subscriptions']['substanzas']})

    def subscribe(self, *nodes):
        """Subscribe to one or more pubsub nodes."""
        for node in nodes:
            log.info('Subscribing to %s', node)
            self['xep_0060'].subscribe(self._pubsub_server, node)

    def unsubscribe(self, *nodes):
        """Unsubscribe from one or more pubsub nodes."""
        for node in nodes:

            subscriptions = self['xep_0060'].get_subscriptions(
                self._pubsub_server, node
            )['pubsub']['subscriptions']['substanzas']

            for subscription in subscriptions:
                log.info('Unsubscribing from %s [%s]',
                         node, subscription['subid'])
                self['xep_0060'].unsubscribe(
                    self._pubsub_server, node, subscription['subid'])
