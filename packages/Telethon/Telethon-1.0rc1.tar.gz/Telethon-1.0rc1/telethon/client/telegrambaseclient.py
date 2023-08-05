import abc
import logging
import platform
import queue
import sys
import threading
import time
import warnings
from datetime import timedelta, datetime

from .. import version
from ..crypto import rsa
from ..extensions import markdown
from ..network import MTProtoSender, ConnectionTcpFull
from ..network.mtprotostate import MTProtoState
from ..sessions import Session, SQLiteSession
from ..tl import TLObject, functions, types
from ..tl.alltlobjects import LAYER

DEFAULT_DC_ID = 4
DEFAULT_IPV4_IP = '149.154.167.51'
DEFAULT_IPV6_IP = '[2001:67c:4e8:f002::a]'
DEFAULT_PORT = 443

__log__ = logging.getLogger(__name__)


class TelegramBaseClient(abc.ABC):
    """
    This is the abstract base class for the client. It defines some
    basic stuff like connecting, switching data center, etc, and
    leaves the `__call__` unimplemented.

    Args:
        session (`str` | `telethon.sessions.abstract.Session`, `None`):
            The file name of the session file to be used if a string is
            given (it may be a full path), or the Session instance to be
            used otherwise. If it's ``None``, the session will not be saved,
            and you should call :meth:`.log_out()` when you're done.

            Note that if you pass a string it will be a file in the current
            working directory, although you can also pass absolute paths.

            The session file contains enough information for you to login
            without re-sending the code, so if you have to enter the code
            more than once, maybe you're changing the working directory,
            renaming or removing the file, or using random names.

        api_id (`int` | `str`):
            The API ID you obtained from https://my.telegram.org.

        api_hash (`str`):
            The API ID you obtained from https://my.telegram.org.

        connection (`telethon.network.connection.common.Connection`, optional):
            The connection instance to be used when creating a new connection
            to the servers. If it's a type, the `proxy` argument will be used.

            Defaults to `telethon.network.connection.tcpfull.ConnectionTcpFull`.

        use_ipv6 (`bool`, optional):
            Whether to connect to the servers through IPv6 or not.
            By default this is ``False`` as IPv6 support is not
            too widespread yet.

        proxy (`tuple` | `dict`, optional):
            A tuple consisting of ``(socks.SOCKS5, 'host', port)``.
            See https://github.com/Anorov/PySocks#usage-1 for more.

        timeout (`int` | `float` | `timedelta`, optional):
            The timeout to be used when connecting, sending and receiving
            responses from the network. This is **not** the timeout to
            be used when ``await``'ing for invoked requests, and you
            should use ``asyncio.wait`` or ``asyncio.wait_for`` for that.

        request_retries (`int`, optional):
            How many times a request should be retried. Request are retried
            when Telegram is having internal issues (due to either
            ``errors.ServerError`` or ``errors.RpcCallFailError``),
            when there is a ``errors.FloodWaitError`` less than
            ``session.flood_sleep_threshold``, or when there's a
            migrate error.

            May set to a false-y value (``0`` or ``None``) for infinite
            retries, but this is not recommended, since some requests can
            always trigger a call fail (such as searching for messages).

        connection_retries (`int`, optional):
            How many times the reconnection should retry, either on the
            initial connection or when Telegram disconnects us. May be
            set to a false-y value (``0`` or ``None``) for infinite
            retries, but this is not recommended, since the program can
            get stuck in an infinite loop.

        auto_reconnect (`bool`, optional):
            Whether reconnection should be retried `connection_retries`
            times automatically if Telegram disconnects us or not.

        report_errors (`bool`, optional):
            Whether to report RPC errors or not. Defaults to ``True``,
            see :ref:`api-status` for more information.

        device_model (`str`, optional):
            "Device model" to be sent when creating the initial connection.
            Defaults to ``platform.node()``.

        system_version (`str`, optional):
            "System version" to be sent when creating the initial connection.
            Defaults to ``platform.system()``.

        app_version (`str`, optional):
            "App version" to be sent when creating the initial connection.
            Defaults to `telethon.version.__version__`.

        lang_code (`str`, optional):
            "Language code" to be sent when creating the initial connection.
            Defaults to ``'en'``.

        system_lang_code (`str`, optional):
            "System lang code"  to be sent when creating the initial connection.
            Defaults to `lang_code`.
    """

    # Current TelegramClient version
    __version__ = version.__version__

    # Cached server configuration (with .dc_options), can be "global"
    _config = None
    _cdn_config = None

    # region Initialization

    def __init__(self, session, api_id, api_hash,
                 *,
                 connection=ConnectionTcpFull,
                 use_ipv6=False,
                 proxy=None,
                 timeout=timedelta(seconds=10),
                 request_retries=5,
                 connection_retries=5,
                 auto_reconnect=True,
                 report_errors=True,
                 device_model=None,
                 system_version=None,
                 app_version=None,
                 lang_code='en',
                 system_lang_code='en',
                 update_workers=None,
                 spawn_read_thread=True):
        if not api_id or not api_hash:
            raise ValueError(
                "Your API ID or Hash cannot be empty or None. "
                "Refer to telethon.rtfd.io for more information.")

        if update_workers is not None or spawn_read_thread is not True:
            warnings.warn(
                'update_workers and spawn_read_thread are deprecated and '
                'have no effect. Stop passing these arguments and '
                'consider using asyncio for more speed and control.'
            )

        self._use_ipv6 = use_ipv6

        # Determine what session object we have
        if isinstance(session, str) or session is None:
            session = SQLiteSession(session)
        elif not isinstance(session, Session):
            raise TypeError(
                'The given session must be a str or a Session instance.'
            )

        # ':' in session.server_address is True if it's an IPv6 address
        if (not session.server_address or
                (':' in session.server_address) != use_ipv6):
            session.set_dc(
                DEFAULT_DC_ID,
                DEFAULT_IPV6_IP if self._use_ipv6 else DEFAULT_IPV4_IP,
                DEFAULT_PORT
            )

        session.report_errors = report_errors
        self.session = session
        self.api_id = int(api_id)
        self.api_hash = api_hash

        self._request_retries = request_retries or sys.maxsize
        self._connection_retries = connection_retries or sys.maxsize
        self._auto_reconnect = auto_reconnect

        if isinstance(connection, type):
            connection = connection(
                proxy=proxy, timeout=timeout)

        # Used on connection. Capture the variables in a lambda since
        # exporting clients need to create this InvokeWithLayerRequest.
        system = platform.uname()
        self._init_with = lambda x: functions.InvokeWithLayerRequest(
            LAYER, functions.InitConnectionRequest(
                api_id=self.api_id,
                device_model=device_model or system.system or 'Unknown',
                system_version=system_version or system.release or '1.0',
                app_version=app_version or self.__version__,
                lang_code=lang_code,
                system_lang_code=system_lang_code,
                lang_pack='',  # "langPacks are for official apps only"
                query=x
            )
        )

        state = MTProtoState(self.session.auth_key)
        self._connection = connection
        self._sender = MTProtoSender(
            state, connection,
            retries=self._connection_retries,
            auto_reconnect=self._auto_reconnect,
            update_callback=self._handle_update
        )

        # Cache :tl:`ExportedAuthorization` as ``dc_id: MTProtoState``
        # to easily import them when getting an exported sender.
        self._exported_auths = {}

        # Save whether the user is authorized here (a.k.a. logged in)
        self._authorized = None  # None = We don't know yet

        # Default PingRequest delay
        self._last_ping = time.time()
        self._ping_delay = timedelta(minutes=1)

        self._updates = queue.Queue()
        self._updates_handle = None
        self._last_request = time.time()
        self._channel_pts = {}

        # Start with invalid state (-1) so we can have somewhere to store
        # the state, but also be able to determine if we are authorized.
        self._state = types.updates.State(-1, 0, datetime.now(), 0, -1)

        # Some further state for subclasses
        self._event_builders = []
        self._events_pending_resolve = []
        self._event_resolve_lock = threading.Lock()

        # Default parse mode
        self._parse_mode = markdown

        # Some fields to easy signing in. Let {phone: hash} be
        # a dictionary because the user may change their mind.
        self._phone_code_hash = {}
        self._phone = None
        self._tos = None

        # Sometimes we need to know who we are, cache the self peer
        self._self_input_peer = None

    # endregion

    # region Properties

    @property
    def disconnected(self):
        """
        Future that resolves when the connection to Telegram
        ends, either by user action or in the background.
        """
        return self._sender.disconnected

    # endregion

    # region Connecting

    def connect(self):
        """
        Connects to Telegram.
        """
        had_auth = self.session.auth_key is not None
        self._sender.connect(
            self.session.server_address, self.session.port)

        self._sender.send(self._init_with(
            functions.help.GetConfigRequest()))

        self._updates_handle = threading.Thread(target=self._update_loop,
                                                daemon=True)
        self._updates_handle.start()

        if not had_auth:
            self.session.auth_key = self._sender.state.auth_key
            self.session.save()

    def is_connected(self):
        """
        Returns ``True`` if the user has connected.
        """
        return self._sender.is_connected()

    def disconnect(self):
        """
        Disconnects from Telegram.
        """
        self._sender.disconnect()
        # This method can be called from its own thread, so don't join self
        if self._updates_handle != threading.current_thread():
            self._updates_handle.join()
        self.session.close()

    def _switch_dc(self, new_dc):
        """
        Permanently switches the current connection to the new data center.
        """
        __log__.info('Reconnecting to new data center %s', new_dc)
        dc = self._get_dc(new_dc)

        self.session.set_dc(dc.id, dc.ip_address, dc.port)
        # auth_key's are associated with a server, which has now changed
        # so it's not valid anymore. Set to None to force recreating it.
        self.session.auth_key = self._sender.state.auth_key = None
        self.session.save()
        self.disconnect()
        return self.connect()

    # endregion

    # region Working with different connections/Data Centers

    def _get_dc(self, dc_id, cdn=False):
        """Gets the Data Center (DC) associated to 'dc_id'"""
        cls = self.__class__
        if not cls._config:
            cls._config = self(functions.help.GetConfigRequest())

        if cdn and not self._cdn_config:
            cls._cdn_config = self(functions.help.GetCdnConfigRequest())
            for pk in cls._cdn_config.public_keys:
                rsa.add_key(pk.public_key)

        return next(
            dc for dc in cls._config.dc_options
            if dc.id == dc_id
            and bool(dc.ipv6) == self._use_ipv6 and bool(dc.cdn) == cdn
        )

    def _get_exported_sender(self, dc_id):
        """
        Returns a cached `MTProtoSender` for the given `dc_id`, or creates
        a new one if it doesn't exist yet, and imports a freshly exported
        authorization key for it to be usable.
        """
        # Thanks badoualy/kotlogram on /telegram/api/DefaultTelegramClient.kt
        # for clearly showing how to export the authorization
        auth = self._exported_auths.get(dc_id)
        dc = self._get_dc(dc_id)
        state = MTProtoState(auth)
        # Can't reuse self._sender._connection as it has its own seqno.
        #
        # If one were to do that, Telegram would reset the connection
        # with no further clues.
        sender = MTProtoSender(state, self._connection.clone())
        sender.connect(dc.ip_address, dc.port)
        if not auth:
            __log__.info('Exporting authorization for data center %s', dc)
            auth = self(functions.auth.ExportAuthorizationRequest(dc_id))
            req = self._init_with(functions.auth.ImportAuthorizationRequest(
                id=auth.id, bytes=auth.bytes
            ))
            sender.send(req).result()  # Wait for the authorization object
            self._exported_auths[dc_id] = sender.state.auth_key

        return sender

    def _get_cdn_client(self, cdn_redirect):
        """Similar to ._get_exported_client, but for CDNs"""
        # TODO Implement
        raise NotImplementedError
        session = self._exported_sessions.get(cdn_redirect.dc_id)
        if not session:
            dc = self._get_dc(cdn_redirect.dc_id, cdn=True)
            session = self.session.clone()
            session.set_dc(dc.id, dc.ip_address, dc.port)
            self._exported_sessions[cdn_redirect.dc_id] = session

        __log__.info('Creating new CDN client')
        client = TelegramBareClient(
            session, self.api_id, self.api_hash,
            proxy=self._sender.connection.conn.proxy,
            timeout=self._sender.connection.get_timeout()
        )

        # This will make use of the new RSA keys for this specific CDN.
        #
        # We won't be calling GetConfigRequest because it's only called
        # when needed by ._get_dc, and also it's static so it's likely
        # set already. Avoid invoking non-CDN methods by not syncing updates.
        client.connect(_sync_updates=False)
        client._authorized = self._authorized
        return client

    # endregion

    # region Invoking Telegram requests

    @abc.abstractmethod
    def __call__(self, request, ordered=False):
        """
        Invokes (sends) one or more MTProtoRequests and returns (receives)
        their result.

        Args:
            request (`TLObject` | `list`):
                The request or requests to be invoked.

            ordered (`bool`, optional):
                Whether the requests (if more than one was given) should be
                executed sequentially on the server. They run in arbitrary
                order by default.

        Returns:
            The result of the request (often a `TLObject`) or a list of
            results if more than one request was given.
        """
        raise NotImplementedError

    # Let people use client.invoke(SomeRequest()) instead client(...)
    def invoke(self, *args, **kwargs):
        warnings.warn('client.invoke(...) is deprecated, '
                      'use client(...) instead')
        return self(*args, **kwargs)

    @abc.abstractmethod
    def _handle_update(self, update):
        raise NotImplementedError

    @abc.abstractmethod
    def _update_loop(self):
        raise NotImplementedError

    # endregion
