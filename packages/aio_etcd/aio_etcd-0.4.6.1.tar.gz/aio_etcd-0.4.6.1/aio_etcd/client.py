"""
.. module:: python-aio_etcd
   :synopsis: An asynchronus python etcd client.

.. moduleauthor:: Jose Plana <jplana@gmail.com>


"""
import logging
#from http.client import HTTPException
from aiohttp.web_exceptions import HTTPException
try:
    from aiohttp.errors import DisconnectedError,ClientConnectionError,ClientResponseError
except ImportError:
    from aiohttp.client_exceptions import ServerDisconnectedError as DisconnectedError
    from aiohttp.client_exceptions import ClientConnectionError,ClientResponseError,ClientPayloadError
from aiohttp.helpers import BasicAuth


import socket
import aiohttp
from urllib3.exceptions import HTTPError
from urllib3.exceptions import ReadTimeoutError
import json
import ssl
import dns.resolver
import aio_etcd as etcd
import asyncio
from functools import wraps

try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse


_log = logging.getLogger(__name__)


class Client(object):

    """
    Asynchronous client for etcd, the distributed log service using raft.
    """

    _MGET = 'GET'
    _MPUT = 'PUT'
    _MPOST = 'POST'
    _MDELETE = 'DELETE'
    _comparison_conditions = set(('prevValue', 'prevIndex', 'prevExist', 'refresh'))
    _read_options = set(('recursive', 'wait', 'waitIndex', 'sorted', 'quorum'))
    _del_conditions = set(('prevValue', 'prevIndex'))

    _client = None

    def __init__(
            self,
            host='127.0.0.1',
            port=2379,
            srv_domain=None,
            version_prefix='/v2',
            allow_redirect=True,
            protocol='http',
            cert=None,
            ca_cert=None,
            username=None,
            password=None,
            allow_reconnect=False,
            use_proxies=False,
            expected_cluster_id=None,
            per_host_pool_size=10,
            ssl_verify=ssl.CERT_REQUIRED,
            loop=None,
            lock_prefix="/_locks"
    ):
        """
        Initialize the client.

        Args:
            host (mixed):
                           If a string, IP to connect to.
                           If a tuple ((host, port), (host, port), ...)

            port (int):  Port used to connect to etcd.

            srv_domain (str): Domain to search the SRV record for cluster autodiscovery.

            version_prefix (str): Url or version prefix in etcd url (default=/v2).

            allow_redirect (bool): allow the client to connect to other nodes.

            protocol (str):  Protocol used to connect to etcd.

            cert (mixed):   If a string, the whole ssl client certificate;
                            if a tuple, the cert and key file names.

            ca_cert (str): The ca certificate. If pressent it will enable
                           validation.

            username (str): username for etcd authentication.

            password (str): password for etcd authentication.

            allow_reconnect (bool): allow the client to reconnect to another
                                    etcd server in the cluster in the case the
                                    default one does not respond.

            use_proxies (bool): we are using a list of proxies to which we connect,
                                 and don't want to connect to the original etcd cluster.

            expected_cluster_id (str): If a string, recorded as the expected
                                       UUID of the cluster (rather than
                                       learning it from the first request),
                                       reads will raise EtcdClusterIdChanged
                                       if they receive a response with a
                                       different cluster ID.
            per_host_pool_size (int): specifies maximum number of connections to pool
                                      by host. By default this will use up to 10
                                      connections.
            lock_prefix (str): Set the key prefix at etcd when client to lock object.
                                      By default this will be use /_locks.
        """

        # If a DNS record is provided, use it to get the hosts list
        if srv_domain is not None:
            try:
                host = self._discover(srv_domain)
            except Exception as e:
                _log.error("Could not discover the etcd hosts from %s: %s",
                           srv_domain, e)

        self._protocol = protocol
        self._loop = loop if loop is not None else asyncio.get_event_loop()

        def uri(protocol, host, port):
            return '%s://%s:%d' % (protocol, host, port)

        if not isinstance(host, tuple):
            self._machines_cache = []
            self._base_uri = uri(self._protocol, host, port)
        else:
            if not allow_reconnect:
                _log.error("List of hosts incompatible with allow_reconnect.")
                raise etcd.EtcdException("A list of hosts to connect to was given, but reconnection not allowed?")
            self._machines_cache = [uri(self._protocol, *conn) for conn in host]
            self._base_uri = self._machines_cache.pop(0)

        self.expected_cluster_id = expected_cluster_id
        self.version_prefix = version_prefix

        self._allow_redirect = allow_redirect
        self._use_proxies = use_proxies
        self._allow_reconnect = allow_reconnect
        self._lock_prefix = lock_prefix

        # SSL Client certificate support
        ssl_ctx = ssl.create_default_context()
        if protocol == 'https':
            # If we don't allow TLSv1, clients using older version of OpenSSL
            # (<1.0) won't be able to connect.
            _log.debug("HTTPS enabled.")
            #kw['ssl_version'] = ssl.PROTOCOL_TLSv1
            if ssl_verify == ssl.CERT_NONE:
                ssl_ctx.check_hostname = False
            ssl_ctx.verify_mode = ssl_verify

        if cert:
            if isinstance(cert, tuple):
                # Key and cert are separate
                ssl_ctx.load_cert_chain(*cert)
            else:
                ssl_ctx.load_cert_chain(cert)

        if ca_cert:
            ssl_ctx.load_verify_locations(ca_cert)

        self.username = None
        self.password = None
        if username and password:
            self.username = username
            self.password = password
        elif username:
            _log.warning('Username provided without password, both are required for authentication')
        elif password:
            _log.warning('Password provided without username, both are required for authentication')
        if self._allow_reconnect:
            # we need the set of servers in the cluster in order to try
            # reconnecting upon error. The cluster members will be
            # added to the hosts list you provided. If you are using
            # proxies, set all
            #
            # Beware though: if you input '127.0.0.1' as your host and
            # etcd advertises 'localhost', both will be in the
            # resulting list.

            # If we're connecting to the original cluster, we can
            # extend the list given to the client with what we get
            # from self.machines
            self._machines_available = self._use_proxies
            self._machines_cache = list(set(self._machines_cache))

            if self._base_uri in self._machines_cache:
                self._machines_cache.remove(self._base_uri)
            _log.debug("Machines cache initialised to %s",
                       self._machines_cache)
        else:
            self._machines_available = True

        if protocol == "https":
            conn = aiohttp.TCPConnector(ssl_context=ssl_ctx, loop=loop)
            self._client = aiohttp.ClientSession(connector=conn, loop=loop)
        else:
            self._client = aiohttp.ClientSession(loop=loop)

    def __del__(self):
        self.close()

    def close(self):
        """Explicitly release the etcd connection(s)."""
        client, self._client = self._client, None
        if client is not None:
           asyncio.run_coroutine_threadsafe(client.close(), self._loop)

    async def _update_machines(self):
        self._machines_cache = await self.machines()
        self._machines_available = True

        # Versions set to None. They will be set upon first usage.
        self._version = self._cluster_version = None

    def _set_version_info(self):
        """
        Sets the version information provided by the server.
        """
        # Set the version
        version_info = json.loads(self.http.request(
            self._MGET,
            self._base_uri + '/version',
            headers=self._get_headers(),
            timeout=self.read_timeout,
            redirect=self.allow_redirect).data.decode('utf-8'))
        self._version = version_info['etcdserver']
        self._cluster_version = version_info['etcdcluster']

    def _discover(self, domain):
        srv_name = "_etcd._tcp.{}".format(domain)
        answers = dns.resolver.query(srv_name, 'SRV')
        hosts = []
        for answer in answers:
            hosts.append(
                (answer.target.to_text(omit_final_dot=True), answer.port))
        _log.debug("Found %s", hosts)
        if not len(hosts):
            raise ValueError("The SRV record is present but no host were found")
        return tuple(hosts)

    @property
    def base_uri(self):
        """URI used by the client to connect to etcd."""
        return self._base_uri

    @property
    def host(self):
        """Node to connect to etcd."""
        return urlparse(self._base_uri).netloc.split(':')[0]

    @property
    def port(self):
        """Port to connect to etcd."""
        return int(urlparse(self._base_uri).netloc.split(':')[1])

    @property
    def protocol(self):
        """Protocol used to connect to etcd."""
        return self._protocol

    @property
    def allow_redirect(self):
        """Allow the client to connect to other nodes."""
        return self._allow_redirect

    @property
    def lock_prefix(self):
        """Get the key prefix at etcd when client to lock object."""
        return self._lock_prefix

    async def machines(self):
        """
        Members of the cluster.

        Returns:
            list. str with all the nodes in the cluster.

        >>> print client.machines
        ['http://127.0.0.1:4001', 'http://127.0.0.1:4002']
        """
        # We can't use api_execute here, or it causes a logical loop
        retries = 0
        while retries < 5:
            for m in [self._base_uri]+self._machines_cache:
                try:
                    uri = m + self.version_prefix + '/machines'
                    response = await self._client.request(
                        self._MGET,
                        uri,
                        allow_redirects=self.allow_redirect,
                    )

                    response = await self._handle_server_response(response)
                    response = await response.read()
                    if response != b"":
                        machines = [
                            node.strip() for node in response.decode('utf-8').split(',')
                        ]
                        _log.debug("Retrieved list of machines: %s", machines)
                        return machines
                except (HTTPException, socket.error, DisconnectedError,
                        ClientConnectionError, asyncio.TimeoutError) as e:
                    # We can't get the list of machines, if one server is in the
                    # machines cache, try on it
                    _log.error("Failed to get list of machines from %s%s: %r",
                            self._base_uri, self.version_prefix, e)
            retries += 1
            await asyncio.sleep(retries/10, loop=self._loop)
        raise etcd.EtcdException("Could not get the list of servers, "
                                    "maybe you provided the wrong "
                                    "host(s) to connect to?")

    async def members(self, **kw):
        """
        A more structured view of peers in the cluster.
        """
        # Empty the members list
        self._members = {}
        try:
            response = await self.api_execute(self.version_prefix + '/members', self._MGET, **kw)
            data = await response.read()
            res = json.loads(data.decode('utf-8'))
            for member in res['members']:
                self._members[member['id']] = member
            return self._members
        except Exception as e:
            raise etcd.EtcdException("Could not get the members list, maybe the cluster has gone away?") from e

    async def leader(self, **kw):
        """
        Returns:
            dict. the leader of the cluster.

        >>> print (loop.run_until_complete(client.leader()))
        {"id":"ce2a822cea30bfca","name":"default","peerURLs":["http://localhost:2380","http://localhost:7001"],"clientURLs":["http://127.0.0.1:4001"]}
        """
        try:
            response = await self.api_execute(self.version_prefix + '/stats/self', self._MGET, **kw)
            data = await response.read()
            leader = json.loads(data.decode('utf-8'))
            return (await self.members())[leader['leaderInfo']['leader']]
        except Exception as exc:
            raise etcd.EtcdException("Cannot get leader data") from exc

    def stats(self):
        """
        Returns:
            dict. the stats of the local server
        """
        return self._stats()
    stats._is_coroutine = True

    def leader_stats(self):
        """
        Returns:
            dict. the stats of the leader
        """
        return self._stats('leader')
    leader_stats._is_coroutine = True

    def store_stats(self):
        """
        Returns:
           dict. the stats of the kv store
        """
        return self._stats('store')
    store_stats._is_coroutine = True

    async def _stats(self, what='self'):
        """ Internal method to access the stats endpoints"""
        data = await self.api_execute(self.version_prefix + '/stats/' + what, self._MGET)
        data = await data.read()
        data = data.decode('utf-8')
        try:
            return json.loads(data)
        except (TypeError,ValueError) as e:
            raise etcd.EtcdException("Cannot parse json data in the response") from e

    @property
    def version(self):
        """
        Version of etcd.
        """
        if not self._version:
            self._set_version_info()
        return self._version

    @property
    def cluster_version(self):
        """
        Version of the etcd cluster.
        """
        if not self._cluster_version:
            self._set_version_info()

        return self._cluster_version

    @property
    def key_endpoint(self):
        """
        REST key endpoint.
        """
        return self.version_prefix + '/keys'

    async def contains(self, key):
        """
        Check if a key is available in the cluster.

        >>> print 'key' in client
        True
        """
        try:
            await self.get(key)
            return True
        except etcd.EtcdKeyNotFound:
            return False

    def _sanitize_key(self, key):
        if not key.startswith('/'):
            key = "/{}".format(key)
        return key

    async def write(self, key, value, ttl=None, dir=False, append=False, **kwdargs):
        """
        Writes the value for a key, possibly doing atomic Compare-and-Swap

        Args:
            key (str):  Key.

            value (object):  value to set

            ttl (int):  Time in seconds of expiration (optional).

            dir (bool): Set to true if we are writing a directory; default is false.

            append (bool): If true, it will post to append the new value to the dir, creating a sequential key. Defaults to false.

            Other parameters modifying the write method are accepted:


            prevValue (str): compare key to this value, and swap only if corresponding (optional).

            prevIndex (int): modify key only if actual modifiedIndex matches the provided one (optional).

            prevExist (bool): If false, only create key; if true, only update key.

            refresh (bool): since 2.3.0, If true, only update the ttl, prev key must existed(prevExist=True).

        Returns:
            client.EtcdResult

        >>> print client.write('/key', 'newValue', ttl=60, prevExist=False).value
        'newValue'

        """
        _log.debug("Writing %s to key %s ttl=%s dir=%s append=%s %s",
                  value, key, ttl, dir, append, kwdargs)
        key = self._sanitize_key(key)
        params = {}
        if value is not None:
            params['value'] = value

        if ttl is not None:
            params['ttl'] = ttl

        if dir:
            if value:
                raise etcd.EtcdException(
                    'Cannot create a directory with a value')
            params['dir'] = "true"

        kw = {}
        for (k, v) in kwdargs.items():
            if k in self._comparison_conditions:
                if type(v) == bool:
                    params[k] = v and "true" or "false"
                else:
                    params[k] = v
            else:
                kw[k] = v

        method = append and self._MPOST or self._MPUT
        if '_endpoint' in kwdargs:
            path = kwdargs['_endpoint'] + key
        else:
            path = self.key_endpoint + key

        response = await self.api_execute(path, method, params=params, **kw)
        return (await self._result_from_response(response))

    def refresh(self, key, ttl, **kwdargs):
        """
        (Since 2.3.0) Refresh the ttl of a key without notifying watchers.

        Keys in etcd can be refreshed without notifying watchers,
        this can be achieved by setting the refresh to true when updating a TTL

        You cannot update the value of a key when refreshing it

        @see: https://github.com/coreos/etcd/blob/release-2.3/Documentation/api.md#refreshing-key-ttl

        Args:
            key (str):  Key.

            ttl (int):  Time in seconds of expiration (optional).

            Other parameters modifying the write method are accepted as `EtcdClient.write`.
        """
        # overwrite kwdargs' prevExist
        kwdargs['prevExist'] = True
        return self.write(key=key, value=None, ttl=ttl, refresh=True, **kwdargs)

    def update(self, obj, **kwdargs):
        """
        Updates the value for a key atomically. Typical usage would be:

        c = aio_etcd.Client()
        o = await c.read("/somekey")
        o.value += 1
        await c.update(o)

        Args:
            obj (aio_etcd.EtcdResult):  The object that needs updating.

        This method returns a coroutine.
        """
        _log.debug("Updating %s to %s.", obj.key, obj.value)
        kwdargs['dir'] = obj.dir
        kwdargs['ttl'] = obj.ttl
        kwdargs['prevExist'] = True

        if not obj.dir:
            # prevIndex on a dir causes a 'not a file' error. d'oh!
            kwdargs['prevIndex'] = obj.modifiedIndex
        return self.write(obj.key, obj.value, **kwdargs)

    async def read(self, key, **kwdargs):
        """
        Returns the value of the key 'key'.

        Args:
            key (str):  Key.

            Recognized kwd args

            recursive (bool): If you should fetch recursively a dir

            wait (bool): If we should wait and return next time the key is changed

            waitIndex (int): The index to fetch results from.

            sorted (bool): Sort the output keys (alphanumerically)

        Returns:
            client.EtcdResult (or an array of client.EtcdResult if a
            subtree is queried)

        Raises:
            KeyValue:  If the key doesn't exists.

        >>> print client.get('/key').value
        'value'

        """
        _log.debug("Issuing read for key %s with args %s", key, kwdargs)
        key = self._sanitize_key(key)

        params = {}
        kw = {}
        for (k, v) in kwdargs.items():
            if k in self._read_options:
                if type(v) == bool:
                    params[k] = v and "true" or "false"
                elif v is not None:
                    params[k] = v
            else:
                kw[k] = v

        response = await self.api_execute(
            self.key_endpoint + key, self._MGET, params=params, **kw)
        return (await self._result_from_response(response))

    async def delete(self, key, recursive=None, dir=None, **kwdargs):
        """
        Removed a key from etcd.

        Args:

            key (str):  Key.

            recursive (bool): if we want to recursively delete a directory, set
                              it to true

            dir (bool): if we want to delete a directory, set it to true

            prevValue (str): compare key to this value, and swap only if
                             corresponding (optional).

            prevIndex (int): modify key only if actual modifiedIndex matches the
                             provided one (optional).

        Returns:
            client.EtcdResult

        Raises:
            KeyValue:  If the key doesn't exists.

        >>> print client.delete('/key').key
        '/key'

        """
        _log.debug("Deleting %s recursive=%s dir=%s extra args=%s",
                   key, recursive, dir, kwdargs)
        key = self._sanitize_key(key)

        params = {}
        if recursive is not None:
            params['recursive'] = recursive and "true" or "false"
        if dir is not None:
            params['dir'] = dir and "true" or "false"

        for k in self._del_conditions:
            if k in kwdargs:
                params[k] = kwdargs.pop(k)
        _log.debug("Calculated params = %s", params)

        response = await self.api_execute(
            self.key_endpoint + key, self._MDELETE, params=params, **kwdargs)
        return (await self._result_from_response(response))

    def pop(self, key, recursive=None, dir=None, **kwdargs):
        """
        Remove specified key from etcd and return the corresponding value.

        Args:

            key (str):  Key.

            recursive (bool): if we want to recursively delete a directory, set
                              it to true

            dir (bool): if we want to delete a directory, set it to true

            prevValue (str): compare key to this value, and swap only if
                             corresponding (optional).

            prevIndex (int): modify key only if actual modifiedIndex matches the
                             provided one (optional).

        Returns:
            A coroutine returning client.EtcdResult

        Raises:
            KeyValue:  If the key doesn't exists.

        >>> print client.pop('/key').value
        'value'

        """
        return self.delete(key=key, recursive=recursive, dir=dir, **kwdargs)._prev_node
    pop._is_coroutine = True

    # Higher-level methods on top of the basic primitives
    def test_and_set(self, key, value, prev_value, ttl=None, **kwdargs):
        """
        Atomic test & set operation.
        It will check if the value of 'key' is 'prev_value',
        if the the check is correct will change the value for 'key' to 'value'
        if the the check is false an exception will be raised.

        Args:
            key (str):  Key.
            value (object):  value to set
            prev_value (object):  previous value.
            ttl (int):  Time in seconds of expiration (optional).

        Returns:
            A coroutine returning client.EtcdResult

        Raises:
            ValueError: When the 'prev_value' is not the current value.

        >>> print client.test_and_set('/key', 'new', 'old', ttl=60).value
        'new'

        """
        return self.write(key, value, prevValue=prev_value, ttl=ttl, **kwdargs)
    test_and_set._is_coroutine = True

    def set(self, key, value, ttl=None, **kwdargs):
        """
        Compatibility: sets the value of the key 'key' to the value 'value'

        Args:
            key (str):  Key.
            value (object):  value to set
            ttl (int):  Time in seconds of expiration (optional).

        Returns:
            A coroutine returning client.EtcdResult

        Raises:
           etcd.EtcdException: when something weird goes wrong.

        """
        return self.write(key, value, ttl=ttl, **kwdargs)
    set._is_coroutine = True

    def get(self, key, **kwdargs):
        """
        Returns the value of the key 'key'.

        Args:
            key (str):  Key.

        Returns:
            A coroutine returning client.EtcdResult

        Raises:
            KeyError:  If the key doesn't exists.

        >>> print client.get('/key').value
        'value'

        """
        return self.read(key, **kwdargs)
    get._is_coroutine = True

    async def watch(self, key, index=None, recursive=None):
        """
        Blocks until a new event has been received, starting at index 'index'

        Args:
            key (str):  Key.

            index (int): Index to start from.

        Returns:
            A coroutine returning client.EtcdResult

        Raises:
            KeyValue:  If the key doesn't exist.

        >>> print client.watch('/key').value
        'value'

        """
        _log.debug("Wait %s on %s", index, key)
        if index:
            res = await self.read(key, wait=True, waitIndex=index, recursive=recursive, timeout=None)
        else:
            res = await self.read(key, wait=True, recursive=recursive, timeout=None)
        _log.debug("Wait %s on %s done: %s",index, key, res)
        return res

    async def eternal_watch(self, key, callback, index=None, recursive=None):
        """
        Generator that will call the callback every time a key changes.
        Note that this method will block forever until an event is generated
        and the callback function raises StopWatching.

        Args:
            key (str):  Key to subcribe to.
            index (int):  Index from where the changes will be received.

        Returns:
            Index to continue watching from

        >>> for event in client.eternal_watch('/subcription_key'):
        ...     print event.value
        ...
        value1
        value2

        """
        local_index = index
        while True:
            response = await self.watch(key, index=local_index, recursive=recursive)
            local_index = response.modifiedIndex + 1
            try:
                res = callback(response)
                if isinstance(res, asyncio.Future) or asyncio.iscoroutine(res):
                    await res
            except etcd.StopWatching:
                return local_index

    def get_lock(self, *args, **kwargs):
        raise NotImplementedError('Lock primitives were removed from etcd 2.0')

    @property
    def election(self):
        raise NotImplementedError('Election primitives were removed from etcd 2.0')

    async def _result_from_response(self, response):
        """ Creates an EtcdResult from json dictionary """
        raw_response = await response.read()
        try:
            res = await response.json()
        except (TypeError, ValueError, UnicodeError) as e:
            raise etcd.EtcdException(
                'Server response was not valid JSON: %r', raw_response)
        _log.debug("result: %s", res)
        try:
            r = etcd.EtcdResult(**res)
            if response.status == 201:
                r.newKey = True
            r.parse_headers(response)
            return r
        except Exception as e:
            raise etcd.EtcdException(
                'Unable to decode server response') from e

    def _next_server(self, cause=None):
        """ Selects the next server in the list, refreshes the server list. """
        _log.debug("Selection next machine in cache. Available machines: %s",
                   self._machines_cache)
        try:
            mach = self._machines_cache.pop()
        except IndexError as e:
            _log.error("Machines cache is empty, no machines to try.")
            raise etcd.EtcdConnectionFailed('No more machines in the cluster', cause=cause) from e
        else:
            _log.info("Selected new etcd server %s", mach)
            return mach

    def _wrap_request(payload):
        @wraps(payload)
        async def wrapper(self, path, method, params=None, **kw):
            some_request_failed = False
            response = False

            if not path.startswith('/'):
                raise ValueError('Path does not start with /')

            if not self._machines_available:
                await self._update_machines()

            while not response:
                some_request_failed = False
                try:
                    if self._client is None:
                        raise DisconnectedError
                    response = await payload(self, path, method, params=params, **kw)
                    # Check the cluster ID hasn't changed under us.  We use
                    # preload_content=False above so we can read the headers
                    # before we wait for the content of a watch.
                    self._check_cluster_id(response)
                    # Now force the data to be preloaded in order to trigger any
                    # IO-related errors in this method rather than when we try to
                    # access it later.
                    _ = await response.read()
                    # urllib3 doesn't wrap all httplib exceptions and earlier versions
                    # don't wrap socket errors either.
                except (ClientResponseError, DisconnectedError, HTTPException,
                        socket.error, asyncio.TimeoutError, ClientPayloadError) as e:
                    if (isinstance(params, dict) and
                        params.get("wait") == "true" and
                        isinstance(e, ReadTimeoutError)):
                        _log.debug("Watch timed out.")
                        raise etcd.EtcdWatchTimedOut(
                            "Watch timed out: %r" % e,
                            cause=e
                        )
                    _log.error("Request to server %s failed: %r",
                               self._base_uri, e)
                    if self._allow_reconnect:
                        _log.info("Reconnection allowed, looking for another "
                                  "server.")
                        # _next_server() raises EtcdException if there are no
                        # machines left to try, breaking out of the loop.
                        self._base_uri = self._next_server(cause=e)
                        some_request_failed = True

                        # if exception is raised on _ = response.data
                        # the condition for while loop will be False
                        # but we should retry
                        response = False
                    else:
                        _log.debug("Reconnection disabled, giving up.")
                        raise etcd.EtcdConnectionFailed(
                            "Connection to etcd failed due to %r" % e,
                            cause=e
                        )
                except etcd.EtcdClusterIdChanged as e:
                    _log.warning(e)
                    raise
                except asyncio.CancelledError:
                    # don't complain
                    raise
                except Exception:
                    _log.exception("Unexpected request failure, re-raising.")
                    raise
                else:
                    try:
                        response = await self._handle_server_response(response)
                    except etcd.EtcdException as e:
                        if "during rolling upgrades" in e.payload['message']:
                            response = False
                            some_request_failed = True
                        else:
                            raise

                if some_request_failed:
                    if not self._use_proxies:
                        # The cluster may have changed since last invocation
                        self._machines_cache = await self.machines()
                    if self._base_uri in self._machines_cache:
                        self._machines_cache.remove(self._base_uri)
            return response
        return wrapper

    @_wrap_request
    def api_execute(self, path, method, params=None, **kw):
        """ Executes the query. """

        if not path.startswith('/'):
            raise ValueError('Path does not start with /')

        url = self._base_uri + path

        if (method == self._MGET) or (method == self._MDELETE):
            return self._client.request(
                method,
                url,
                params=params,
                auth=self._get_auth(),
                allow_redirects=self.allow_redirect,
                **kw
                )

        elif (method == self._MPUT) or (method == self._MPOST):
            return self._client.request(
                method,
                url,
                data=params,
                auth=self._get_auth(),
                allow_redirects=self.allow_redirect,
                **kw
                )
        else:
            raise etcd.EtcdException(
                'HTTP method {} not supported'.format(method))

    @_wrap_request
    def api_execute_json(self, path, method, params=None, **kw):
        url = self._base_uri + path
        json_payload = json.dumps(params)
        headers = { 'Content-Type': 'application/json' }
        return self._client.request(method,
                                    url,
                                    data=json_payload,
                                    allow_redirects=self.allow_redirect,
                                    auth=self._get_auth(),
                                    headers=headers,
                                    **kw)

    def _check_cluster_id(self, response):
        cluster_id = response.headers.get("x-etcd-cluster-id", None)
        if not cluster_id:
            # _log.warning("etcd response did not contain a cluster ID")
            return
        id_changed = (self.expected_cluster_id and
                      cluster_id != self.expected_cluster_id)
        # Update the ID so we only raise the exception once.
        old_expected_cluster_id = self.expected_cluster_id
        self.expected_cluster_id = cluster_id
        if id_changed:
            # Defensive: clear the pool so that we connect afresh next
            # time.
            raise etcd.EtcdClusterIdChanged(
                'The UUID of the cluster changed from {} to '
                '{}.'.format(old_expected_cluster_id, cluster_id))

    async def _handle_server_response(self, response):
        """ Handles the server response """
        if response.status in [200, 201]:
            return response

        else:
            data = await response.read()
            resp = data.decode('utf-8')

            # throw the appropriate exception
            try:
                r = json.loads(resp)
                r['status'] = response.status
            except (TypeError, ValueError):
                # Bad JSON, make a response locally.
                r = {"message": "Bad response",
                     "cause": str(resp)}
            etcd.EtcdError.handle(r)

    def _get_auth(self):
        if self.username and self.password:
            return BasicAuth(self.username, self.password)
        return None

