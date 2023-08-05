# Copyright (c) 2013-2018 by Ron Frederick <ronf@timeheart.net>.
# All rights reserved.
#
# This program and the accompanying materials are made available under
# the terms of the Eclipse Public License v1.0 which accompanies this
# distribution and is available at:
#
#     http://www.eclipse.org/legal/epl-v10.html
#
# Contributors:
#     Ron Frederick - initial implementation, API, and documentation

"""SSH connection handlers"""

import asyncio
import getpass
import io
import os
import socket
import sys
import time

from collections import OrderedDict
from functools import partial

from .agent import connect_agent, create_agent_listener

from .auth import lookup_client_auth
from .auth import get_server_auth_methods, lookup_server_auth

from .auth_keys import read_authorized_keys

from .channel import SSHClientChannel, SSHServerChannel
from .channel import SSHTCPChannel, SSHUNIXChannel
from .channel import SSHX11Channel, SSHAgentChannel

from .client import SSHClient

from .compression import get_compression_algs, get_compression_params
from .compression import get_compressor, get_decompressor

from .constants import DEFAULT_LANG
from .constants import DISC_BY_APPLICATION, DISC_CONNECTION_LOST
from .constants import DISC_KEY_EXCHANGE_FAILED, DISC_HOST_KEY_NOT_VERIFYABLE
from .constants import DISC_MAC_ERROR, DISC_NO_MORE_AUTH_METHODS_AVAILABLE
from .constants import DISC_PROTOCOL_ERROR, DISC_SERVICE_NOT_AVAILABLE
from .constants import EXTENDED_DATA_STDERR
from .constants import MSG_DISCONNECT, MSG_IGNORE, MSG_UNIMPLEMENTED, MSG_DEBUG
from .constants import MSG_SERVICE_REQUEST, MSG_SERVICE_ACCEPT, MSG_EXT_INFO
from .constants import MSG_CHANNEL_OPEN, MSG_CHANNEL_OPEN_CONFIRMATION
from .constants import MSG_CHANNEL_OPEN_FAILURE
from .constants import MSG_CHANNEL_FIRST, MSG_CHANNEL_LAST
from .constants import MSG_KEXINIT, MSG_NEWKEYS, MSG_KEX_FIRST, MSG_KEX_LAST
from .constants import MSG_USERAUTH_REQUEST, MSG_USERAUTH_FAILURE
from .constants import MSG_USERAUTH_SUCCESS, MSG_USERAUTH_BANNER
from .constants import MSG_USERAUTH_FIRST, MSG_USERAUTH_LAST
from .constants import MSG_GLOBAL_REQUEST, MSG_REQUEST_SUCCESS
from .constants import MSG_REQUEST_FAILURE
from .constants import OPEN_ADMINISTRATIVELY_PROHIBITED, OPEN_CONNECT_FAILED
from .constants import OPEN_UNKNOWN_CHANNEL_TYPE

from .encryption import get_encryption_algs, get_encryption_params
from .encryption import get_encryption

from .forward import SSHForwarder

from .gss import GSSClient, GSSServer, GSSError

from .kex import get_kex_algs, expand_kex_algs, get_kex

from .known_hosts import match_known_hosts

from .listener import SSHTCPClientListener, SSHUNIXClientListener
from .listener import create_tcp_forward_listener, create_unix_forward_listener
from .listener import create_socks_listener

from .logging import logger

from .mac import get_mac_algs

from .misc import ChannelOpenError, DisconnectError, PasswordChangeRequired
from .misc import async_context_manager, create_task, get_symbol_names
from .misc import ip_address, map_handler_name

from .packet import Boolean, Byte, NameList, String, UInt32
from .packet import PacketDecodeError, SSHPacket, SSHPacketHandler

from .process import PIPE, SSHClientProcess, SSHServerProcess

from .public_key import CERT_TYPE_HOST, CERT_TYPE_USER, KeyImportError
from .public_key import decode_ssh_public_key, decode_ssh_certificate
from .public_key import get_public_key_algs, get_certificate_algs
from .public_key import get_x509_certificate_algs
from .public_key import load_keypairs, load_default_keypairs, load_certificates

from .saslprep import saslprep, SASLPrepError

from .server import SSHServer

from .sftp import SFTPServer, start_sftp_client

from .stream import SSHClientStreamSession, SSHServerStreamSession
from .stream import SSHTCPStreamSession, SSHUNIXStreamSession
from .stream import SSHReader, SSHWriter

from .x11 import create_x11_client_listener, create_x11_server_listener


# SSH default port
_DEFAULT_PORT = 22

# SSH service names
_USERAUTH_SERVICE = b'ssh-userauth'
_CONNECTION_SERVICE = b'ssh-connection'

# Default rekey parameters
_DEFAULT_REKEY_BYTES = 1 << 30      # 1 GiB
_DEFAULT_REKEY_SECONDS = 3600       # 1 hour

# Default login timeout
_DEFAULT_LOGIN_TIMEOUT = 120        # 2 minutes

# Default channel parameters
_DEFAULT_WINDOW = 2*1024*1024       # 2 MiB
_DEFAULT_MAX_PKTSIZE = 32768        # 32 kiB

# Default line editor parameters
_DEFAULT_LINE_HISTORY = 1000        # 1000 lines


def _validate_version(version):
    """Validate requested SSH version"""

    if version == ():
        from .version import __version__

        version = b'AsyncSSH_' + __version__.encode('ascii')
    else:
        if isinstance(version, str):
            version = version.encode('ascii')

        # Version including 'SSH-2.0-' and CRLF must be 255 chars or less
        if len(version) > 245:
            raise ValueError('Version string is too long')

        for b in version:
            if b < 0x20 or b > 0x7e:
                raise ValueError('Version string must be printable ASCII')

    return version


def _select_algs(alg_type, algs, possible_algs, none_value=None):
    """Select a set of allowed algorithms"""

    if algs == ():
        return possible_algs
    elif algs:
        result = []

        for alg_str in algs:
            alg = alg_str.encode('ascii')
            if alg not in possible_algs:
                raise ValueError('%s is not a valid %s algorithm' %
                                 (alg_str, alg_type))

            result.append(alg)

        return result
    elif none_value:
        return [none_value]
    else:
        raise ValueError('No %s algorithms selected' % alg_type)


def _validate_algs(kex_algs, enc_algs, mac_algs, cmp_algs,
                   sig_algs, allow_x509):
    """Validate requested algorithms"""

    kex_algs = _select_algs('key exchange', kex_algs, get_kex_algs())
    enc_algs = _select_algs('encryption', enc_algs, get_encryption_algs())
    mac_algs = _select_algs('MAC', mac_algs, get_mac_algs())
    cmp_algs = _select_algs('compression', cmp_algs,
                            get_compression_algs(), b'none')

    allowed_sig_algs = get_x509_certificate_algs() if allow_x509 else []
    allowed_sig_algs = allowed_sig_algs + get_public_key_algs()

    sig_algs = _select_algs('signature', sig_algs, allowed_sig_algs)

    return kex_algs, enc_algs, mac_algs, cmp_algs, sig_algs


class SSHConnection(SSHPacketHandler):
    """Parent class for SSH connections"""

    _handler_names = get_symbol_names(globals(), 'MSG_')

    next_conn = 0    # Next connection number, for logging

    @staticmethod
    def _get_next_conn():
        """Return the next available connection number (for logging)"""

        next_conn = SSHConnection.next_conn
        SSHConnection.next_conn += 1
        return next_conn

    def __init__(self, protocol_factory, loop, version, x509_trusted_certs,
                 x509_trusted_cert_paths, x509_purposes, kex_algs,
                 encryption_algs, mac_algs, compression_algs, signature_algs,
                 rekey_bytes, rekey_seconds, server):
        self._protocol_factory = protocol_factory
        self._loop = loop
        self._transport = None
        self._local_addr = None
        self._local_port = None
        self._peer_addr = None
        self._peer_port = None
        self._owner = None
        self._extra = {}
        self._server = server
        self._inpbuf = b''
        self._packet = b''
        self._pktlen = 0

        self._version = version
        self._client_version = b''
        self._server_version = b''
        self._client_kexinit = b''
        self._server_kexinit = b''
        self._session_id = None

        self._send_seq = 0
        self._send_encryption = None
        self._send_enchdrlen = 5
        self._send_blocksize = 8
        self._compressor = None
        self._compress_after_auth = False
        self._deferred_packets = []

        self._recv_handler = self._recv_version
        self._recv_seq = 0
        self._recv_encryption = None
        self._recv_blocksize = 8
        self._recv_macsize = 0
        self._decompressor = None
        self._decompress_after_auth = None
        self._next_recv_encryption = None
        self._next_recv_blocksize = 0
        self._next_recv_macsize = 0
        self._next_decompressor = None
        self._next_decompress_after_auth = None

        self._trusted_host_keys = set()
        self._trusted_host_key_algs = []
        self._trusted_ca_keys = set()
        self._revoked_host_keys = set()

        self._x509_trusted_certs = x509_trusted_certs
        self._x509_trusted_cert_paths = x509_trusted_cert_paths
        self._x509_revoked_certs = []
        self._x509_trusted_subjects = []
        self._x509_revoked_subjects = []
        self._x509_purposes = x509_purposes

        self._kex_algs = kex_algs
        self._enc_algs = encryption_algs
        self._mac_algs = mac_algs
        self._cmp_algs = compression_algs
        self._sig_algs = signature_algs

        self._kex = None
        self._kexinit_sent = False
        self._kex_complete = False
        self._ignore_first_kex = False

        self._gss = None
        self._gss_kex_auth = False
        self._gss_mic_auth = False

        self._rekey_bytes = rekey_bytes
        self._rekey_bytes_sent = 0
        self._rekey_seconds = rekey_seconds
        self._rekey_time = time.time() + rekey_seconds

        self._enc_alg_cs = None
        self._enc_alg_sc = None

        self._mac_alg_cs = None
        self._mac_alg_sc = None

        self._cmp_alg_cs = None
        self._cmp_alg_sc = None

        self._can_send_ext_info = False
        self._extensions_sent = OrderedDict()

        self._server_sig_algs = ()

        self._next_service = None

        self._agent = None
        self._auth = None
        self._auth_in_progress = False
        self._auth_complete = False
        self._auth_methods = [b'none']
        self._auth_waiter = None
        self._username = None

        self._channels = {}
        self._next_recv_chan = 0

        self._global_request_queue = []
        self._global_request_waiters = []

        self._local_listeners = {}

        self._x11_listener = None

        self._close_event = asyncio.Event(loop=loop)

        self._server_host_key_algs = []

        self._logger = logger.get_child(context='conn=%d' %
                                        self._get_next_conn())

    def __enter__(self):
        """Allow SSHConnection to be used as a context manager"""

        return self

    def __exit__(self, *exc_info):
        """Automatically close the connection when used as a context manager"""

        try:
            self.close()
        except RuntimeError as exc: # pragma: no cover
            # There's a race in some cases between the close call here
            # and the code which shuts down the event loop. Since the
            # loop.is_closed() method is only in Python 3.4.2 and later,
            # catch and ignore the RuntimeError for now if this happens.

            if exc.args[0] == 'Event loop is closed':
                pass
            else:
                raise

    @asyncio.coroutine
    def __aenter__(self):
        """Allow SSHConnection to be used as an async context manager"""

        return self

    @asyncio.coroutine
    def __aexit__(self, *exc_info):
        """Wait for connection close when used as an async context manager"""

        self.__exit__()
        yield from self.wait_closed()

    @property
    def logger(self):
        """A logger associated with this connection"""

        return self._logger

    def _cleanup(self, exc):
        """Clean up this connection"""

        for chan in list(self._channels.values()):
            chan.process_connection_close(exc)

        for listener in self._local_listeners.values():
            listener.close()

        while self._global_request_waiters:
            self._process_global_response(MSG_REQUEST_FAILURE, None,
                                          SSHPacket(b''))

        if self._auth:
            self._auth.cancel()
            self._auth = None

        if self._owner: # pragma: no branch
            self._owner.connection_lost(exc)
            self._owner = None

        self._close_event.set()

        self._inpbuf = b''
        self._recv_handler = None

    def _force_close(self, exc):
        """Force this connection to close immediately"""

        if not self._transport:
            return

        self._transport.abort()
        self._transport = None

        self._loop.call_soon(self._cleanup, exc)

    def _reap_task(self, task_logger, task):
        """Collect result of an async task, reporting errors"""

        # pylint: disable=broad-except
        try:
            task.result()
        except asyncio.CancelledError:
            pass
        except DisconnectError as exc:
            self._send_disconnect(exc.code, exc.reason, exc.lang)
            self._force_close(exc)
        except Exception:
            self.internal_error(error_logger=task_logger)

    def create_task(self, coro, task_logger=None):
        """Create an asynchronous task which catches and reports errors"""

        task = create_task(coro, loop=self._loop)
        task.add_done_callback(partial(self._reap_task, task_logger))
        return task

    def is_client(self):
        """Return if this is a client connection"""

        return not self._server

    def is_server(self):
        """Return if this is a server connection"""

        return self._server

    def get_owner(self):
        """Return the SSHClient or SSHServer which owns this connection"""

        return self._owner

    def get_hash_prefix(self):
        """Return the bytes used in calculating unique connection hashes

           This methods returns a packetized version of the client and
           server version and kexinit strings which is needed to perform
           key exchange hashes.

        """

        return b''.join((String(self._client_version),
                         String(self._server_version),
                         String(self._client_kexinit),
                         String(self._server_kexinit)))

    def _match_known_hosts(self, known_hosts, host, addr, port):
        """Determine the set of trusted host keys and certificates"""

        trusted_host_keys, trusted_ca_keys, revoked_host_keys, \
            trusted_x509_certs, revoked_x509_certs, \
            trusted_x509_subjects, revoked_x509_subjects = \
                match_known_hosts(known_hosts, host, addr, port)

        for key in trusted_host_keys:
            self._trusted_host_keys.add(key)

            if key.algorithm not in self._trusted_host_key_algs:
                self._trusted_host_key_algs.extend(key.sig_algorithms)

        self._trusted_ca_keys = set(trusted_ca_keys)
        self._revoked_host_keys = set(revoked_host_keys)

        if self._x509_trusted_certs is not None:
            self._x509_trusted_certs = list(self._x509_trusted_certs)
            self._x509_trusted_certs.extend(trusted_x509_certs)
            self._x509_revoked_certs = set(revoked_x509_certs)

            self._x509_trusted_subjects = trusted_x509_subjects
            self._x509_revoked_subjects = revoked_x509_subjects

    def _validate_openssh_host_certificate(self, host, cert):
        """Validate an OpenSSH host certificate"""

        if cert.signing_key in self._revoked_host_keys:
            raise ValueError('Host CA key is revoked')

        if self._trusted_ca_keys is not None and \
           cert.signing_key not in self._trusted_ca_keys:
            raise ValueError('Host CA key is not trusted')

        cert.validate(CERT_TYPE_HOST, host)

        return cert.key

    def _validate_x509_host_certificate_chain(self, host, cert):
        """Validate an X.509 host certificate"""

        if (self._x509_revoked_subjects and
                any(pattern.matches(cert.subject)
                    for pattern in self._x509_revoked_subjects)):
            raise ValueError('X.509 subject name is revoked')

        if (self._x509_trusted_subjects and
                not any(pattern.matches(cert.subject)
                        for pattern in self._x509_trusted_subjects)):
            raise ValueError('X.509 subject name is not trusted')

        # Only validate hostname against X.509 certificate host
        # principals when there are no X.509 trusted subject
        # entries matched in known_hosts.
        if self._x509_trusted_subjects:
            host = None

        cert.validate_chain(self._x509_trusted_certs,
                            self._x509_trusted_cert_paths,
                            self._x509_revoked_certs,
                            self._x509_purposes,
                            host_principal=host)

        return cert.key

    def _validate_host_key(self, host, key_data):
        """Validate and return a trusted host key"""

        try:
            cert = decode_ssh_certificate(key_data)
        except KeyImportError:
            pass
        else:
            if cert.is_x509_chain:
                return self._validate_x509_host_certificate_chain(host, cert)
            else:
                return self._validate_openssh_host_certificate(host, cert)

        try:
            key = decode_ssh_public_key(key_data)
        except KeyImportError:
            pass
        else:
            if key in self._revoked_host_keys:
                raise ValueError('Host key is revoked')

            if self._trusted_host_keys is not None and \
               key not in self._trusted_host_keys:
                raise ValueError('Host key is not trusted')

            return key

        raise ValueError('Unable to decode host key')

    def connection_made(self, transport):
        """Handle a newly opened connection"""

        self._transport = transport

        sock = transport.get_extra_info('socket')
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        sockname = transport.get_extra_info('sockname')
        self._local_addr, self._local_port = sockname[:2]

        peername = transport.get_extra_info('peername')
        self._peer_addr, self._peer_port = peername[:2]

        self._owner = self._protocol_factory()
        self._protocol_factory = None

        # pylint: disable=broad-except
        try:
            self._connection_made()
            self._owner.connection_made(self)
            self._send_version()
        except DisconnectError as exc:
            self._loop.call_soon(self.connection_lost, exc)
        except Exception:
            self._loop.call_soon(self.internal_error, sys.exc_info())

    def connection_lost(self, exc=None):
        """Handle the closing of a connection"""

        if exc is None and self._transport:
            exc = DisconnectError(DISC_CONNECTION_LOST, 'Connection lost')

        self._force_close(exc)

    def internal_error(self, exc_info=None, error_logger=None):
        """Handle a fatal error in connection processing"""

        if not exc_info:
            exc_info = sys.exc_info()

        if not error_logger:
            error_logger = self.logger

        error_logger.debug1('Uncaught exception', exc_info=exc_info)
        self._force_close(exc_info[1])

    def session_started(self):
        """Handle session start when opening tunneled SSH connection"""

        pass

    def data_received(self, data, datatype=None):
        """Handle incoming data on the connection"""

        # pylint: disable=unused-argument

        self._inpbuf += data

        # pylint: disable=broad-except
        try:
            while self._inpbuf and self._recv_handler():
                pass
        except DisconnectError as exc:
            self._send_disconnect(exc.code, exc.reason, exc.lang)
            self._force_close(exc)
        except Exception:
            self.internal_error()

    def eof_received(self):
        """Handle an incoming end of file on the connection"""

        self.connection_lost(None)

    def pause_writing(self):
        """Handle a request from the transport to pause writing data"""

        # Do nothing with this for now
        pass # pragma: no cover

    def resume_writing(self):
        """Handle a request from the transport to resume writing data"""

        # Do nothing with this for now
        pass # pragma: no cover

    def add_channel(self, chan):
        """Add a new channel, returning its channel number"""

        if not self._transport:
            raise ChannelOpenError(OPEN_CONNECT_FAILED,
                                   'SSH connection closed')

        while self._next_recv_chan in self._channels: # pragma: no cover
            self._next_recv_chan = (self._next_recv_chan + 1) & 0xffffffff

        recv_chan = self._next_recv_chan
        self._next_recv_chan = (self._next_recv_chan + 1) & 0xffffffff

        self._channels[recv_chan] = chan
        return recv_chan

    def remove_channel(self, recv_chan):
        """Remove the channel with the specified channel number"""

        del self._channels[recv_chan]

    def get_gss_context(self):
        """Return the GSS context associated with this connection"""

        return self._gss

    def enable_gss_kex_auth(self):
        """Enable GSS key exchange authentication"""

        self._gss_kex_auth = True

    def _choose_alg(self, alg_type, local_algs, remote_algs):
        """Choose a common algorithm from the client & server lists

           This method returns the earliest algorithm on the client's
           list which is supported by the server.

        """

        if self.is_client():
            client_algs, server_algs = local_algs, remote_algs
        else:
            client_algs, server_algs = remote_algs, local_algs

        for alg in client_algs:
            if alg in server_algs:
                return alg

        raise DisconnectError(DISC_KEY_EXCHANGE_FAILED,
                              'No matching %s algorithm found' % alg_type)

    def _get_ext_info_kex_alg(self):
        """Return the kex alg to add if any to request extension info"""

        return [b'ext-info-c'] if self.is_client() else []

    def _send(self, data):
        """Send data to the SSH connection"""

        if self._transport:
            self._transport.write(data)

    def _send_version(self):
        """Start the SSH handshake"""

        version = b'SSH-2.0-' + self._version

        if self.is_client():
            self._client_version = version
            self._extra.update(client_version=version.decode('ascii'))
        else:
            self._server_version = version
            self._extra.update(server_version=version.decode('ascii'))

        self._send(version + b'\r\n')

    def _recv_version(self):
        """Receive and parse the remote SSH version"""

        idx = self._inpbuf.find(b'\n')
        if idx < 0:
            return False

        version = self._inpbuf[:idx]
        if version.endswith(b'\r'):
            version = version[:-1]

        self._inpbuf = self._inpbuf[idx+1:]

        if (version.startswith(b'SSH-2.0-') or
                (self.is_client() and version.startswith(b'SSH-1.99-'))):
            # Accept version 2.0, or 1.99 if we're a client
            if self.is_server():
                self._client_version = version
                self._extra.update(client_version=version.decode('ascii'))
            else:
                self._server_version = version
                self._extra.update(server_version=version.decode('ascii'))

            self._send_kexinit()
            self._kexinit_sent = True
            self._recv_handler = self._recv_pkthdr
        elif self.is_client() and not version.startswith(b'SSH-'):
            # As a client, ignore the line if it doesn't appear to be a version
            pass
        else:
            # Otherwise, reject the unknown version
            self._force_close(DisconnectError(DISC_PROTOCOL_ERROR,
                                              'Unknown SSH version'))
            return False

        return True

    def _recv_pkthdr(self):
        """Receive and parse an SSH packet header"""

        if len(self._inpbuf) < self._recv_blocksize:
            return False

        self._packet = self._inpbuf[:self._recv_blocksize]
        self._inpbuf = self._inpbuf[self._recv_blocksize:]

        if self._recv_encryption:
            self._packet, pktlen = \
                self._recv_encryption.decrypt_header(self._recv_seq,
                                                     self._packet, 4)
        else:
            pktlen = self._packet[:4]

        self._pktlen = int.from_bytes(pktlen, 'big')
        self._recv_handler = self._recv_packet
        return True

    def _recv_packet(self):
        """Receive the remainder of an SSH packet and process it"""

        rem = 4 + self._pktlen + self._recv_macsize - self._recv_blocksize
        if len(self._inpbuf) < rem:
            return False

        seq = self._recv_seq
        rest = self._inpbuf[:rem-self._recv_macsize]
        mac = self._inpbuf[rem-self._recv_macsize:rem]

        if self._recv_encryption:
            packet = self._recv_encryption.decrypt_packet(seq, self._packet,
                                                          rest, 4, mac)

            if not packet:
                raise DisconnectError(DISC_MAC_ERROR, 'MAC verification failed')
        else:
            packet = self._packet[4:] + rest

        self._inpbuf = self._inpbuf[rem:]
        self._packet = b''

        payload = packet[1:-packet[0]]

        if self._decompressor and (self._auth_complete or
                                   not self._decompress_after_auth):
            payload = self._decompressor.decompress(payload)

        packet = SSHPacket(payload)
        pkttype = packet.get_byte()
        handler = self
        skip_reason = ''
        exc_reason = ''

        if self._kex and MSG_KEX_FIRST <= pkttype <= MSG_KEX_LAST:
            if self._ignore_first_kex: # pragma: no cover
                skip_reason = 'ignored first kex'
                self._ignore_first_kex = False
            else:
                handler = self._kex
        elif (self._auth and
              MSG_USERAUTH_FIRST <= pkttype <= MSG_USERAUTH_LAST):
            handler = self._auth
        elif pkttype > MSG_USERAUTH_LAST and not self._auth_complete:
            skip_reason = 'invalid request before auth complete'
            exc_reason = 'Invalid request before authentication was complete'
        elif MSG_CHANNEL_FIRST <= pkttype <= MSG_CHANNEL_LAST:
            try:
                recv_chan = packet.get_uint32()
                handler = self._channels[recv_chan]
            except KeyError:
                skip_reason = 'invalid channel number'
                exc_reason = 'Invalid channel number %d received' % recv_chan
            except PacketDecodeError:
                skip_reason = 'incomplete channel request'
                exc_reason = 'Incomplete channel request received'

        handler.log_received_packet(pkttype, seq, packet, skip_reason)

        if not skip_reason:
            try:
                processed = handler.process_packet(pkttype, seq, packet)
            except PacketDecodeError as exc:
                raise DisconnectError(DISC_PROTOCOL_ERROR, str(exc)) from None

            if not processed:
                self.logger.debug1('Unknown packet type %d received', pkttype)
                self.send_packet(MSG_UNIMPLEMENTED, UInt32(seq))

        if exc_reason:
            raise DisconnectError(DISC_PROTOCOL_ERROR, exc_reason)

        if self._transport:
            self._recv_seq = (seq + 1) & 0xffffffff
            self._recv_handler = self._recv_pkthdr

        return True

    def send_packet(self, pkttype, *args, handler=None):
        """Send an SSH packet"""

        if (self._auth_complete and self._kex_complete and
                (self._rekey_bytes_sent >= self._rekey_bytes or
                 time.monotonic() >= self._rekey_time)):
            self._send_kexinit()
            self._kexinit_sent = True

        if (((pkttype in {MSG_SERVICE_REQUEST, MSG_SERVICE_ACCEPT} or
              pkttype > MSG_KEX_LAST) and not self._kex_complete) or
                (pkttype == MSG_USERAUTH_BANNER and
                 not (self._auth_in_progress or self._auth_complete)) or
                (pkttype > MSG_USERAUTH_LAST and not self._auth_complete)):
            self._deferred_packets.append((pkttype, args))
            return

        # If we're encrypting and we have no data outstanding, insert an
        # ignore packet into the stream
        if self._send_encryption and pkttype != MSG_IGNORE:
            self.send_packet(MSG_IGNORE, String(b''))

        payload = Byte(pkttype) + b''.join(args)
        log_data = payload

        if self._compressor and (self._auth_complete or
                                 not self._compress_after_auth):
            payload = self._compressor.compress(payload)

        padlen = -(self._send_enchdrlen + len(payload)) % self._send_blocksize
        if padlen < 4:
            padlen += self._send_blocksize

        packet = Byte(padlen) + payload + os.urandom(padlen)
        pktlen = len(packet)
        hdr = UInt32(pktlen)
        seq = self._send_seq

        if self._send_encryption:
            packet, mac = self._send_encryption.encrypt_packet(seq, hdr, packet)
        else:
            packet = hdr + packet
            mac = b''

        self._send(packet + mac)
        self._send_seq = (seq + 1) & 0xffffffff

        if self._kex_complete:
            self._rekey_bytes_sent += pktlen

        if not handler:
            handler = self

        handler.log_sent_packet(pkttype, seq, log_data)

    def _send_deferred_packets(self):
        """Send packets deferred due to key exchange or auth"""

        deferred_packets = self._deferred_packets
        self._deferred_packets = []

        for pkttype, args in deferred_packets:
            self.send_packet(pkttype, *args)

    def _send_disconnect(self, code, reason, lang):
        """Send a disconnect packet"""

        self.logger.info('Sending disconnect: %s (%d)', reason, code)

        self.send_packet(MSG_DISCONNECT, UInt32(code),
                         String(reason), String(lang))

    def _send_kexinit(self):
        """Start a key exchange"""

        self._kex_complete = False
        self._rekey_bytes_sent = 0
        self._rekey_time = time.monotonic() + self._rekey_seconds

        gss_mechs = self._gss.mechs if self._gss else []
        kex_algs = expand_kex_algs(self._kex_algs, gss_mechs,
                                   bool(self._server_host_key_algs))

        host_key_algs = self._server_host_key_algs or [b'null']

        self.logger.debug1('Requesting key exchange')
        self.logger.debug2('  Key exchange algs: %s', kex_algs)
        self.logger.debug2('  Host key algs: %s', host_key_algs)
        self.logger.debug2('  Encryption algs: %s', self._enc_algs)
        self.logger.debug2('  MAC algs: %s', self._mac_algs)
        self.logger.debug2('  Compression algs: %s', self._cmp_algs)

        cookie = os.urandom(16)
        kex_algs = NameList(kex_algs + self._get_ext_info_kex_alg())
        host_key_algs = NameList(host_key_algs)
        enc_algs = NameList(self._enc_algs)
        mac_algs = NameList(self._mac_algs)
        cmp_algs = NameList(self._cmp_algs)
        langs = NameList([])

        packet = b''.join((Byte(MSG_KEXINIT), cookie, kex_algs, host_key_algs,
                           enc_algs, enc_algs, mac_algs, mac_algs, cmp_algs,
                           cmp_algs, langs, langs, Boolean(False), UInt32(0)))

        if self.is_server():
            self._server_kexinit = packet
        else:
            self._client_kexinit = packet

        self.send_packet(MSG_KEXINIT, packet[1:])

    def _send_ext_info(self):
        """Send extension information"""

        packet = UInt32(len(self._extensions_sent))

        self.logger.debug2('Sending extension info')

        for name, value in self._extensions_sent.items():
            packet += String(name) + String(value)

            self.logger.debug2('  %s: %s', name, value)

        self.send_packet(MSG_EXT_INFO, packet)

    def send_newkeys(self, k, h):
        """Finish a key exchange and send a new keys message"""

        if not self._session_id:
            self._session_id = h

        enc_keysize_cs, enc_ivsize_cs, enc_blocksize_cs, \
        mac_keysize_cs, mac_hashsize_cs, etm_cs = \
            get_encryption_params(self._enc_alg_cs, self._mac_alg_cs)

        enc_keysize_sc, enc_ivsize_sc, enc_blocksize_sc, \
        mac_keysize_sc, mac_hashsize_sc, etm_sc = \
            get_encryption_params(self._enc_alg_sc, self._mac_alg_sc)

        if mac_keysize_cs == 0:
            self._mac_alg_cs = self._enc_alg_cs

        if mac_keysize_sc == 0:
            self._mac_alg_sc = self._enc_alg_sc

        cmp_after_auth_cs = get_compression_params(self._cmp_alg_cs)
        cmp_after_auth_sc = get_compression_params(self._cmp_alg_sc)

        self.logger.debug2('  Client to server:')
        self.logger.debug2('    Encryption alg: %s', self._enc_alg_cs)
        self.logger.debug2('    MAC alg: %s', self._mac_alg_cs)
        self.logger.debug2('    Compression alg: %s', self._cmp_alg_cs)
        self.logger.debug2('  Server to client:')
        self.logger.debug2('    Encryption alg: %s', self._enc_alg_sc)
        self.logger.debug2('    MAC alg: %s', self._mac_alg_sc)
        self.logger.debug2('    Compression alg: %s', self._cmp_alg_sc)

        iv_cs = self._kex.compute_key(k, h, b'A', self._session_id,
                                      enc_ivsize_cs)
        iv_sc = self._kex.compute_key(k, h, b'B', self._session_id,
                                      enc_ivsize_sc)
        enc_key_cs = self._kex.compute_key(k, h, b'C', self._session_id,
                                           enc_keysize_cs)
        enc_key_sc = self._kex.compute_key(k, h, b'D', self._session_id,
                                           enc_keysize_sc)
        mac_key_cs = self._kex.compute_key(k, h, b'E', self._session_id,
                                           mac_keysize_cs)
        mac_key_sc = self._kex.compute_key(k, h, b'F', self._session_id,
                                           mac_keysize_sc)
        self._kex = None

        next_enc_cs = get_encryption(self._enc_alg_cs, enc_key_cs, iv_cs,
                                     self._mac_alg_cs, mac_key_cs, etm_cs)
        next_enc_sc = get_encryption(self._enc_alg_sc, enc_key_sc, iv_sc,
                                     self._mac_alg_sc, mac_key_sc, etm_sc)

        self.send_packet(MSG_NEWKEYS)

        if self.is_client():
            self._send_encryption = next_enc_cs
            self._send_enchdrlen = 1 if etm_cs else 5
            self._send_blocksize = max(8, enc_blocksize_cs)
            self._compressor = get_compressor(self._cmp_alg_cs)
            self._compress_after_auth = cmp_after_auth_cs

            self._next_recv_encryption = next_enc_sc
            self._next_recv_blocksize = max(8, enc_blocksize_sc)
            self._next_recv_macsize = mac_hashsize_sc
            self._next_decompressor = get_decompressor(self._cmp_alg_sc)
            self._next_decompress_after_auth = cmp_after_auth_sc

            self._extra.update(
                send_cipher=self._enc_alg_cs.decode('ascii'),
                send_mac=self._mac_alg_cs.decode('ascii'),
                send_compression=self._cmp_alg_cs.decode('ascii'),
                recv_cipher=self._enc_alg_sc.decode('ascii'),
                recv_mac=self._mac_alg_sc.decode('ascii'),
                recv_compression=self._cmp_alg_sc.decode('ascii'))
        else:
            self._send_encryption = next_enc_sc
            self._send_enchdrlen = 1 if etm_sc else 5
            self._send_blocksize = max(8, enc_blocksize_sc)
            self._compressor = get_compressor(self._cmp_alg_sc)
            self._compress_after_auth = cmp_after_auth_sc

            self._next_recv_encryption = next_enc_cs
            self._next_recv_blocksize = max(8, enc_blocksize_cs)
            self._next_recv_macsize = mac_hashsize_cs
            self._next_decompressor = get_decompressor(self._cmp_alg_cs)
            self._next_decompress_after_auth = cmp_after_auth_cs

            self._extra.update(
                send_cipher=self._enc_alg_sc.decode('ascii'),
                send_mac=self._mac_alg_sc.decode('ascii'),
                send_compression=self._cmp_alg_sc.decode('ascii'),
                recv_cipher=self._enc_alg_cs.decode('ascii'),
                recv_mac=self._mac_alg_cs.decode('ascii'),
                recv_compression=self._cmp_alg_cs.decode('ascii'))

            self._next_service = _USERAUTH_SERVICE

            if self._can_send_ext_info:
                self._extensions_sent[b'server-sig-algs'] = \
                    b','.join(self._sig_algs)
                self._send_ext_info()
                self._can_send_ext_info = False

        self._kex_complete = True
        self._send_deferred_packets()

    def send_service_request(self, service):
        """Send a service request"""

        self.logger.debug2('Requesting service %s', service)

        self._next_service = service
        self.send_packet(MSG_SERVICE_REQUEST, String(service))

    def _get_userauth_request_packet(self, method, args):
        """Get packet data for a user authentication request"""

        return b''.join((Byte(MSG_USERAUTH_REQUEST), String(self._username),
                         String(_CONNECTION_SERVICE), String(method)) + args)

    def get_userauth_request_data(self, method, *args):
        """Get signature data for a user authentication request"""

        return (String(self._session_id) +
                self._get_userauth_request_packet(method, args))

    @asyncio.coroutine
    def send_userauth_request(self, method, *args, key=None):
        """Send a user authentication request"""

        packet = self._get_userauth_request_packet(method, args)

        if key:
            sig = key.sign(String(self._session_id) + packet)

            if asyncio.iscoroutine(sig):
                sig = yield from sig

            packet += String(sig)

        self.send_packet(MSG_USERAUTH_REQUEST, packet[1:])

    def send_userauth_failure(self, partial_success):
        """Send a user authentication failure response"""

        methods = get_server_auth_methods(self)

        self.logger.debug2('Remaining auth methods: %s', methods or 'None')

        self._auth = None
        self.send_packet(MSG_USERAUTH_FAILURE, NameList(methods),
                         Boolean(partial_success))

    def send_userauth_success(self):
        """Send a user authentication success response"""

        self.logger.info('Auth for user %s succeeded', self._username)

        self.send_packet(MSG_USERAUTH_SUCCESS)
        self._auth = None
        self._auth_in_progress = False
        self._auth_complete = True
        self._extra.update(username=self._username)
        self._send_deferred_packets()

        # This method is only in SSHServerConnection
        # pylint: disable=no-member
        self._cancel_login_timer()

    def send_channel_open_confirmation(self, send_chan, recv_chan,
                                       recv_window, recv_pktsize,
                                       *result_args):
        """Send a channel open confirmation"""

        self.send_packet(MSG_CHANNEL_OPEN_CONFIRMATION, UInt32(send_chan),
                         UInt32(recv_chan), UInt32(recv_window),
                         UInt32(recv_pktsize), *result_args)

    def send_channel_open_failure(self, send_chan, code, reason, lang):
        """Send a channel open failure"""

        self.send_packet(MSG_CHANNEL_OPEN_FAILURE, UInt32(send_chan),
                         UInt32(code), String(reason), String(lang))

    @asyncio.coroutine
    def _make_global_request(self, request, *args):
        """Send a global request and wait for the response"""

        if not self._transport:
            return MSG_REQUEST_FAILURE, SSHPacket(b'')

        waiter = asyncio.Future(loop=self._loop)
        self._global_request_waiters.append(waiter)

        self.send_packet(MSG_GLOBAL_REQUEST, String(request),
                         Boolean(True), *args)

        return (yield from waiter)

    def _report_global_response(self, result):
        """Report back the response to a previously issued global request"""

        _, _, want_reply = self._global_request_queue.pop(0)

        if want_reply: # pragma: no branch
            if result:
                response = b'' if result is True else result
                self.send_packet(MSG_REQUEST_SUCCESS, response)
            else:
                self.send_packet(MSG_REQUEST_FAILURE)

        if self._global_request_queue:
            self._service_next_global_request()

    def _service_next_global_request(self):
        """Process next item on global request queue"""

        handler, packet, _ = self._global_request_queue[0]
        if callable(handler):
            handler(packet)
        else:
            self._report_global_response(False)

    def _connection_made(self):
        """Handle the opening of a new connection"""

        raise NotImplementedError

    def _process_disconnect(self, pkttype, pktid, packet):
        """Process a disconnect message"""

        # pylint: disable=unused-argument

        code = packet.get_uint32()
        reason = packet.get_string()
        lang = packet.get_string()
        packet.check_end()

        try:
            reason = reason.decode('utf-8')
            lang = lang.decode('ascii')
        except UnicodeDecodeError:
            raise DisconnectError(DISC_PROTOCOL_ERROR,
                                  'Invalid disconnect message') from None

        self.logger.debug1('Received disconnect: %s (%d)', reason, code)

        if code != DISC_BY_APPLICATION:
            exc = DisconnectError(code, reason, lang)
        else:
            exc = None

        self._force_close(exc)

    def _process_ignore(self, pkttype, pktid, packet):
        """Process an ignore message"""

        # pylint: disable=no-self-use,unused-argument

        _ = packet.get_string()     # data
        packet.check_end()

        # Do nothing

    def _process_unimplemented(self, pkttype, pktid, packet):
        """Process an unimplemented message response"""

        # pylint: disable=no-self-use,unused-argument

        _ = packet.get_uint32()     # seq
        packet.check_end()

        # Ignore this

    def _process_debug(self, pkttype, pktid, packet):
        """Process a debug message"""

        # pylint: disable=unused-argument

        always_display = packet.get_boolean()
        msg = packet.get_string()
        lang = packet.get_string()
        packet.check_end()

        try:
            msg = msg.decode('utf-8')
            lang = lang.decode('ascii')
        except UnicodeDecodeError:
            raise DisconnectError(DISC_PROTOCOL_ERROR,
                                  'Invalid debug message') from None

        self.logger.debug1('Received debug message: %s%s', msg,
                           ' (always display)' if always_display else '')

        self._owner.debug_msg_received(msg, lang, always_display)

    def _process_service_request(self, pkttype, pktid, packet):
        """Process a service request"""

        # pylint: disable=unused-argument

        service = packet.get_string()
        packet.check_end()

        if service == self._next_service:
            self.logger.debug2('Accepting request for service %s', service)

            self._next_service = None
            self.send_packet(MSG_SERVICE_ACCEPT, String(service))

            if (self.is_server() and               # pragma: no branch
                    service == _USERAUTH_SERVICE):
                self._auth_in_progress = True
                self._send_deferred_packets()
        else:
            raise DisconnectError(DISC_SERVICE_NOT_AVAILABLE,
                                  'Unexpected service request received')

    def _process_service_accept(self, pkttype, pktid, packet):
        """Process a service accept response"""

        # pylint: disable=unused-argument

        service = packet.get_string()
        packet.check_end()

        if service == self._next_service:
            self.logger.debug2('Request for service %s accepted', service)

            self._next_service = None

            if (self.is_client() and               # pragma: no branch
                    service == _USERAUTH_SERVICE):
                self.logger.info('Beginning auth for user %s', self._username)

                self._auth_in_progress = True

                # This method is only in SSHClientConnection
                # pylint: disable=no-member
                self.try_next_auth()
        else:
            raise DisconnectError(DISC_SERVICE_NOT_AVAILABLE,
                                  'Unexpected service accept received')

    def _process_ext_info(self, pkttype, pktid, packet):
        """Process extension information"""

        # pylint: disable=unused-argument

        extensions = {}

        self.logger.debug2('Received extension info')

        num_extensions = packet.get_uint32()
        for _ in range(num_extensions):
            name = packet.get_string()
            value = packet.get_string()
            extensions[name] = value

            self.logger.debug2('  %s: %s', name, value)

        packet.check_end()

        if self.is_client():
            self._server_sig_algs = \
                extensions.get(b'server-sig-algs').split(b',')

    def _process_kexinit(self, pkttype, pktid, packet):
        """Process a key exchange request"""

        # pylint: disable=unused-argument

        if self._kex:
            raise DisconnectError(DISC_PROTOCOL_ERROR,
                                  'Key exchange already in progress')

        _ = packet.get_bytes(16)                        # cookie
        peer_kex_algs = packet.get_namelist()
        peer_host_key_algs = packet.get_namelist()
        enc_algs_cs = packet.get_namelist()
        enc_algs_sc = packet.get_namelist()
        mac_algs_cs = packet.get_namelist()
        mac_algs_sc = packet.get_namelist()
        cmp_algs_cs = packet.get_namelist()
        cmp_algs_sc = packet.get_namelist()
        _ = packet.get_namelist()                       # lang_cs
        _ = packet.get_namelist()                       # lang_sc
        first_kex_follows = packet.get_boolean()
        _ = packet.get_uint32()                         # reserved
        packet.check_end()

        if self.is_server():
            self._client_kexinit = packet.get_consumed_payload()

            if b'ext-info-c' in peer_kex_algs and not self._session_id:
                self._can_send_ext_info = True
        else:
            self._server_kexinit = packet.get_consumed_payload()

        if self._kexinit_sent:
            self._kexinit_sent = False
        else:
            self._send_kexinit()

        if self._gss:
            self._gss.reset()

        gss_mechs = self._gss.mechs if self._gss else []
        kex_algs = expand_kex_algs(self._kex_algs, gss_mechs,
                                   bool(self._server_host_key_algs))

        self.logger.debug1('Received key exchange request')
        self.logger.debug2('  Key exchange algs: %s', peer_kex_algs)
        self.logger.debug2('  Host key algs: %s', peer_host_key_algs)
        self.logger.debug2('  Client to server:')
        self.logger.debug2('    Encryption algs: %s', enc_algs_cs)
        self.logger.debug2('    MAC algs: %s', mac_algs_cs)
        self.logger.debug2('    Compression algs: %s', cmp_algs_cs)
        self.logger.debug2('  Server to client:')
        self.logger.debug2('    Encryption algs: %s', enc_algs_sc)
        self.logger.debug2('    MAC algs: %s', mac_algs_sc)
        self.logger.debug2('    Compression algs: %s', cmp_algs_sc)

        kex_alg = self._choose_alg('key exchange', kex_algs, peer_kex_algs)
        self._kex = get_kex(self, kex_alg)
        self._ignore_first_kex = (first_kex_follows and
                                  self._kex.algorithm != peer_kex_algs[0])

        if self.is_server():
            # This method is only in SSHServerConnection
            # pylint: disable=no-member
            if (not self._choose_server_host_key(peer_host_key_algs) and
                    not kex_alg.startswith(b'gss-')):
                raise DisconnectError(DISC_KEY_EXCHANGE_FAILED, 'Unable '
                                      'to find compatible server host key')

        self._enc_alg_cs = self._choose_alg('encryption', self._enc_algs,
                                            enc_algs_cs)
        self._enc_alg_sc = self._choose_alg('encryption', self._enc_algs,
                                            enc_algs_sc)

        self._mac_alg_cs = self._choose_alg('MAC', self._mac_algs, mac_algs_cs)
        self._mac_alg_sc = self._choose_alg('MAC', self._mac_algs, mac_algs_sc)

        self._cmp_alg_cs = self._choose_alg('compression', self._cmp_algs,
                                            cmp_algs_cs)
        self._cmp_alg_sc = self._choose_alg('compression', self._cmp_algs,
                                            cmp_algs_sc)

        self.logger.debug1('Beginning key exchange')
        self.logger.debug2('  Key exchange alg: %s', self._kex.algorithm)

        self._kex.start()

    def _process_newkeys(self, pkttype, pktid, packet):
        """Process a new keys message, finishing a key exchange"""

        # pylint: disable=unused-argument

        packet.check_end()

        if self._next_recv_encryption:
            self._recv_encryption = self._next_recv_encryption
            self._recv_blocksize = self._next_recv_blocksize
            self._recv_macsize = self._next_recv_macsize
            self._decompressor = self._next_decompressor
            self._decompress_after_auth = self._next_decompress_after_auth

            self._next_recv_encryption = None
        else:
            raise DisconnectError(DISC_PROTOCOL_ERROR,
                                  'New keys not negotiated')

        self.logger.debug1('Completed key exchange')

        if self.is_client() and not (self._auth_in_progress or
                                     self._auth_complete):
            self.send_service_request(_USERAUTH_SERVICE)

    def _process_userauth_request(self, pkttype, pktid, packet):
        """Process a user authentication request"""

        # pylint: disable=unused-argument

        username = packet.get_string()
        service = packet.get_string()
        method = packet.get_string()

        if service != _CONNECTION_SERVICE:
            raise DisconnectError(DISC_SERVICE_NOT_AVAILABLE,
                                  'Unexpected service in auth request')

        try:
            username = saslprep(username.decode('utf-8'))
        except (UnicodeDecodeError, SASLPrepError):
            raise DisconnectError(DISC_PROTOCOL_ERROR,
                                  'Invalid auth request message') from None

        if self.is_client():
            raise DisconnectError(DISC_PROTOCOL_ERROR,
                                  'Unexpected userauth request')
        elif self._auth_complete:
            # Silently ignore requests if we're already authenticated
            pass
        else:
            if username != self._username:
                self.logger.info('Beginning auth for user %s', username)

                self._username = username

                result = self._owner.begin_auth(username)
            else:
                result = True

            self.create_task(self._finish_userauth(result, method, packet))

    @asyncio.coroutine
    def _finish_userauth(self, result, method, packet):
        """Finish processing a user authentication request"""

        if asyncio.iscoroutine(result):
            result = yield from result

        if not result:
            self.send_userauth_success()
            return

        if self._auth:
            self._auth.cancel()

        self._auth = lookup_server_auth(self, self._username, method, packet)

    def _process_userauth_failure(self, pkttype, pktid, packet):
        """Process a user authentication failure response"""

        # pylint: disable=unused-argument

        self._auth_methods = packet.get_namelist()
        partial_success = packet.get_boolean()
        packet.check_end()

        self.logger.debug2('Remaining auth methods: %s',
                           self._auth_methods or 'None')

        if self.is_client() and self._auth:
            if partial_success: # pragma: no cover
                # Partial success not implemented yet
                self._auth.auth_succeeded()
            else:
                self._auth.auth_failed()

            # This method is only in SSHClientConnection
            # pylint: disable=no-member
            self.try_next_auth()
        else:
            raise DisconnectError(DISC_PROTOCOL_ERROR,
                                  'Unexpected userauth response')

    def _process_userauth_success(self, pkttype, pktid, packet):
        """Process a user authentication success response"""

        # pylint: disable=unused-argument

        packet.check_end()

        if self.is_client() and self._auth:
            self.logger.info('Auth for user %s succeeded', self._username)

            self._auth.auth_succeeded()
            self._auth.cancel()
            self._auth = None
            self._auth_in_progress = False
            self._auth_complete = True

            if self._agent:
                self._agent.close()
                self._agent = None

            self._extra.update(username=self._username)
            self._send_deferred_packets()

            self._owner.auth_completed()

            if not self._auth_waiter.cancelled(): # pragma: no branch
                self._auth_waiter.set_result(None)

            self._auth_waiter = None
        else:
            raise DisconnectError(DISC_PROTOCOL_ERROR,
                                  'Unexpected userauth response')

    def _process_userauth_banner(self, pkttype, pktid, packet):
        """Process a user authentication banner message"""

        # pylint: disable=unused-argument

        msg = packet.get_string()
        lang = packet.get_string()
        packet.check_end()

        try:
            msg = msg.decode('utf-8')
            lang = lang.decode('ascii')
        except UnicodeDecodeError:
            raise DisconnectError(DISC_PROTOCOL_ERROR,
                                  'Invalid userauth banner') from None

        self.logger.debug1('Received authentication banner')

        if self.is_client():
            self._owner.auth_banner_received(msg, lang)
        else:
            raise DisconnectError(DISC_PROTOCOL_ERROR,
                                  'Unexpected userauth banner')

    def _process_global_request(self, pkttype, pktid, packet):
        """Process a global request"""

        # pylint: disable=unused-argument

        request = packet.get_string()
        want_reply = packet.get_boolean()

        try:
            request = request.decode('ascii')
        except UnicodeDecodeError:
            raise DisconnectError(DISC_PROTOCOL_ERROR,
                                  'Invalid global request') from None

        name = '_process_' + map_handler_name(request) + '_global_request'
        handler = getattr(self, name, None)

        if not handler:
            self.logger.debug1('Received unknown global request: %s', request)

        self._global_request_queue.append((handler, packet, want_reply))
        if len(self._global_request_queue) == 1:
            self._service_next_global_request()

    def _process_global_response(self, pkttype, pktid, packet):
        """Process a global response"""

        # pylint: disable=unused-argument

        if self._global_request_waiters:
            waiter = self._global_request_waiters.pop(0)
            if not waiter.cancelled(): # pragma: no branch
                waiter.set_result((pkttype, packet))
        else:
            raise DisconnectError(DISC_PROTOCOL_ERROR,
                                  'Unexpected global response')

    def _process_channel_open(self, pkttype, pktid, packet):
        """Process a channel open request"""

        # pylint: disable=unused-argument

        chantype = packet.get_string()
        send_chan = packet.get_uint32()
        send_window = packet.get_uint32()
        send_pktsize = packet.get_uint32()

        try:
            chantype = chantype.decode('ascii')
        except UnicodeDecodeError:
            raise DisconnectError(DISC_PROTOCOL_ERROR,
                                  'Invalid channel open request') from None

        try:
            name = '_process_' + map_handler_name(chantype) + '_open'
            handler = getattr(self, name, None)
            if callable(handler):
                chan, session = handler(packet)
                chan.process_open(send_chan, send_window,
                                  send_pktsize, session)
            else:
                raise ChannelOpenError(OPEN_UNKNOWN_CHANNEL_TYPE,
                                       'Unknown channel type')
        except ChannelOpenError as exc:
            self.logger.debug1('Open failed for channel type %s: %s',
                               chantype, exc.reason)

            self.send_channel_open_failure(send_chan, exc.code,
                                           exc.reason, exc.lang)

    def _process_channel_open_confirmation(self, pkttype, pktid, packet):
        """Process a channel open confirmation response"""

        # pylint: disable=unused-argument

        recv_chan = packet.get_uint32()
        send_chan = packet.get_uint32()
        send_window = packet.get_uint32()
        send_pktsize = packet.get_uint32()

        chan = self._channels.get(recv_chan)
        if chan:
            chan.process_open_confirmation(send_chan, send_window,
                                           send_pktsize, packet)
        else:
            self.logger.debug1('Received open confirmation for unknown '
                               'channel %d', recv_chan)

            raise DisconnectError(DISC_PROTOCOL_ERROR,
                                  'Invalid channel number')

    def _process_channel_open_failure(self, pkttype, pktid, packet):
        """Process a channel open failure response"""

        # pylint: disable=unused-argument

        recv_chan = packet.get_uint32()
        code = packet.get_uint32()
        reason = packet.get_string()
        lang = packet.get_string()
        packet.check_end()

        try:
            reason = reason.decode('utf-8')
            lang = lang.decode('ascii')
        except UnicodeDecodeError:
            raise DisconnectError(DISC_PROTOCOL_ERROR,
                                  'Invalid channel open failure') from None

        chan = self._channels.get(recv_chan)
        if chan:
            chan.process_open_failure(code, reason, lang)
        else:
            self.logger.debug1('Received open failure for unknown '
                               'channel %d', recv_chan)

            raise DisconnectError(DISC_PROTOCOL_ERROR,
                                  'Invalid channel number')

    _packet_handlers = {
        MSG_DISCONNECT:                 _process_disconnect,
        MSG_IGNORE:                     _process_ignore,
        MSG_UNIMPLEMENTED:              _process_unimplemented,
        MSG_DEBUG:                      _process_debug,
        MSG_SERVICE_REQUEST:            _process_service_request,
        MSG_SERVICE_ACCEPT:             _process_service_accept,
        MSG_EXT_INFO:                   _process_ext_info,

        MSG_KEXINIT:                    _process_kexinit,
        MSG_NEWKEYS:                    _process_newkeys,

        MSG_USERAUTH_REQUEST:           _process_userauth_request,
        MSG_USERAUTH_FAILURE:           _process_userauth_failure,
        MSG_USERAUTH_SUCCESS:           _process_userauth_success,
        MSG_USERAUTH_BANNER:            _process_userauth_banner,

        MSG_GLOBAL_REQUEST:             _process_global_request,
        MSG_REQUEST_SUCCESS:            _process_global_response,
        MSG_REQUEST_FAILURE:            _process_global_response,

        MSG_CHANNEL_OPEN:               _process_channel_open,
        MSG_CHANNEL_OPEN_CONFIRMATION:  _process_channel_open_confirmation,
        MSG_CHANNEL_OPEN_FAILURE:       _process_channel_open_failure
    }

    def abort(self):
        """Forcibly close the SSH connection

           This method closes the SSH connection immediately, without
           waiting for pending operations to complete and wihtout sending
           an explicit SSH disconnect message. Buffered data waiting to be
           sent will be lost and no more data will be received. When the
           the connection is closed, :meth:`connection_lost()
           <SSHClient.connection_lost>` on the associated :class:`SSHClient`
           object will be called with the value `None`.

        """

        self.logger.info('Aborting connection')

        self._force_close(None)

    def close(self):
        """Cleanly close the SSH connection

           This method calls :meth:`disconnect` with the reason set to
           indicate that the connection was closed explicitly by the
           application.

        """

        self.logger.info('Closing connection')

        self.disconnect(DISC_BY_APPLICATION, 'Disconnected by application')

    @asyncio.coroutine
    def wait_closed(self):
        """Wait for this connection to close

           This method is a coroutine which can be called to block until
           this connection has finished closing.

        """

        yield from self._close_event.wait()

    def disconnect(self, code, reason, lang=DEFAULT_LANG):
        """Disconnect the SSH connection

           This method sends a disconnect message and closes the SSH
           connection after buffered data waiting to be written has been
           sent. No more data will be received. When the connection is
           fully closed, :meth:`connection_lost() <SSHClient.connection_lost>`
           on the associated :class:`SSHClient` or :class:`SSHServer` object
           will be called with the value `None`.

           :param code:
               The reason for the disconnect, from
               :ref:`disconnect reason codes <DisconnectReasons>`
           :param reason:
               A human readable reason for the disconnect
           :param lang:
               The language the reason is in
           :type code: `int`
           :type reason: `str`
           :type lang: `str`

        """

        if not self._transport:
            return

        for chan in list(self._channels.values()):
            chan.close()

        self._send_disconnect(code, reason, lang)

        self._transport.close()
        self._transport = None

        self._loop.call_soon(self._cleanup, None)

    def get_extra_info(self, name, default=None):
        """Get additional information about the connection

           This method returns extra information about the connection once
           it is established. Supported values include everything supported
           by a socket transport plus:

             | username
             | client_version
             | server_version
             | send_cipher
             | send_mac
             | send_compression
             | recv_cipher
             | recv_mac
             | recv_compression

           See :meth:`get_extra_info() <asyncio.BaseTransport.get_extra_info>`
           in :class:`asyncio.BaseTransport` for more information.

        """

        return self._extra.get(name,
                               self._transport.get_extra_info(name, default)
                               if self._transport else default)

    def send_debug(self, msg, lang=DEFAULT_LANG, always_display=False):
        """Send a debug message on this connection

           This method can be called to send a debug message to the
           other end of the connection.

           :param msg:
               The debug message to send
           :param lang:
               The language the message is in
           :param always_display:
               Whether or not to display the message
           :type msg: `str`
           :type lang: `str`
           :type always_display: `bool`

        """

        self.logger.debug1('Sending debug message: %s%s', msg,
                           ' (always display)' if always_display else '')

        self.send_packet(MSG_DEBUG, Boolean(always_display),
                         String(msg), String(lang))

    def create_tcp_channel(self, encoding=None, window=_DEFAULT_WINDOW,
                           max_pktsize=_DEFAULT_MAX_PKTSIZE):
        """Create an SSH TCP channel for a new direct TCP connection

           This method can be called by :meth:`connection_requested()
           <SSHServer.connection_requested>` to create an
           :class:`SSHTCPChannel` with the desired encoding, window, and
           max packet size for a newly created SSH direct connection.

           :param encoding: (optional)
               The Unicode encoding to use for data exchanged on the
               connection. This defaults to `None`, allowing the
               application to send and receive raw bytes.
           :param window: (optional)
               The receive window size for this session
           :param max_pktsize: (optional)
               The maximum packet size for this session
           :type encoding: `str`
           :type window: `int`
           :type max_pktsize: `int`

           :returns: :class:`SSHTCPChannel`

        """

        return SSHTCPChannel(self, self._loop, encoding, window, max_pktsize)

    def create_unix_channel(self, encoding=None, window=_DEFAULT_WINDOW,
                            max_pktsize=_DEFAULT_MAX_PKTSIZE):
        """Create an SSH UNIX channel for a new direct UNIX domain connection

           This method can be called by :meth:`unix_connection_requested()
           <SSHServer.unix_connection_requested>` to create an
           :class:`SSHUNIXChannel` with the desired encoding, window, and
           max packet size for a newly created SSH direct UNIX domain
           socket connection.

           :param encoding: (optional)
               The Unicode encoding to use for data exchanged on the
               connection. This defaults to `None`, allowing the
               application to send and receive raw bytes.
           :param window: (optional)
               The receive window size for this session
           :param max_pktsize: (optional)
               The maximum packet size for this session
           :type encoding: `str`
           :type window: `int`
           :type max_pktsize: `int`

           :returns: :class:`SSHUNIXChannel`

        """

        return SSHUNIXChannel(self, self._loop, encoding, window, max_pktsize)

    def create_x11_channel(self, encoding=None, window=_DEFAULT_WINDOW,
                           max_pktsize=_DEFAULT_MAX_PKTSIZE):
        """Create an SSH X11 channel to use in X11 forwarding"""

        return SSHX11Channel(self, self._loop, encoding, window, max_pktsize)

    def create_agent_channel(self, encoding=None, window=_DEFAULT_WINDOW,
                             max_pktsize=_DEFAULT_MAX_PKTSIZE):
        """Create an SSH agent channel to use in agent forwarding"""

        return SSHAgentChannel(self, self._loop, encoding, window, max_pktsize)

    @asyncio.coroutine
    def create_connection(self, session_factory, remote_host, remote_port,
                          orig_host='', orig_port=0, *, encoding=None,
                          window=_DEFAULT_WINDOW,
                          max_pktsize=_DEFAULT_MAX_PKTSIZE):
        """Create an SSH direct or forwarded TCP connection"""

        raise NotImplementedError

    @asyncio.coroutine
    def create_unix_connection(self, session_factory, remote_path, *,
                               encoding=None, window=_DEFAULT_WINDOW,
                               max_pktsize=_DEFAULT_MAX_PKTSIZE):
        """Create an SSH direct or forwarded UNIX domain socket connection"""

        raise NotImplementedError

    @asyncio.coroutine
    def forward_connection(self, dest_host, dest_port):
        """Forward a tunneled TCP connection

           This method is a coroutine which can be returned by a
           `session_factory` to forward connections tunneled over
           SSH to the specified destination host and port.

           :param dest_host:
               The hostname or address to forward the connections to
           :param dest_port:
               The port number to forward the connections to
           :type dest_host: `str`
           :type dest_port: `int`

           :returns: :class:`SSHTCPSession`

        """

        try:
            if dest_host == '':
                dest_host = None

            _, peer = yield from self._loop.create_connection(SSHForwarder,
                                                              dest_host,
                                                              dest_port)

            self.logger.info('  Forwarding TCP connection to %s',
                             (dest_host, dest_port))
        except OSError as exc:
            raise ChannelOpenError(OPEN_CONNECT_FAILED, str(exc)) from None

        return SSHForwarder(peer)

    @asyncio.coroutine
    def forward_unix_connection(self, dest_path):
        """Forward a tunneled UNIX domain socket connection

           This method is a coroutine which can be returned by a
           `session_factory` to forward connections tunneled over
           SSH to the specified destination path.

           :param dest_path:
               The path to forward the connection to
           :type dest_path: `str`

           :returns: :class:`SSHUNIXSession`

        """

        try:
            _, peer = \
                yield from self._loop.create_unix_connection(SSHForwarder,
                                                             dest_path)

            self.logger.info('  Forwarding UNIX connection to %s', dest_path)
        except OSError as exc:
            raise ChannelOpenError(OPEN_CONNECT_FAILED, str(exc)) from None

        return SSHForwarder(peer)

    @asyncio.coroutine
    def forward_local_port(self, listen_host, listen_port,
                           dest_host, dest_port):
        """Set up local port forwarding

           This method is a coroutine which attempts to set up port
           forwarding from a local listening port to a remote host and port
           via the SSH connection. If the request is successful, the
           return value is an :class:`SSHListener` object which can be used
           later to shut down the port forwarding.

           :param listen_host:
               The hostname or address on the local host to listen on
           :param listen_port:
               The port number on the local host to listen on
           :param dest_host:
               The hostname or address to forward the connections to
           :param dest_port:
               The port number to forward the connections to
           :type listen_host: `str`
           :type listen_port: `int`
           :type dest_host: `str`
           :type dest_port: `int`

           :returns: :class:`SSHListener`

           :raises: :exc:`OSError` if the listener can't be opened

        """

        @asyncio.coroutine
        def tunnel_connection(session_factory, orig_host, orig_port):
            """Forward a local connection over SSH"""

            return (yield from self.create_connection(session_factory,
                                                      dest_host, dest_port,
                                                      orig_host, orig_port))

        if (listen_host, listen_port) == (dest_host, dest_port):
            self.logger.info('Creating local TCP forwarder on %s',
                             (listen_host, listen_port))
        else:
            self.logger.info('Creating local TCP forwarder from %s to %s',
                             (listen_host, listen_port), (dest_host, dest_port))

        try:
            listener = yield from create_tcp_forward_listener(self, self._loop,
                                                              tunnel_connection,
                                                              listen_host,
                                                              listen_port)

            if dest_port == 0:
                dest_port = listener.get_port()

            return listener
        except OSError as exc:
            self.logger.debug1('Failed to create local TCP listener: %s', exc)
            raise

    @asyncio.coroutine
    def forward_local_path(self, listen_path, dest_path):
        """Set up local UNIX domain socket forwarding

           This method is a coroutine which attempts to set up UNIX domain
           socket forwarding from a local listening path to a remote path
           via the SSH connection. If the request is successful, the
           return value is an :class:`SSHListener` object which can be used
           later to shut down the UNIX domain socket forwarding.

           :param listen_path:
               The path on the local host to listen on
           :param dest_path:
               The path on the remote host to forward the connections to
           :type listen_path: `str`
           :type dest_path: `str`

           :returns: :class:`SSHListener`

           :raises: :exc:`OSError` if the listener can't be opened

        """

        @asyncio.coroutine
        def tunnel_connection(session_factory):
            """Forward a local connection over SSH"""

            return (yield from self.create_unix_connection(session_factory,
                                                           dest_path))

        self.logger.info('Creating local UNIX forwarder from %s to %s',
                         listen_path, dest_path)

        try:
            return (yield from create_unix_forward_listener(self, self._loop,
                                                            tunnel_connection,
                                                            listen_path))
        except OSError as exc:
            self.logger.debug1('Failed to create local UNIX listener: %s', exc)
            raise


class SSHClientConnection(SSHConnection):
    """SSH client connection

       This class represents an SSH client connection.

       Once authentication is successful on a connection, new client
       sessions can be opened by calling :meth:`create_session`.

       Direct TCP connections can be opened by calling
       :meth:`create_connection`.

       Remote listeners for forwarded TCP connections can be opened by
       calling :meth:`create_server`.

       Direct UNIX domain socket connections can be opened by calling
       :meth:`create_unix_connection`.

       Remote listeners for forwarded UNIX domain socket connections
       can be opened by calling :meth:`create_unix_server`.

       TCP port forwarding can be set up by calling :meth:`forward_local_port`
       or :meth:`forward_remote_port`.

       UNIX domain socket forwarding can be set up by calling
       :meth:`forward_local_path` or :meth:`forward_remote_path`.

    """

    def __init__(self, client_factory, loop, client_version,
                 x509_trusted_certs, x509_trusted_cert_paths, x509_purposes,
                 kex_algs, encryption_algs, mac_algs, compression_algs,
                 signature_algs, rekey_bytes, rekey_seconds, host, port,
                 known_hosts, username, password, client_host_keys,
                 client_host, client_username, client_keys, gss_host,
                 gss_delegate_creds, agent, agent_path, auth_waiter):
        super().__init__(client_factory, loop, client_version,
                         x509_trusted_certs, x509_trusted_cert_paths,
                         x509_purposes, kex_algs, encryption_algs, mac_algs,
                         compression_algs, signature_algs, rekey_bytes,
                         rekey_seconds, server=False)

        self._host = host
        self._port = port
        self._known_hosts = known_hosts
        self._username = username
        self._password = password
        self._client_host_keys = client_host_keys
        self._client_host = client_host
        self._client_username = client_username
        self._client_keys = client_keys
        self._agent = agent
        self._agent_path = agent_path
        self._auth_waiter = auth_waiter

        if gss_host:
            try:
                self._gss = GSSClient(gss_host, gss_delegate_creds)
                self._gss_mic_auth = True
            except GSSError:
                pass

        self._kbdint_password_auth = False

        self._remote_listeners = {}
        self._dynamic_remote_listeners = {}

    def _connection_made(self):
        """Handle the opening of a new connection"""

        if self._known_hosts is None:
            self._trusted_host_keys = None
            self._trusted_ca_keys = None
        else:
            if not self._known_hosts:
                self._known_hosts = os.path.join(os.path.expanduser('~'),
                                                 '.ssh', 'known_hosts')

            port = self._port if self._port != _DEFAULT_PORT else None

            self._match_known_hosts(self._known_hosts, self._host,
                                    self._peer_addr, port)

            self._server_host_key_algs = self._trusted_host_key_algs

            if self._trusted_ca_keys:
                self._server_host_key_algs = \
                    get_certificate_algs() + self._server_host_key_algs

            if self._x509_trusted_certs is not None:
                if self._x509_trusted_certs or self._x509_trusted_cert_paths:
                    self._server_host_key_algs = \
                        get_x509_certificate_algs() + \
                        self._server_host_key_algs

        if not self._server_host_key_algs:
            if self._known_hosts is None:
                self._server_host_key_algs = (get_certificate_algs() +
                                              get_public_key_algs())

                if self._x509_trusted_certs is not None:
                    self._server_host_key_algs = \
                        get_x509_certificate_algs() + self._server_host_key_algs
            elif self._gss:
                self._server_host_key_algs = [b'null']
            else:
                raise DisconnectError(DISC_HOST_KEY_NOT_VERIFYABLE,
                                      'No trusted server host keys available')

        self.logger.info('Connection to %s succeeded', (self._host, self._port))

        self.logger.info('  Local address: %s',
                         (self._local_addr, self._local_port))


    def _cleanup(self, exc):
        """Clean up this client connection"""

        if self._agent:
            self._agent.close()
            self._agent = None

        if self._remote_listeners:
            for listener in self._remote_listeners.values():
                listener.close()

            self._remote_listeners = {}
            self._dynamic_remote_listeners = {}

        if self._auth_waiter:
            if not self._auth_waiter.cancelled(): # pragma: no branch
                self._auth_waiter.set_exception(exc)

            self._auth_waiter = None

        reason = 'lost: ' + str(exc) if exc else 'closed'
        self.logger.info('Connection %s', reason)

        super()._cleanup(exc)


    def _choose_signature_alg(self, keypair):
        """Choose signature algorithm to use for key-based authentication"""

        if self._server_sig_algs:
            for alg in keypair.sig_algorithms:
                if alg in self._sig_algs and alg in self._server_sig_algs:
                    keypair.set_sig_algorithm(alg)
                    return True

        return keypair.sig_algorithms[-1] in self._sig_algs

    def validate_server_host_key(self, key_data):
        """Validate and return the server's host key"""

        try:
            return self._validate_host_key(self._host, key_data)
        except ValueError as exc:
            raise DisconnectError(DISC_HOST_KEY_NOT_VERIFYABLE, str(exc))

    def try_next_auth(self):
        """Attempt client authentication using the next compatible method"""

        if self._auth:
            self._auth.cancel()
            self._auth = None

        while self._auth_methods:
            method = self._auth_methods.pop(0)

            self._auth = lookup_client_auth(self, method)

            if self._auth:
                return

        self.logger.info('Auth failed for user %s', self._username)

        self._force_close(DisconnectError(DISC_NO_MORE_AUTH_METHODS_AVAILABLE,
                                          'Permission denied'))

    def gss_kex_auth_requested(self):
        """Return whether to allow GSS key exchange authentication or not"""

        if self._gss_kex_auth:
            self._gss_kex_auth = False
            return True
        else:
            return False

    def gss_mic_auth_requested(self):
        """Return whether to allow GSS MIC authentication or not"""

        if self._gss_mic_auth:
            self._gss_mic_auth = False
            return True
        else:
            return False

    @asyncio.coroutine
    def host_based_auth_requested(self):
        """Return a host key pair, host, and user to authenticate with"""

        while True:
            try:
                keypair = self._client_host_keys.pop(0)
            except IndexError:
                keypair = None
                break

            if self._choose_signature_alg(keypair):
                break

        if self._client_host is None:
            self._client_host, _ = yield from self._loop.getnameinfo(
                self.get_extra_info('sockname'), socket.NI_NUMERICSERV)

        return keypair, self._client_host, self._client_username

    @asyncio.coroutine
    def public_key_auth_requested(self):
        """Return a client key pair to authenticate with"""

        while True:
            if not self._client_keys:
                result = self._owner.public_key_auth_requested()

                if asyncio.iscoroutine(result):
                    result = yield from result

                if not result:
                    return None

                self._client_keys = load_keypairs(result)

            keypair = self._client_keys.pop(0)

            if self._choose_signature_alg(keypair):
                return keypair

    @asyncio.coroutine
    def password_auth_requested(self):
        """Return a password to authenticate with"""

        if self._password is not None:
            result = self._password
            self._password = None
        else:
            result = self._owner.password_auth_requested()

            if asyncio.iscoroutine(result):
                result = yield from result

        return result

    @asyncio.coroutine
    def password_change_requested(self, prompt, lang):
        """Return a password to authenticate with and what to change it to"""

        result = self._owner.password_change_requested(prompt, lang)

        if asyncio.iscoroutine(result):
            result = yield from result

        return result

    def password_changed(self):
        """Report a successful password change"""

        self._owner.password_changed()

    def password_change_failed(self):
        """Report a failed password change"""

        self._owner.password_change_failed()

    @asyncio.coroutine
    def kbdint_auth_requested(self):
        """Return the list of supported keyboard-interactive auth methods

           If keyboard-interactive auth is not supported in the client but
           a password was provided when the connection was opened, this
           will allow sending the password via keyboard-interactive auth.

        """

        result = self._owner.kbdint_auth_requested()

        if asyncio.iscoroutine(result):
            result = yield from result

        if result is NotImplemented:
            if self._password is not None and not self._kbdint_password_auth:
                self._kbdint_password_auth = True
                result = ''
            else:
                result = None

        return result

    @asyncio.coroutine
    def kbdint_challenge_received(self, name, instructions, lang, prompts):
        """Return responses to a keyboard-interactive auth challenge"""

        if self._kbdint_password_auth:
            if not prompts:
                # Silently drop any empty challenges used to print messages
                result = []
            elif len(prompts) == 1 and 'password' in prompts[0][0].lower():
                password = yield from self.password_auth_requested()

                result = [password] if password is not None else None
            else:
                result = None
        else:
            result = self._owner.kbdint_challenge_received(name, instructions,
                                                           lang, prompts)

            if asyncio.iscoroutine(result):
                result = yield from result

        return result

    def _process_session_open(self, packet):
        """Process an inbound session open request

           These requests are disallowed on an SSH client.

        """

        # pylint: disable=no-self-use,unused-argument

        raise ChannelOpenError(OPEN_ADMINISTRATIVELY_PROHIBITED,
                               'Session open forbidden on client')

    def _process_direct_tcpip_open(self, packet):
        """Process an inbound direct TCP/IP channel open request

           These requests are disallowed on an SSH client.

        """

        # pylint: disable=no-self-use,unused-argument

        raise ChannelOpenError(OPEN_ADMINISTRATIVELY_PROHIBITED,
                               'Direct TCP/IP open forbidden on client')

    def _process_forwarded_tcpip_open(self, packet):
        """Process an inbound forwarded TCP/IP channel open request"""

        dest_host = packet.get_string()
        dest_port = packet.get_uint32()
        orig_host = packet.get_string()
        orig_port = packet.get_uint32()
        packet.check_end()

        try:
            dest_host = dest_host.decode('utf-8')
            orig_host = orig_host.decode('utf-8')
        except UnicodeDecodeError:
            raise DisconnectError(DISC_PROTOCOL_ERROR, 'Invalid forwarded '
                                  'TCP/IP channel open request') from None

        # Some buggy servers send back a port of `0` instead of the actual
        # listening port when reporting connections which arrive on a listener
        # set up on a dynamic port. This lookup attempts to work around that.
        listener = (self._remote_listeners.get((dest_host, dest_port)) or
                    self._dynamic_remote_listeners.get(dest_host))

        if listener:
            chan, session = listener.process_connection(orig_host, orig_port)

            self.logger.info('Accepted forwarded TCP connection on %s',
                             (dest_host, dest_port))
            self.logger.info('  Client address: %s', (orig_host, orig_port))

            return chan, session
        else:
            raise ChannelOpenError(OPEN_CONNECT_FAILED, 'No such listener')

    @asyncio.coroutine
    def close_client_tcp_listener(self, listen_host, listen_port):
        """Close a remote TCP/IP listener"""

        yield from self._make_global_request(
            b'cancel-tcpip-forward', String(listen_host), UInt32(listen_port))

        self.logger.info('Closed remote TCP listener on %s',
                         (listen_host, listen_port))

        listener = self._remote_listeners.get((listen_host, listen_port))

        if listener:
            if self._dynamic_remote_listeners.get(listen_host) == listener:
                del self._dynamic_remote_listeners[listen_host]

            del self._remote_listeners[listen_host, listen_port]

    def _process_direct_streamlocal_at_openssh_dot_com_open(self, packet):
        """Process an inbound direct UNIX domain channel open request

           These requests are disallowed on an SSH client.

        """

        # pylint: disable=no-self-use,unused-argument

        raise ChannelOpenError(OPEN_ADMINISTRATIVELY_PROHIBITED,
                               'Direct UNIX domain socket open '
                               'forbidden on client')

    def _process_forwarded_streamlocal_at_openssh_dot_com_open(self, packet):
        """Process an inbound forwarded UNIX domain channel open request"""

        dest_path = packet.get_string()
        _ = packet.get_string()                         # reserved
        packet.check_end()

        try:
            dest_path = dest_path.decode('utf-8')
        except UnicodeDecodeError:
            raise DisconnectError(DISC_PROTOCOL_ERROR, 'Invalid forwarded '
                                  'UNIX domain channel open request') from None

        listener = self._remote_listeners.get(dest_path)

        if listener:
            chan, session = listener.process_connection()

            self.logger.info('Accepted remote UNIX connection on %s', dest_path)

            return chan, session
        else:
            raise ChannelOpenError(OPEN_CONNECT_FAILED, 'No such listener')

    @asyncio.coroutine
    def close_client_unix_listener(self, listen_path):
        """Close a remote UNIX domain socket listener"""

        yield from self._make_global_request(
            b'cancel-streamlocal-forward@openssh.com', String(listen_path))

        self.logger.info('Closed UNIX listener on %s', listen_path)

        if listen_path in self._remote_listeners:
            del self._remote_listeners[listen_path]

    def _process_x11_open(self, packet):
        """Process an inbound X11 channel open request"""

        orig_host = packet.get_string()
        orig_port = packet.get_uint32()

        packet.check_end()

        if self._x11_listener:
            self.logger.info('Accepted X11 connection')
            self.logger.info('  Client address: %s', (orig_host, orig_port))

            chan = self.create_x11_channel()

            chan.set_inbound_peer_names(orig_host, orig_port)

            return chan, self._x11_listener.forward_connection()
        else:
            raise ChannelOpenError(OPEN_CONNECT_FAILED,
                                   'X11 forwarding disabled')

    def _process_auth_agent_at_openssh_dot_com_open(self, packet):
        """Process an inbound auth agent channel open request"""

        packet.check_end()

        if self._agent_path:
            self.logger.info('Accepted SSH agent connection')

            return (self.create_unix_channel(),
                    self.forward_unix_connection(self._agent_path))
        else:
            raise ChannelOpenError(OPEN_CONNECT_FAILED,
                                   'Auth agent forwarding disabled')

    @asyncio.coroutine
    def attach_x11_listener(self, chan, display, auth_path, single_connection):
        """Attach a channel to a local X11 display"""

        if not display:
            display = os.environ.get('DISPLAY')

        if not display:
            raise ValueError('X11 display not set')

        if not self._x11_listener:
            self._x11_listener = yield from create_x11_client_listener(
                self._loop, display, auth_path)

        return self._x11_listener.attach(display, chan, single_connection)

    def detach_x11_listener(self, chan):
        """Detach a session from a local X11 listener"""

        if self._x11_listener:
            if self._x11_listener.detach(chan):
                self._x11_listener = None

    @asyncio.coroutine
    def create_session(self, session_factory, command=None, *, subsystem=None,
                       env={}, term_type=None, term_size=None, term_modes={},
                       x11_forwarding=False, x11_display=None,
                       x11_auth_path=None, x11_single_connection=False,
                       encoding='utf-8', window=_DEFAULT_WINDOW,
                       max_pktsize=_DEFAULT_MAX_PKTSIZE):
        """Create an SSH client session

           This method is a coroutine which can be called to create an SSH
           client session used to execute a command, start a subsystem
           such as sftp, or if no command or subsystem is specified run an
           interactive shell. Optional arguments allow terminal and
           environment information to be provided.

           By default, this class expects string data in its send and
           receive functions, which it encodes on the SSH connection in
           UTF-8 (ISO 10646) format. An optional encoding argument can
           be passed in to select a different encoding, or `None` can
           be passed in if the application wishes to send and receive
           raw bytes.

           Other optional arguments include the SSH receive window size and
           max packet size which default to 2 MB and 32 KB, respectively.

           :param session_factory:
               A `callable` which returns an :class:`SSHClientSession` object
               that will be created to handle activity on this session
           :param command: (optional)
               The remote command to execute. By default, an interactive
               shell is started if no command or subsystem is provided.
           :param subsystem: (optional)
               The name of a remote subsystem to start up
           :param env: (optional)
               The set of environment variables to set for this session.
               Keys and values passed in here will be converted to
               Unicode strings encoded as UTF-8 (ISO 10646) for
               transmission.

               .. note:: Many SSH servers restrict which environment
                         variables a client is allowed to set. The
                         server's configuration may need to be edited
                         before environment variables can be
                         successfully set in the remote environment.
           :param term_type: (optional)
               The terminal type to set for this session. If this is not set,
               a pseudo-terminal will not be requested for this session.
           :param term_size: (optional)
               The terminal width and height in characters and optionally
               the width and height in pixels
           :param term_modes: (optional)
               POSIX terminal modes to set for this session, where keys
               are taken from :ref:`POSIX terminal modes <PTYModes>` with
               values defined in section 8 of :rfc:`RFC 4254 <4254#section-8>`.
           :param x11_forwarding: (optional)
               Whether or not to request X11 forwarding for this session,
               defaulting to `False`
           :param x11_display: (optional)
               The display that X11 connections should be forwarded to,
               defaulting to the value in the environment variable `DISPLAY`
           :param x11_auth_path: (optional)
               The path to the Xauthority file to read X11 authentication
               data from, defaulting to the value in the environment variable
               `XAUTHORITY` or the file :file:`.Xauthority` in the user's
               home directory if that's not set
           :param x11_single_connection: (optional)
               Whether or not to limit X11 forwarding to a single connection,
               defaulting to `False`
           :param encoding: (optional)
               The Unicode encoding to use for data exchanged on the connection
           :param window: (optional)
               The receive window size for this session
           :param max_pktsize: (optional)
               The maximum packet size for this session
           :type session_factory: `callable`
           :type command: `str`
           :type subsystem: `str`
           :type env: `dict`
           :type term_type: `str`
           :type term_size: `tuple` of 2 or 4 `int` values
           :type term_modes: `dict`
           :type x11_forwarding: `bool`
           :type x11_display: `str`
           :type x11_auth_path: `str`
           :type x11_single_connection: `bool`
           :type encoding: `str`
           :type window: `int`
           :type max_pktsize: `int`

           :returns: an :class:`SSHClientChannel` and :class:`SSHClientSession`

           :raises: :exc:`ChannelOpenError` if the session can't be opened

        """

        chan = SSHClientChannel(self, self._loop, encoding,
                                window, max_pktsize)

        return (yield from chan.create(session_factory, command, subsystem,
                                       env, term_type, term_size, term_modes,
                                       x11_forwarding, x11_display,
                                       x11_auth_path, x11_single_connection,
                                       bool(self._agent_path)))

    @asyncio.coroutine
    def open_session(self, *args, **kwargs):
        """Open an SSH client session

           This method is a coroutine wrapper around :meth:`create_session`
           designed to provide a "high-level" stream interface for creating
           an SSH client session. Instead of taking a `session_factory`
           argument for constructing an object which will handle activity
           on the session via callbacks, it returns an :class:`SSHWriter`
           and two :class:`SSHReader` objects representing stdin, stdout,
           and stderr which can be used to perform I/O on the session. With
           the exception of `session_factory`, all of the arguments to
           :meth:`create_session` are supported and have the same meaning.

        """

        chan, session = yield from self.create_session(SSHClientStreamSession,
                                                       *args, **kwargs)

        return (SSHWriter(session, chan), SSHReader(session, chan),
                SSHReader(session, chan, EXTENDED_DATA_STDERR))

    # pylint: disable=redefined-builtin
    @async_context_manager
    def create_process(self, *args, bufsize=io.DEFAULT_BUFFER_SIZE, input=None,
                       stdin=PIPE, stdout=PIPE, stderr=PIPE, **kwargs):
        """Create a process on the remote system

           This method is a coroutine wrapper around :meth:`create_session`
           which can be used to execute a command, start a subsystem,
           or start an interactive shell, optionally redirecting stdin,
           stdout, and stderr to and from files or pipes attached to
           other local and remote processes.

           By default, the stdin, stdout, and stderr arguments default
           to the special value `PIPE` which means that they can be
           read and written interactively via stream objects which are
           members of the :class:`SSHClientProcess` object this method
           returns. If other file-like objects are provided as arguments,
           input or output will automatically be redirected to them. The
           special value `DEVNULL` can be used to provide no input or
           discard all output, and the special value `STDOUT` can be
           provided as `stderr` to send its output to the same stream
           as `stdout`.

           In addition to the arguments below, all arguments to
           :meth:`create_session` except for `session_factory` are
           supported and have the same meaning.

           :param bufsize: (optional)
               Buffer size to use when feeding data from a file to stdin
           :param input: (optional)
               Input data to feed to standard input of the remote process.
               If specified, this argument takes precedence over stdin.
               Data should be a `str` if encoding is set, or `bytes` if not.
           :param stdin: (optional)
               A filename, file-like object, file descriptor, socket, or
               :class:`SSHReader` to feed to standard input of the remote
               process, or `DEVNULL` to provide no input.
           :param stdout: (optional)
               A filename, file-like object, file descriptor, socket, or
               :class:`SSHWriter` to feed standard output of the remote
               process to, or `DEVNULL` to discard this output.
           :param stderr: (optional)
               A filename, file-like object, file descriptor, socket, or
               :class:`SSHWriter` to feed standard error of the remote
               process to, `DEVNULL` to discard this output, or `STDOUT`
               to feed standard error to the same place as stdout.
           :type bufsize: `int`
           :type input: `str` or `bytes`

           :returns: :class:`SSHClientProcess`

           :raises: :exc:`ChannelOpenError` if the channel can't be opened

        """

        chan, process = yield from self.create_session(SSHClientProcess,
                                                       *args, **kwargs)

        if input:
            chan.write(input)
            chan.write_eof()
            stdin = None

        yield from process.redirect(stdin, stdout, stderr, bufsize)

        return process
    # pylint: enable=redefined-builtin

    @asyncio.coroutine
    def run(self, *args, check=False, **kwargs):
        """Run a command on the remote system and collect its output

           This method is a coroutine wrapper around :meth:`create_process`
           which can be used to run a process to completion when no
           interactivity is needed. All of the arguments to
           :meth:`create_process` can be passed in to provide input or
           redirect stdin, stdout, and stderr, but this method waits until
           the process exits and returns an :class:`SSHCompletedProcess`
           object with the exit status or signal information and the
           output to stdout and stderr (if not redirected).

           If the check argument is set to `True`, a non-zero exit status
           from the remote process will trigger the :exc:`ProcessError`
           exception to be raised.

           In addition to the argument below, all arguments to
           :meth:`create_process` are supported and have the same meaning.

           :param check: (optional)
               Whether or not to raise :exc:`ProcessError` when a non-zero
               exit status is returned
           :type check: `bool`

           :returns: :class:`SSHCompletedProcess`

           :raises: | :exc:`ChannelOpenError` if the session can't be opened
                    | :exc:`ProcessError` if checking non-zero exit status

        """

        process = yield from self.create_process(*args, **kwargs)

        return (yield from process.wait(check))

    @asyncio.coroutine
    def create_connection(self, session_factory, remote_host, remote_port,
                          orig_host='', orig_port=0, *, encoding=None,
                          window=_DEFAULT_WINDOW,
                          max_pktsize=_DEFAULT_MAX_PKTSIZE):
        """Create an SSH TCP direct connection

           This method is a coroutine which can be called to request that
           the server open a new outbound TCP connection to the specified
           destination host and port. If the connection is successfully
           opened, a new SSH channel will be opened with data being handled
           by a :class:`SSHTCPSession` object created by `session_factory`.

           Optional arguments include the host and port of the original
           client opening the connection when performing TCP port forwarding.

           By default, this class expects data to be sent and received as
           raw bytes. However, an optional encoding argument can be
           passed in to select the encoding to use, allowing the
           application send and receive string data.

           Other optional arguments include the SSH receive window size and
           max packet size which default to 2 MB and 32 KB, respectively.

           :param session_factory:
               A `callable` which returns an :class:`SSHClientSession` object
               that will be created to handle activity on this session
           :param remote_host:
               The remote hostname or address to connect to
           :param remote_port:
               The remote port number to connect to
           :param orig_host: (optional)
               The hostname or address of the client requesting the connection
           :param orig_port: (optional)
               The port number of the client requesting the connection
           :param encoding: (optional)
               The Unicode encoding to use for data exchanged on the connection
           :param window: (optional)
               The receive window size for this session
           :param max_pktsize: (optional)
               The maximum packet size for this session
           :type session_factory: `callable`
           :type remote_host: `str`
           :type remote_port: `int`
           :type orig_host: `str`
           :type orig_port: `int`
           :type encoding: `str`
           :type window: `int`
           :type max_pktsize: `int`

           :returns: an :class:`SSHTCPChannel` and :class:`SSHTCPSession`

           :raises: :exc:`ChannelOpenError` if the connection can't be opened

        """

        self.logger.info('Opening direct TCP connection to %s',
                         (remote_host, remote_port))
        self.logger.info('  Client address: %s', (orig_host, orig_port))

        chan = self.create_tcp_channel(encoding, window, max_pktsize)

        session = yield from chan.connect(session_factory, remote_host,
                                          remote_port, orig_host, orig_port)

        return chan, session

    @asyncio.coroutine
    def open_connection(self, *args, **kwargs):
        """Open an SSH TCP direct connection

           This method is a coroutine wrapper around :meth:`create_connection`
           designed to provide a "high-level" stream interface for creating
           an SSH TCP direct connection. Instead of taking a
           `session_factory` argument for constructing an object which will
           handle activity on the session via callbacks, it returns
           :class:`SSHReader` and :class:`SSHWriter` objects which can be
           used to perform I/O on the connection.

           With the exception of `session_factory`, all of the arguments
           to :meth:`create_connection` are supported and have the same
           meaning here.

           :returns: an :class:`SSHReader` and :class:`SSHWriter`

           :raises: :exc:`ChannelOpenError` if the connection can't be opened

        """

        chan, session = yield from self.create_connection(SSHTCPStreamSession,
                                                          *args, **kwargs)

        return SSHReader(session, chan), SSHWriter(session, chan)

    @asyncio.coroutine
    def create_server(self, session_factory, listen_host, listen_port, *,
                      encoding=None, window=_DEFAULT_WINDOW,
                      max_pktsize=_DEFAULT_MAX_PKTSIZE):
        """Create a remote SSH TCP listener

           This method is a coroutine which can be called to request that
           the server listen on the specified remote address and port for
           incoming TCP connections. If the request is successful, the
           return value is an :class:`SSHListener` object which can be
           used later to shut down the listener. If the request fails,
           `None` is returned.

           :param session_factory:
               A `callable` or coroutine which takes arguments of the
               original host and port of the client and decides whether
               to accept the connection or not, either returning an
               :class:`SSHTCPSession` object used to handle activity on
               that connection or raising :exc:`ChannelOpenError` to
               indicate that the connection should not be accepted
           :param listen_host:
               The hostname or address on the remote host to listen on
           :param listen_port:
               The port number on the remote host to listen on
           :param encoding: (optional)
               The Unicode encoding to use for data exchanged on the connection
           :param window: (optional)
               The receive window size for this session
           :param max_pktsize: (optional)
               The maximum packet size for this session
           :type session_factory: `callable` or coroutine
           :type listen_host: `str`
           :type listen_port: `int`
           :type encoding: `str`
           :type window: `int`
           :type max_pktsize: `int`

           :returns: :class:`SSHListener` or `None` if the listener can't
                     be opened

        """

        listen_host = listen_host.lower()

        self.logger.info('Creating remote TCP listener on %s',
                         (listen_host, listen_port))

        pkttype, packet = yield from self._make_global_request(
            b'tcpip-forward', String(listen_host), UInt32(listen_port))

        if pkttype == MSG_REQUEST_SUCCESS:
            if listen_port == 0:
                listen_port = packet.get_uint32()
                dynamic = True
            else:
                # OpenSSH 6.8 introduced a bug which causes the reply
                # to contain an extra uint32 value of 0 when non-dynamic
                # ports are requested, causing the check_end() call below
                # to fail. This check works around this problem.
                if len(packet.get_remaining_payload()) == 4: # pragma: no cover
                    packet.get_uint32()

                dynamic = False

            packet.check_end()

            listener = SSHTCPClientListener(self, self._loop, session_factory,
                                            listen_host, listen_port,
                                            encoding, window, max_pktsize)

            if dynamic:
                self.logger.debug1('Assigning dynamic port %d', listen_port)

                self._dynamic_remote_listeners[listen_host] = listener

            self._remote_listeners[listen_host, listen_port] = listener
            return listener
        else:
            packet.check_end()
            self.logger.debug1('Failed to create remote TCP listener')
            return None

    @asyncio.coroutine
    def start_server(self, handler_factory, *args, **kwargs):
        """Start a remote SSH TCP listener

           This method is a coroutine wrapper around :meth:`create_server`
           designed to provide a "high-level" stream interface for creating
           remote SSH TCP listeners. Instead of taking a `session_factory`
           argument for constructing an object which will handle activity on
           the session via callbacks, it takes a `handler_factory` which
           returns a `callable` or coroutine that will be passed
           :class:`SSHReader` and :class:`SSHWriter` objects which can be
           used to perform I/O on each new connection which arrives. Like
           :meth:`create_server`, `handler_factory` can also raise
           :exc:`ChannelOpenError` if the connection should not be accepted.

           With the exception of `handler_factory` replacing
           `session_factory`, all of the arguments to :meth:`create_server`
           are supported and have the same meaning here.

           :param handler_factory:
               A `callable` or coroutine which takes arguments of the
               original host and port of the client and decides whether to
               accept the connection or not, either returning a callback
               or coroutine used to handle activity on that connection
               or raising :exc:`ChannelOpenError` to indicate that the
               connection should not be accepted
           :type handler_factory: `callable` or coroutine

           :returns: :class:`SSHListener` or `None` if the listener can't
                     be opened

        """

        def session_factory(orig_host, orig_port):
            """Return a TCP stream session handler"""

            return SSHTCPStreamSession(handler_factory(orig_host, orig_port))

        return (yield from self.create_server(session_factory,
                                              *args, **kwargs))

    @asyncio.coroutine
    def create_unix_connection(self, session_factory, remote_path, *,
                               encoding=None, window=_DEFAULT_WINDOW,
                               max_pktsize=_DEFAULT_MAX_PKTSIZE):
        """Create an SSH UNIX domain socket direct connection

           This method is a coroutine which can be called to request that
           the server open a new outbound UNIX domain socket connection to
           the specified destination path. If the connection is successfully
           opened, a new SSH channel will be opened with data being handled
           by a :class:`SSHUNIXSession` object created by `session_factory`.

           By default, this class expects data to be sent and received as
           raw bytes. However, an optional encoding argument can be
           passed in to select the encoding to use, allowing the
           application send and receive string data.

           Other optional arguments include the SSH receive window size and
           max packet size which default to 2 MB and 32 KB, respectively.

           :param session_factory:
               A `callable` which returns an :class:`SSHClientSession` object
               that will be created to handle activity on this session
           :param remote_path:
               The remote path to connect to
           :param encoding: (optional)
               The Unicode encoding to use for data exchanged on the connection
           :param window: (optional)
               The receive window size for this session
           :param max_pktsize: (optional)
               The maximum packet size for this session
           :type session_factory: `callable`
           :type remote_path: `str`
           :type encoding: `str`
           :type window: `int`
           :type max_pktsize: `int`

           :returns: an :class:`SSHUNIXChannel` and :class:`SSHUNIXSession`

           :raises: :exc:`ChannelOpenError` if the connection can't be opened

        """

        self.logger.info('Opening direct UNIX connection to %s', remote_path)

        chan = self.create_unix_channel(encoding, window, max_pktsize)

        session = yield from chan.connect(session_factory, remote_path)

        return chan, session

    @asyncio.coroutine
    def open_unix_connection(self, *args, **kwargs):
        """Open an SSH UNIX domain socket direct connection

           This method is a coroutine wrapper around
           :meth:`create_unix_connection` designed to provide a "high-level"
           stream interface for creating an SSH UNIX domain socket direct
           connection. Instead of taking a `session_factory` argument for
           constructing an object which will handle activity on the session
           via callbacks, it returns :class:`SSHReader` and :class:`SSHWriter`
           objects which can be used to perform I/O on the connection.

           With the exception of `session_factory`, all of the arguments
           to :meth:`create_unix_connection` are supported and have the same
           meaning here.

           :returns: an :class:`SSHReader` and :class:`SSHWriter`

           :raises: :exc:`ChannelOpenError` if the connection can't be opened

        """

        chan, session = \
            yield from self.create_unix_connection(SSHUNIXStreamSession,
                                                   *args, **kwargs)

        return SSHReader(session, chan), SSHWriter(session, chan)

    @asyncio.coroutine
    def create_unix_server(self, session_factory, listen_path, *,
                           encoding=None, window=_DEFAULT_WINDOW,
                           max_pktsize=_DEFAULT_MAX_PKTSIZE):
        """Create a remote SSH UNIX domain socket listener

           This method is a coroutine which can be called to request that
           the server listen on the specified remote path for incoming UNIX
           domain socket connections. If the request is successful, the
           return value is an :class:`SSHListener` object which can be
           used later to shut down the listener. If the request fails,
           `None` is returned.

           :param session_factory:
               A `callable` or coroutine which takes arguments of the
               original host and port of the client and decides whether
               to accept the connection or not, either returning an
               :class:`SSHUNIXSession` object used to handle activity
               on that connection or raising :exc:`ChannelOpenError`
               to indicate that the connection should not be accepted
           :param listen_path:
               The path on the remote host to listen on
           :param encoding: (optional)
               The Unicode encoding to use for data exchanged on the connection
           :param window: (optional)
               The receive window size for this session
           :param max_pktsize: (optional)
               The maximum packet size for this session
           :type session_factory: `callable` or coroutine
           :type listen_path: `str`
           :type encoding: `str`
           :type window: `int`
           :type max_pktsize: `int`

           :returns: :class:`SSHListener` or `None` if the listener can't
                     be opened

        """

        self.logger.info('Creating remote UNIX listener on %s', listen_path)

        pkttype, packet = yield from self._make_global_request(
            b'streamlocal-forward@openssh.com', String(listen_path))

        packet.check_end()

        if pkttype == MSG_REQUEST_SUCCESS:
            listener = SSHUNIXClientListener(self, self._loop, session_factory,
                                             listen_path, encoding,
                                             window, max_pktsize)

            self._remote_listeners[listen_path] = listener
            return listener
        else:
            self.logger.debug1('Failed to create remote UNIX listener')
            return None

    @asyncio.coroutine
    def start_unix_server(self, handler_factory, *args, **kwargs):
        """Start a remote SSH UNIX domain socket listener

           This method is a coroutine wrapper around :meth:`create_unix_server`
           designed to provide a "high-level" stream interface for creating
           remote SSH UNIX domain socket listeners. Instead of taking a
           `session_factory` argument for constructing an object which
           will handle activity on the session via callbacks, it takes a
           `handler_factory` which returns a `callable` or coroutine that
           will be passed :class:`SSHReader` and :class:`SSHWriter` objects
           which can be used to perform I/O on each new connection which
           arrives. Like :meth:`create_unix_server`, `handler_factory`
           can also raise :exc:`ChannelOpenError` if the connection should
           not be accepted.

           With the exception of `handler_factory` replacing
           `session_factory`, all of the arguments to
           :meth:`create_unix_server` are supported and have the same
           meaning here.

           :param handler_factory:
               A `callable` or coroutine which takes arguments of the
               original host and port of the client and decides whether to
               accept the connection or not, either returning a callback
               or coroutine used to handle activity on that connection
               or raising :exc:`ChannelOpenError` to indicate that the
               connection should not be accepted
           :type handler_factory: `callable` or coroutine

           :returns: :class:`SSHListener` or `None` if the listener can't
                     be opened

        """

        def session_factory():
            """Return a UNIX domain socket stream session handler"""

            return SSHUNIXStreamSession(handler_factory())

        return (yield from self.create_unix_server(session_factory,
                                                   *args, **kwargs))

    @asyncio.coroutine
    def create_ssh_connection(self, client_factory, host,
                              port=_DEFAULT_PORT, **kwargs):
        """Create a tunneled SSH client connection

           This method is a coroutine which can be called to open an
           SSH client connection to the requested host and port tunneled
           inside this already established connection. It takes all the
           same arguments as :func:`create_connection` but requests
           that the upstream SSH server open the connection rather than
           connecting directly.

        """

        return (yield from create_connection(client_factory, host, port,
                                             tunnel=self, **kwargs))

    @asyncio.coroutine
    def connect_ssh(self, host, port=_DEFAULT_PORT, **kwargs):
        """Make a tunneled SSH client connection

           This method is a coroutine which can be called to open an
           SSH client connection to the requested host and port tunneled
           inside this already established connection. It takes all the
           same arguments as :func:`connect` but requests that the upstream
           SSH server open the connection rather than connecting directly.

        """

        return (yield from connect(host, port, tunnel=self, **kwargs))

    @asyncio.coroutine
    def forward_remote_port(self, listen_host, listen_port,
                            dest_host, dest_port):
        """Set up remote port forwarding

           This method is a coroutine which attempts to set up port
           forwarding from a remote listening port to a local host and port
           via the SSH connection. If the request is successful, the
           return value is an :class:`SSHListener` object which can be
           used later to shut down the port forwarding. If the request
           fails, `None` is returned.

           :param listen_host:
               The hostname or address on the remote host to listen on
           :param listen_port:
               The port number on the remote host to listen on
           :param dest_host:
               The hostname or address to forward connections to
           :param dest_port:
               The port number to forward connections to
           :type listen_host: `str`
           :type listen_port: `int`
           :type dest_host: `str`
           :type dest_port: `int`

           :returns: :class:`SSHListener` or `None` if the listener can't
                     be opened

        """

        def session_factory(orig_host, orig_port):
            """Return an SSHTCPSession used to do remote port forwarding"""

            # pylint: disable=unused-argument
            return self.forward_connection(dest_host, dest_port)

        self.logger.info('Creating remote TCP forwarder from %s to %s',
                         (listen_host, listen_port), (dest_host, dest_port))

        return (yield from self.create_server(session_factory, listen_host,
                                              listen_port))

    @asyncio.coroutine
    def forward_remote_path(self, listen_path, dest_path):
        """Set up remote UNIX domain socket forwarding

           This method is a coroutine which attempts to set up UNIX domain
           socket forwarding from a remote listening path to a local path
           via the SSH connection. If the request is successful, the
           return value is an :class:`SSHListener` object which can be
           used later to shut down the port forwarding. If the request
           fails, `None` is returned.

           :param listen_path:
               The path on the remote host to listen on
           :param dest_path:
               The path on the local host to forward connections to
           :type listen_path: `str`
           :type dest_path: `str`

           :returns: :class:`SSHListener` or `None` if the listener can't
                     be opened

        """

        def session_factory():
            """Return an SSHUNIXSession used to do remote path forwarding"""

            return self.forward_unix_connection(dest_path)

        self.logger.info('Creating remote UNIX forwarder from %s to %s',
                         listen_path, dest_path)

        return (yield from self.create_unix_server(session_factory,
                                                   listen_path))

    @asyncio.coroutine
    def forward_socks(self, listen_host, listen_port):
        """Set up local port forwarding via SOCKS

           This method is a coroutine which attempts to set up dynamic
           port forwarding via SOCKS on the specified local host and
           port. Each SOCKS request contains the destination host and
           port to connect to and triggers a request to tunnel traffic
           to the requested host and port via the SSH connection.

           If the request is successful, the return value is an
           :class:`SSHListener` object which can be used later to shut
           down the port forwarding.

           :param listen_host:
               The hostname or address on the local host to listen on
           :param listen_port:
               The port number on the local host to listen on
           :type listen_host: `str`
           :type listen_port: `int`

           :returns: :class:`SSHListener`

           :raises: :exc:`OSError` if the listener can't be opened

        """

        @asyncio.coroutine
        def tunnel_socks(session_factory, dest_host, dest_port,
                         orig_host, orig_port):
            """Forward a local SOCKS connection over SSH"""

            return (yield from self.create_connection(session_factory,
                                                      dest_host, dest_port,
                                                      orig_host, orig_port))

        self.logger.info('Creating local SOCKS forwarder on %s',
                         (listen_host, listen_port))

        try:
            return (yield from create_socks_listener(self, self._loop,
                                                     tunnel_socks, listen_host,
                                                     listen_port))
        except OSError as exc:
            self.logger.debug1('Failed to create local SOCKS listener: %s', exc)
            raise

    @async_context_manager
    def start_sftp_client(self, path_encoding='utf-8', path_errors='strict'):
        """Start an SFTP client

           This method is a coroutine which attempts to start a secure
           file transfer session. If it succeeds, it returns an
           :class:`SFTPClient` object which can be used to copy and
           access files on the remote host.

           An optional Unicode encoding can be specified for sending and
           receiving pathnames, defaulting to UTF-8 with strict error
           checking. If an encoding of `None` is specified, pathnames
           will be left as bytes rather than being converted to & from
           strings.

           :param path_encoding:
               The Unicode encoding to apply when sending and receiving
               remote pathnames
           :param path_errors:
               The error handling strategy to apply on encode/decode errors
           :type path_encoding: `str`
           :type path_errors: `str`

           :returns: :class:`SFTPClient`

           :raises: :exc:`SFTPError` if the session can't be opened

        """

        writer, reader, _ = yield from self.open_session(subsystem='sftp',
                                                         encoding=None)

        return (yield from start_sftp_client(self, self._loop, reader, writer,
                                             path_encoding, path_errors))


class SSHServerConnection(SSHConnection):
    """SSH server connection

       This class represents an SSH server connection.

       During authentication, :meth:`send_auth_banner` can be called to
       send an authentication banner to the client.

       Once authenticated, :class:`SSHServer` objects wishing to create
       session objects with non-default channel properties can call
       :meth:`create_server_channel` from their :meth:`session_requested()
       <SSHServer.session_requested>` method and return a tuple of
       the :class:`SSHServerChannel` object returned from that and either
       an :class:`SSHServerSession` object or a coroutine which returns
       an :class:`SSHServerSession`.

       Similarly, :class:`SSHServer` objects wishing to create TCP
       connection objects with non-default channel properties can call
       :meth:`create_tcp_channel` from their :meth:`connection_requested()
       <SSHServer.connection_requested>` method and return a tuple of
       the :class:`SSHTCPChannel` object returned from that and either
       an :class:`SSHTCPSession` object or a coroutine which returns an
       :class:`SSHTCPSession`.

       :class:`SSHServer` objects wishing to create UNIX domain socket
       connection objects with non-default channel properties can call
       :meth:`create_unix_channel` from the :meth:`unix_connection_requested()
       <SSHServer.unix_connection_requested>` method and return a tuple of
       the :class:`SSHUNIXChannel` object returned from that and either
       an :class:`SSHUNIXSession` object or a coroutine which returns an
       :class:`SSHUNIXSession`.

    """

    def __init__(self, server_factory, loop, server_version,
                 x509_trusted_certs, x509_trusted_cert_paths, x509_purposes,
                 kex_algs, encryption_algs, mac_algs, compression_algs,
                 signature_algs, rekey_bytes, rekey_seconds,
                 server_host_keys, known_client_hosts, trust_client_host,
                 authorized_client_keys, gss_host, allow_pty, line_editor,
                 line_history, x11_forwarding, x11_auth_path, agent_forwarding,
                 process_factory, session_factory, session_encoding,
                 sftp_factory, allow_scp, window, max_pktsize, login_timeout):
        super().__init__(server_factory, loop, server_version,
                         x509_trusted_certs, x509_trusted_cert_paths,
                         x509_purposes, kex_algs, encryption_algs, mac_algs,
                         compression_algs, signature_algs, rekey_bytes,
                         rekey_seconds, server=True)

        self._server_host_keys = server_host_keys
        self._server_host_key_algs = list(server_host_keys.keys())
        self._known_client_hosts = known_client_hosts
        self._trust_client_host = trust_client_host
        self._client_keys = authorized_client_keys
        self._allow_pty = allow_pty
        self._line_editor = line_editor
        self._line_history = line_history
        self._x11_forwarding = x11_forwarding
        self._x11_auth_path = x11_auth_path
        self._agent_forwarding = agent_forwarding
        self._process_factory = process_factory
        self._session_factory = session_factory
        self._session_encoding = session_encoding
        self._sftp_factory = sftp_factory
        self._allow_scp = allow_scp
        self._window = window
        self._max_pktsize = max_pktsize

        if gss_host:
            try:
                self._gss = GSSServer(gss_host)
                self._gss_mic_auth = True
            except GSSError:
                pass

        if login_timeout:
            self._login_timer = loop.call_later(login_timeout,
                                                self._login_timer_callback)
        else:
            self._login_timer = None

        self._server_host_key = None
        self._key_options = {}
        self._cert_options = None
        self._kbdint_password_auth = False

        self._agent_listener = None

    def _cleanup(self, exc):
        """Clean up this server connection"""

        if self._agent_listener:
            self._agent_listener.close()
            self._agent_listener = None

        self._cancel_login_timer()
        super()._cleanup(exc)

    def _cancel_login_timer(self):
        """Cancel the login timer"""

        if self._login_timer:
            self._login_timer.cancel()
            self._login_timer = None

    def _login_timer_callback(self):
        """Close the connection if authentication hasn't completed yet"""

        self._login_timer = None

        self.connection_lost(DisconnectError(DISC_CONNECTION_LOST,
                                             'Login timeout expired'))

    def _connection_made(self):
        """Handle the opening of a new connection"""

        self.logger.info('Accepted SSH connection on %s',
                         (self._local_addr, self._local_port))
        self.logger.info('  Client address: %s',
                         (self._peer_addr, self._peer_port))

    def _choose_server_host_key(self, peer_host_key_algs):
        """Choose the server host key to use

           Given a list of host key algorithms supported by the client,
           select the first compatible server host key we have and return
           whether or not we were able to find a match.

        """

        for alg in peer_host_key_algs:
            keypair = self._server_host_keys.get(alg)
            if keypair:
                if alg != keypair.algorithm:
                    keypair.set_sig_algorithm(alg)

                self._server_host_key = keypair
                return True

        return False

    def get_server_host_key(self):
        """Return the chosen server host key

           This method returns a keypair object containing the
           chosen server host key and a corresponding public key
           or certificate.

        """

        return self._server_host_key

    def gss_kex_auth_supported(self):
        """Return whether GSS key exchange authentication is supported"""

        return self._gss_kex_auth and self._gss.complete

    def gss_mic_auth_supported(self):
        """Return whether GSS MIC authentication is supported"""

        return self._gss_mic_auth

    @asyncio.coroutine
    def validate_gss_principal(self, username, user_principal, host_principal):
        """Validate the GSS principal name for the specified user

           Return whether the user principal acquired during GSS
           authentication is valid for the specified user.

        """

        result = self._owner.validate_gss_principal(username, user_principal,
                                                    host_principal)

        if asyncio.iscoroutine(result):
            result = yield from result

        return result

    def host_based_auth_supported(self):
        """Return whether or not host based authentication is supported"""

        return bool(self._known_client_hosts)

    @asyncio.coroutine
    def validate_host_based_auth(self, username, key_data, client_host,
                                 client_username, msg, signature):
        """Validate host based authentication for the specified host and user"""

        # Remove a trailing '.' from the client host if present
        if client_host[-1:] == '.':
            client_host = client_host[:-1]

        if self._trust_client_host:
            resolved_host = client_host
        else:
            resolved_host, _ = yield from self._loop.getnameinfo(
                self.get_extra_info('peername'), socket.NI_NUMERICSERV)

            if resolved_host != client_host:
                self.logger.info('Client host mismatch: received %s, '
                                 'resolved %s', client_host, resolved_host)

        self._match_known_hosts(self._known_client_hosts, resolved_host,
                                self._peer_addr, None)

        try:
            key = self._validate_host_key(client_host, key_data)
        except ValueError as exc:
            self.logger.debug1('Invalid host key: %s', exc)
            return False

        if not key.verify(String(self._session_id) + msg, signature):
            self.logger.debug1('Invalid host-based auth signature')
            return False

        result = self._owner.validate_host_based_user(username, client_host,
                                                      client_username)

        if asyncio.iscoroutine(result):
            result = yield from result

        return result

    @asyncio.coroutine
    def _validate_openssh_certificate(self, username, cert):
        """Validate an OpenSSH client certificate for the specified user"""

        options = None

        if self._client_keys:
            options = self._client_keys.validate(cert.signing_key,
                                                 self._peer_addr,
                                                 cert.principals, ca=True)

        if options is None:
            result = self._owner.validate_ca_key(username, cert.signing_key)

            if asyncio.iscoroutine(result):
                result = yield from result

            if not result:
                return None

            options = {}

        self._key_options = options

        if self.get_key_option('principals'):
            username = None

        try:
            cert.validate(CERT_TYPE_USER, username)
        except ValueError:
            return None

        allowed_addresses = cert.options.get('source-address')
        if allowed_addresses:
            ip = ip_address(self._peer_addr)
            if not any(ip in network for network in allowed_addresses):
                return None

        self._cert_options = cert.options

        return cert.key

    @asyncio.coroutine
    def _validate_x509_certificate_chain(self, username, cert):
        """Validate an X.509 client certificate for the specified user"""

        if not self._client_keys:
            return None

        options, trusted_cert = \
            self._client_keys.validate_x509(cert, self._peer_addr)

        if options is None:
            return None

        self._key_options = options

        if self.get_key_option('principals'):
            username = None

        if trusted_cert:
            trusted_certs = self._x509_trusted_certs + [trusted_cert]
        else:
            trusted_certs = self._x509_trusted_certs

        try:
            cert.validate_chain(trusted_certs, self._x509_trusted_cert_paths,
                                None, self._x509_purposes,
                                user_principal=username)
        except ValueError:
            return None

        return cert.key

    @asyncio.coroutine
    def _validate_client_certificate(self, username, key_data):
        """Validate a client certificate for the specified user"""

        try:
            cert = decode_ssh_certificate(key_data)
        except KeyImportError:
            return None

        if cert.is_x509_chain:
            return self._validate_x509_certificate_chain(username, cert)
        else:
            return self._validate_openssh_certificate(username, cert)

    @asyncio.coroutine
    def _validate_client_public_key(self, username, key_data):
        """Validate a client public key for the specified user"""

        try:
            key = decode_ssh_public_key(key_data)
        except KeyImportError:
            return None

        options = None

        if self._client_keys:
            options = self._client_keys.validate(key, self._peer_addr)

        if options is None:
            result = self._owner.validate_public_key(username, key)

            if asyncio.iscoroutine(result):
                result = yield from result

            if not result:
                return None

            options = {}

        self._key_options = options

        return key

    def public_key_auth_supported(self):
        """Return whether or not public key authentication is supported"""

        return (bool(self._client_keys) or
                self._owner.public_key_auth_supported())

    @asyncio.coroutine
    def validate_public_key(self, username, key_data, msg, signature):
        """Validate the public key or certificate for the specified user

           This method validates that the public key or certificate provided
           is allowed for the specified user. If msg and signature are
           provided, the key is used to also validate the message signature.
           It returns `True` when the key is allowed and the signature (if
           present) is valid. Otherwise, it returns `False`.

        """

        key = ((yield from self._validate_client_certificate(username,
                                                             key_data)) or
               (yield from self._validate_client_public_key(username,
                                                            key_data)))

        if key is None:
            return False
        elif msg:
            return key.verify(String(self._session_id) + msg, signature)
        else:
            return True

    def password_auth_supported(self):
        """Return whether or not password authentication is supported"""

        return self._owner.password_auth_supported()

    @asyncio.coroutine
    def validate_password(self, username, password):
        """Return whether password is valid for this user"""

        result = self._owner.validate_password(username, password)

        if asyncio.iscoroutine(result):
            result = yield from result

        return result

    @asyncio.coroutine
    def change_password(self, username, old_password, new_password):
        """Handle a password change request for a user"""

        result = self._owner.change_password(username, old_password,
                                             new_password)

        if asyncio.iscoroutine(result):
            result = yield from result

        return result

    def kbdint_auth_supported(self):
        """Return whether or not keyboard-interactive authentication
           is supported"""

        result = self._owner.kbdint_auth_supported()

        if result is True:
            return True
        elif (result is NotImplemented and
              self._owner.password_auth_supported()):
            self._kbdint_password_auth = True
            return True
        else:
            return False

    @asyncio.coroutine
    def get_kbdint_challenge(self, username, lang, submethods):
        """Return a keyboard-interactive auth challenge"""

        if self._kbdint_password_auth:
            result = ('', '', DEFAULT_LANG, (('Password:', False),))
        else:
            result = self._owner.get_kbdint_challenge(username, lang,
                                                      submethods)

            if asyncio.iscoroutine(result):
                result = yield from result

        return result

    @asyncio.coroutine
    def validate_kbdint_response(self, username, responses):
        """Return whether the keyboard-interactive response is valid
           for this user"""

        if self._kbdint_password_auth:
            if len(responses) != 1:
                return False

            try:
                result = self._owner.validate_password(username, responses[0])

                if asyncio.iscoroutine(result):
                    result = yield from result
            except PasswordChangeRequired:
                # Don't support password change requests for now in
                # keyboard-interactive auth
                result = False
        else:
            result = self._owner.validate_kbdint_response(username, responses)

            if asyncio.iscoroutine(result):
                result = yield from result

        return result

    def _process_session_open(self, packet):
        """Process an incoming session open request"""

        packet.check_end()

        if self._process_factory or self._session_factory or self._sftp_factory:
            chan = self.create_server_channel(self._session_encoding,
                                              self._window, self._max_pktsize)

            if self._process_factory:
                session = SSHServerProcess(self._process_factory,
                                           self._sftp_factory,
                                           self._allow_scp)
            else:
                session = SSHServerStreamSession(self._session_factory,
                                                 self._sftp_factory,
                                                 self._allow_scp)
        else:
            result = self._owner.session_requested()

            if not result:
                raise ChannelOpenError(OPEN_CONNECT_FAILED, 'Session refused')

            if isinstance(result, tuple):
                chan, result = result
            else:
                chan = self.create_server_channel(self._session_encoding,
                                                  self._window,
                                                  self._max_pktsize)

            if callable(result):
                session = SSHServerStreamSession(result, None, False)
            else:
                session = result

        return chan, session

    def _process_direct_tcpip_open(self, packet):
        """Process an incoming direct TCP/IP open request"""

        dest_host = packet.get_string()
        dest_port = packet.get_uint32()
        orig_host = packet.get_string()
        orig_port = packet.get_uint32()
        packet.check_end()

        try:
            dest_host = dest_host.decode('utf-8')
            orig_host = orig_host.decode('utf-8')
        except UnicodeDecodeError:
            raise DisconnectError(DISC_PROTOCOL_ERROR, 'Invalid direct '
                                  'TCP/IP channel open request') from None

        if not self.check_key_permission('port-forwarding') or \
           not self.check_certificate_permission('port-forwarding'):
            raise ChannelOpenError(OPEN_ADMINISTRATIVELY_PROHIBITED,
                                   'Port forwarding not permitted')

        permitted_opens = self.get_key_option('permitopen')

        if permitted_opens and \
           (dest_host, dest_port) not in permitted_opens and \
           (dest_host, None) not in permitted_opens:
            raise ChannelOpenError(OPEN_ADMINISTRATIVELY_PROHIBITED,
                                   'Port forwarding not permitted to %s '
                                   'port %s' % (dest_host, dest_port))

        result = self._owner.connection_requested(dest_host, dest_port,
                                                  orig_host, orig_port)

        if not result:
            raise ChannelOpenError(OPEN_CONNECT_FAILED, 'Connection refused')

        if result is True:
            result = self.forward_connection(dest_host, dest_port)

        if isinstance(result, tuple):
            chan, result = result
        else:
            chan = self.create_tcp_channel()

        if callable(result):
            session = SSHTCPStreamSession(result)
        else:
            session = result

        self.logger.info('Accepted direct TCP connection request to %s',
                         (dest_host, dest_port))
        self.logger.info('  Client address: %s', (orig_host, orig_port))

        chan.set_inbound_peer_names(dest_host, dest_port, orig_host, orig_port)

        return chan, session

    def _process_tcpip_forward_global_request(self, packet):
        """Process an incoming TCP/IP port forwarding request"""

        listen_host = packet.get_string()
        listen_port = packet.get_uint32()
        packet.check_end()

        try:
            listen_host = listen_host.decode('utf-8').lower()
        except UnicodeDecodeError:
            raise DisconnectError(DISC_PROTOCOL_ERROR, 'Invalid TCP/IP port '
                                  'forward request') from None

        if not self.check_key_permission('port-forwarding') or \
           not self.check_certificate_permission('port-forwarding'):
            self.logger.info('Request for TCP listener on %s denied: port '
                             'forwarding not permitted',
                             (listen_host, listen_port))

            self._report_global_response(False)
            return

        result = self._owner.server_requested(listen_host, listen_port)

        if not result:
            self.logger.info('Request for TCP listener on %s denied by '
                             'application', (listen_host, listen_port))

            self._report_global_response(False)
            return

        if result is True:
            result = self.forward_local_port(listen_host, listen_port,
                                             listen_host, listen_port)

        self.create_task(self._finish_port_forward(result, listen_host,
                                                   listen_port))

    @asyncio.coroutine
    def _finish_port_forward(self, listener, listen_host, listen_port):
        """Finish processing a TCP/IP port forwarding request"""

        if asyncio.iscoroutine(listener):
            try:
                listener = yield from listener
            except OSError:
                listener = None

        if listener:
            if listen_port == 0:
                listen_port = listener.get_port()
                result = UInt32(listen_port)
            else:
                result = True

            self._local_listeners[listen_host, listen_port] = listener

            self.logger.info('Created TCP listener on %s',
                             (listen_host, listen_port))

            self._report_global_response(result)
        else:
            self.logger.debug1('Failed to create TCP listener')
            self._report_global_response(False)

    def _process_cancel_tcpip_forward_global_request(self, packet):
        """Process a request to cancel TCP/IP port forwarding"""

        listen_host = packet.get_string()
        listen_port = packet.get_uint32()
        packet.check_end()

        try:
            listen_host = listen_host.decode('utf-8').lower()
        except UnicodeDecodeError:
            raise DisconnectError(DISC_PROTOCOL_ERROR, 'Invalid TCP/IP cancel '
                                  'forward request') from None

        try:
            listener = self._local_listeners.pop((listen_host, listen_port))
        except KeyError:
            raise DisconnectError(DISC_PROTOCOL_ERROR, 'TCP/IP listener '
                                  'not found') from None

        self.logger.info('Closed TCP listener on %s',
                         (listen_host, listen_port))

        listener.close()

        self._report_global_response(True)

    def _process_direct_streamlocal_at_openssh_dot_com_open(self, packet):
        """Process an incoming direct UNIX domain socket open request"""

        dest_path = packet.get_string()

        # OpenSSH appears to have a bug which sends this extra data
        _ = packet.get_string()                         # originator
        _ = packet.get_uint32()                         # originator_port

        packet.check_end()

        try:
            dest_path = dest_path.decode('utf-8')
        except UnicodeDecodeError:
            raise DisconnectError(DISC_PROTOCOL_ERROR, 'Invalid direct UNIX '
                                  'domain channel open request') from None

        if not self.check_key_permission('port-forwarding') or \
           not self.check_certificate_permission('port-forwarding'):
            raise ChannelOpenError(OPEN_ADMINISTRATIVELY_PROHIBITED,
                                   'Port forwarding not permitted')

        result = self._owner.unix_connection_requested(dest_path)

        if not result:
            raise ChannelOpenError(OPEN_CONNECT_FAILED, 'Connection refused')

        if result is True:
            result = self.forward_unix_connection(dest_path)

        if isinstance(result, tuple):
            chan, result = result
        else:
            chan = self.create_unix_channel()

        if callable(result):
            session = SSHUNIXStreamSession(result)
        else:
            session = result

        self.logger.info('Accepted direct UNIX connection on %s', dest_path)

        chan.set_inbound_peer_names(dest_path)

        return chan, session

    def _process_streamlocal_forward_at_openssh_dot_com_global_request(self,
                                                                       packet):
        """Process an incoming UNIX domain socket forwarding request"""

        listen_path = packet.get_string()
        packet.check_end()

        try:
            listen_path = listen_path.decode('utf-8')
        except UnicodeDecodeError:
            raise DisconnectError(DISC_PROTOCOL_ERROR, 'Invalid UNIX domain '
                                  'socket forward request') from None

        if not self.check_key_permission('port-forwarding') or \
           not self.check_certificate_permission('port-forwarding'):
            self.logger.info('Request for UNIX listener on %s denied: port '
                             'forwarding not permitted', listen_path)

            self._report_global_response(False)
            return

        result = self._owner.unix_server_requested(listen_path)

        if not result:
            self.logger.info('Request for UNIX listener on %s denied by '
                             'application', listen_path)

            self._report_global_response(False)
            return

        self.logger.info('Creating UNIX listener on %s', listen_path)

        if result is True:
            result = self.forward_local_path(listen_path, listen_path)

        self.create_task(self._finish_path_forward(result, listen_path))

    @asyncio.coroutine
    def _finish_path_forward(self, listener, listen_path):
        """Finish processing a UNIX domain socket forwarding request"""

        if asyncio.iscoroutine(listener):
            try:
                listener = yield from listener
            except OSError:
                listener = None

        if listener:
            self._local_listeners[listen_path] = listener
            self._report_global_response(True)
        else:
            self.logger.debug1('Failed to create UNIX listener')
            self._report_global_response(False)

    def _process_cancel_streamlocal_forward_at_openssh_dot_com_global_request(
            self, packet):
        """Process a request to cancel UNIX domain socket forwarding"""

        listen_path = packet.get_string()
        packet.check_end()

        try:
            listen_path = listen_path.decode('utf-8')
        except UnicodeDecodeError:
            raise DisconnectError(DISC_PROTOCOL_ERROR, 'Invalid UNIX domain '
                                  'cancel forward request') from None

        try:
            listener = self._local_listeners.pop(listen_path)
        except KeyError:
            raise DisconnectError(DISC_PROTOCOL_ERROR, 'UNIX domain listener '
                                  'not found') from None

        self.logger.info('Closed UNIX listener on %s', listen_path)

        listener.close()

        self._report_global_response(True)

    @asyncio.coroutine
    def attach_x11_listener(self, chan, auth_proto, auth_data, screen):
        """Attach a channel to a remote X11 display"""

        if (not self._x11_forwarding or
                not self.check_key_permission('X11-forwarding') or
                not self.check_certificate_permission('X11-forwarding')):
            self.logger.info('X11 forwarding request denied: X11 '
                             'forwarding not permitted')

            return None

        if not self._x11_listener:
            self._x11_listener = yield from create_x11_server_listener(
                self, self._loop, self._x11_auth_path, auth_proto, auth_data)

        if self._x11_listener:
            return self._x11_listener.attach(chan, screen)
        else:
            return None

    def detach_x11_listener(self, chan):
        """Detach a session from a remote X11 listener"""

        if self._x11_listener:
            if self._x11_listener.detach(chan):
                self._x11_listener = None

    def create_agent_listener(self):
        """Create a listener for forwarding ssh-agent connections"""

        if (not self._agent_forwarding or
                not self.check_key_permission('agent-forwarding') or
                not self.check_certificate_permission('agent-forwarding')):
            self.logger.info('Agent forwarding request denied: Agent '
                             'forwarding not permitted')

            return False

        if not self._agent_listener:
            self._agent_listener = yield from create_agent_listener(self,
                                                                    self._loop)

        return bool(self._agent_listener)

    def get_agent_path(self):
        """Return the path of the ssh-agent listener, if one exists"""

        if self._agent_listener:
            return self._agent_listener.get_path()
        else:
            return None

    def send_auth_banner(self, msg, lang=DEFAULT_LANG):
        """Send an authentication banner to the client

           This method can be called to send an authentication banner to
           the client, displaying information while authentication is
           in progress. It is an error to call this method after the
           authentication is complete.

           :param msg:
               The message to display
           :param lang:
               The language the message is in
           :type msg: `str`
           :type lang: `str`

           :raises: :exc:`OSError` if authentication is already completed

        """

        if self._auth_complete:
            raise OSError('Authentication already completed')

        self.logger.debug1('Sending authentication banner')

        self.send_packet(MSG_USERAUTH_BANNER, String(msg), String(lang))

    def set_authorized_keys(self, authorized_keys):
        """Set the keys trusted for client public key authentication

           This method can be called to set the trusted user and
           CA keys for client public key authentication. It should
           generally be called from the :meth:`begin_auth
           <SSHServer.begin_auth>` method of :class:`SSHServer` to
           set the appropriate keys for the user attempting to
           authenticate.

           :param authorized_keys:
               The keys to trust for client public key authentication
           :type authorized_keys: *see* :ref:`SpecifyingAuthorizedKeys`

        """

        if isinstance(authorized_keys, str):
            authorized_keys = read_authorized_keys(authorized_keys)

        self._client_keys = authorized_keys

    def get_key_option(self, option, default=None):
        """Return option from authorized_keys

           If a client key or certificate was presented during authentication,
           this method returns the value of the requested option in the
           corresponding authorized_keys entry if it was set. Otherwise, it
           returns the default value provided.

           The following standard options are supported:

               | command (string)
               | environment (dictionary of name/value pairs)
               | from (list of host patterns)
               | permitopen (list of host/port tuples)
               | principals (list of usernames)

           Non-standard options are also supported and will return the
           value `True` if the option is present without a value or
           return a list of strings containing the values associated
           with each occurrence of that option name. If the option is
           not present, the specified default value is returned.

           :param option:
               The name of the option to look up.
           :param default:
               The default value to return if the option is not present.
           :type option: `str`

           :returns: The value of the option in authorized_keys, if set

        """

        return self._key_options.get(option, default)

    def check_key_permission(self, permission):
        """Check permissions in authorized_keys

           If a client key or certificate was presented during
           authentication, this method returns whether the specified
           permission is allowed by the corresponding authorized_keys
           entry. By default, all permissions are granted, but they
           can be revoked by specifying an option starting with
           'no-' without a value.

           The following standard options are supported:

               | X11-forwarding
               | agent-forwarding
               | port-forwarding
               | pty
               | user-rc

           AsyncSSH internally enforces X11-forwarding, agent-forwarding,
           port-forwarding and pty permissions but ignores user-rc since
           it does not implement that feature.

           Non-standard permissions can also be checked, as long as the
           option follows the convention of starting with 'no-'.

           :param permission:
               The name of the permission to check (without the 'no-').
           :type permission: `str`

           :returns: A `bool` indicating if the permission is granted.

        """

        return not self._key_options.get('no-' + permission, False)

    def get_certificate_option(self, option, default=None):
        """Return option from user certificate

           If a user certificate was presented during authentication,
           this method returns the value of the requested option in
           the certificate if it was set. Otherwise, it returns the
           default value provided.

           The following options are supported:

               | force-command (string)
               | source-address (list of CIDR-style IP network addresses)

           :param option:
               The name of the option to look up.
           :param default:
               The default value to return if the option is not present.
           :type option: `str`

           :returns: The value of the option in the user certificate, if set

        """

        if self._cert_options is not None:
            return self._cert_options.get(option, default)
        else:
            return default

    def check_certificate_permission(self, permission):
        """Check permissions in user certificate

           If a user certificate was presented during authentication,
           this method returns whether the specified permission was
           granted in the certificate. Otherwise, it acts as if all
           permissions are granted and returns `True`.

           The following permissions are supported:

               | X11-forwarding
               | agent-forwarding
               | port-forwarding
               | pty
               | user-rc

           AsyncSSH internally enforces agent-forwarding, port-forwarding
           and pty permissions but ignores the other values since it does
           not implement those features.

           :param permission:
               The name of the permission to check (without the 'permit-').
           :type permission: `str`

           :returns: A `bool` indicating if the permission is granted.

        """

        if self._cert_options is not None:
            return self._cert_options.get('permit-' + permission, False)
        else:
            return True

    def create_server_channel(self, encoding='utf-8', window=_DEFAULT_WINDOW,
                              max_pktsize=_DEFAULT_MAX_PKTSIZE):
        """Create an SSH server channel for a new SSH session

           This method can be called by :meth:`session_requested()
           <SSHServer.session_requested>` to create an
           :class:`SSHServerChannel` with the desired encoding, window,
           and max packet size for a newly created SSH server session.

           :param encoding: (optional)
               The Unicode encoding to use for data exchanged on the
               session, defaulting to UTF-8 (ISO 10646) format. If `None`
               is passed in, the application can send and receive raw
               bytes.
           :param window: (optional)
               The receive window size for this session
           :param max_pktsize: (optional)
               The maximum packet size for this session
           :type encoding: `str`
           :type window: `int`
           :type max_pktsize: `int`

           :returns: :class:`SSHServerChannel`

        """

        return SSHServerChannel(self, self._loop, self._allow_pty,
                                self._line_editor, self._line_history,
                                encoding, window, max_pktsize)

    @asyncio.coroutine
    def create_connection(self, session_factory, remote_host, remote_port,
                          orig_host='', orig_port=0, *, encoding=None,
                          window=_DEFAULT_WINDOW,
                          max_pktsize=_DEFAULT_MAX_PKTSIZE):
        """Create an SSH TCP forwarded connection

           This method is a coroutine which can be called to notify the
           client about a new inbound TCP connection arriving on the
           specified remote host and port. If the connection is successfully
           opened, a new SSH channel will be opened with data being handled
           by a :class:`SSHTCPSession` object created by `session_factory`.

           Optional arguments include the host and port of the original
           client opening the connection when performing TCP port forwarding.

           By default, this class expects data to be sent and received as
           raw bytes. However, an optional encoding argument can be
           passed in to select the encoding to use, allowing the
           application send and receive string data.

           Other optional arguments include the SSH receive window size and
           max packet size which default to 2 MB and 32 KB, respectively.

           :param session_factory:
               A `callable` which returns an :class:`SSHClientSession` object
               that will be created to handle activity on this session
           :param remote_host:
               The hostname or address the connection was received on
           :param remote_port:
               The port number the connection was received on
           :param orig_host: (optional)
               The hostname or address of the client requesting the connection
           :param orig_port: (optional)
               The port number of the client requesting the connection
           :param encoding: (optional)
               The Unicode encoding to use for data exchanged on the connection
           :param window: (optional)
               The receive window size for this session
           :param max_pktsize: (optional)
               The maximum packet size for this session
           :type session_factory: `callable`
           :type remote_host: `str`
           :type remote_port: `int`
           :type orig_host: `str`
           :type orig_port: `int`
           :type encoding: `str`
           :type window: `int`
           :type max_pktsize: `int`

           :returns: an :class:`SSHTCPChannel` and :class:`SSHTCPSession`

        """

        self.logger.info('Opening forwarded TCP connection to %s',
                         (remote_host, remote_port))
        self.logger.info('  Client address: %s', (orig_host, orig_port))

        chan = self.create_tcp_channel(encoding, window, max_pktsize)

        session = yield from chan.accept(session_factory, remote_host,
                                         remote_port, orig_host, orig_port)

        return chan, session

    @asyncio.coroutine
    def open_connection(self, *args, **kwargs):
        """Open an SSH TCP forwarded connection

           This method is a coroutine wrapper around :meth:`create_connection`
           designed to provide a "high-level" stream interface for creating
           an SSH TCP forwarded connection. Instead of taking a
           `session_factory` argument for constructing an object which will
           handle activity on the session via callbacks, it returns
           :class:`SSHReader` and :class:`SSHWriter` objects which can be
           used to perform I/O on the connection.

           With the exception of `session_factory`, all of the arguments
           to :meth:`create_connection` are supported and have the same
           meaning here.

           :returns: an :class:`SSHReader` and :class:`SSHWriter`

        """

        chan, session = yield from self.create_connection(SSHTCPStreamSession,
                                                          *args, **kwargs)

        return SSHReader(session, chan), SSHWriter(session, chan)

    @asyncio.coroutine
    def create_unix_connection(self, session_factory, remote_path, *,
                               encoding=None, window=_DEFAULT_WINDOW,
                               max_pktsize=_DEFAULT_MAX_PKTSIZE):
        """Create an SSH UNIX domain socket forwarded connection

           This method is a coroutine which can be called to notify the
           client about a new inbound UNIX domain socket connection arriving
           on the specified remote path. If the connection is successfully
           opened, a new SSH channel will be opened with data being handled
           by a :class:`SSHUNIXSession` object created by `session_factory`.

           By default, this class expects data to be sent and received as
           raw bytes. However, an optional encoding argument can be
           passed in to select the encoding to use, allowing the
           application send and receive string data.

           Other optional arguments include the SSH receive window size and
           max packet size which default to 2 MB and 32 KB, respectively.

           :param session_factory:
               A `callable` which returns an :class:`SSHClientSession` object
               that will be created to handle activity on this session
           :param remote_path:
               The path the connection was received on
           :param encoding: (optional)
               The Unicode encoding to use for data exchanged on the connection
           :param window: (optional)
               The receive window size for this session
           :param max_pktsize: (optional)
               The maximum packet size for this session
           :type session_factory: `callable`
           :type remote_path: `str`
           :type encoding: `str`
           :type window: `int`
           :type max_pktsize: `int`

           :returns: an :class:`SSHTCPChannel` and :class:`SSHUNIXSession`

        """

        self.logger.info('Opening forwarded UNIX connection to %s', remote_path)

        chan = self.create_unix_channel(encoding, window, max_pktsize)

        session = yield from chan.accept(session_factory, remote_path)

        return chan, session

    @asyncio.coroutine
    def open_unix_connection(self, *args, **kwargs):
        """Open an SSH UNIX domain socket forwarded connection

           This method is a coroutine wrapper around
           :meth:`create_unix_connection` designed to provide a "high-level"
           stream interface for creating an SSH UNIX domain socket forwarded
           connection. Instead of taking a `session_factory` argument for
           constructing an object which will handle activity on the session
           via callbacks, it returns :class:`SSHReader` and :class:`SSHWriter`
           objects which can be used to perform I/O on the connection.

           With the exception of `session_factory`, all of the arguments
           to :meth:`create_unix_connection` are supported and have the same
           meaning here.

           :returns: an :class:`SSHReader` and :class:`SSHWriter`

        """

        chan, session = \
            yield from self.create_unix_connection(SSHUNIXStreamSession,
                                                   *args, **kwargs)

        return SSHReader(session, chan), SSHWriter(session, chan)

    @asyncio.coroutine
    def create_x11_connection(self, session_factory, orig_host='',
                              orig_port=0, *, window=_DEFAULT_WINDOW,
                              max_pktsize=_DEFAULT_MAX_PKTSIZE):
        """Create an SSH X11 forwarded connection"""

        self.logger.info('Opening forwarded X11 connection')

        chan = self.create_x11_channel(None, window, max_pktsize)

        session = yield from chan.open(session_factory, orig_host, orig_port)

        return chan, session

    @asyncio.coroutine
    def create_agent_connection(self, session_factory, *,
                                encoding=None, window=_DEFAULT_WINDOW,
                                max_pktsize=_DEFAULT_MAX_PKTSIZE):
        """Create a forwarded ssh-agent connection back to the client"""

        if not self._agent_listener:
            raise ChannelOpenError(OPEN_ADMINISTRATIVELY_PROHIBITED,
                                   'Agent forwarding not permitted')

        self.logger.info('Opening forwarded agent connection')

        chan = self.create_agent_channel(encoding, window, max_pktsize)

        session = yield from chan.open(session_factory)

        return chan, session

    @asyncio.coroutine
    def open_agent_connection(self):
        """Open a forwarded ssh-agent connection back to the client"""

        chan, session = \
            yield from self.create_agent_connection(SSHUNIXStreamSession)

        return SSHReader(session, chan), SSHWriter(session, chan)


@asyncio.coroutine
def create_connection(client_factory, host, port=_DEFAULT_PORT, *,
                      loop=None, tunnel=None, family=0, flags=0,
                      local_addr=None, known_hosts=(), x509_trusted_certs=(),
                      x509_trusted_cert_paths=(),
                      x509_purposes='secureShellServer', username=None,
                      password=None, client_host_keys=None, client_host=None,
                      client_username=None, client_keys=(), passphrase=None,
                      gss_host=(), gss_delegate_creds=False,
                      agent_path=(), agent_forwarding=False,
                      client_version=(), kex_algs=(), encryption_algs=(),
                      mac_algs=(), compression_algs=(), signature_algs=(),
                      rekey_bytes=_DEFAULT_REKEY_BYTES,
                      rekey_seconds=_DEFAULT_REKEY_SECONDS):
    """Create an SSH client connection

       This function is a coroutine which can be run to create an outbound SSH
       client connection to the specified host and port.

       When successful, the following steps occur:

           1. The connection is established and an :class:`SSHClientConnection`
              object is created to represent it.
           2. The `client_factory` is called without arguments and should
              return an :class:`SSHClient` object.
           3. The client object is tied to the connection and its
              :meth:`connection_made() <SSHClient.connection_made>` method
              is called.
           4. The SSH handshake and authentication process is initiated,
              calling methods on the client object if needed.
           5. When authentication completes successfully, the client's
              :meth:`auth_completed() <SSHClient.auth_completed>` method is
              called.
           6. The coroutine returns the `(connection, client)` pair. At
              this point, the connection is ready for sessions to be opened
              or port forwarding to be set up.

       If an error occurs, it will be raised as an exception and the partially
       open connection and client objects will be cleaned up.

       .. note:: Unlike :func:`socket.create_connection`, asyncio calls
                 to create a connection do not support a `timeout`
                 parameter. However, asyncio calls can be wrapped in a
                 call to :func:`asyncio.wait_for` or :func:`asyncio.wait`
                 which takes a timeout and provides equivalent functionality.

       :param client_factory:
           A `callable` which returns an :class:`SSHClient` object that will
           be tied to the connection
       :param host:
           The hostname or address to connect to
       :param port: (optional)
           The port number to connect to. If not specified, the default
           SSH port is used.
       :param loop: (optional)
           The event loop to use when creating the connection. If not
           specified, the default event loop is used.
       :param tunnel: (optional)
           An existing SSH client connection that this new connection should
           be tunneled over. If set, a direct TCP/IP tunnel will be opened
           over this connection to the requested host and port rather than
           connecting directly via TCP.
       :param family: (optional)
           The address family to use when creating the socket. By default,
           the address family is automatically selected based on the host.
       :param flags: (optional)
           The flags to pass to getaddrinfo() when looking up the host address
       :param local_addr: (optional)
           The host and port to bind the socket to before connecting
       :param known_hosts: (optional)
           The list of keys which will be used to validate the server host
           key presented during the SSH handshake. If this is not specified,
           the keys will be looked up in the file :file:`.ssh/known_hosts`.
           If this is explicitly set to `None`, server host key validation
           will be disabled.
       :param x509_trusted_certs: (optional)
           A list of certificates which should be trusted for X.509 server
           certificate authentication. If no trusted certificates are
           specified, an attempt will be made to load them from the file
           :file:`.ssh/ca-bundle.crt`. If this argument is explicitly set
           to `None`, X.509 server certificate authentication will not
           be performed.

               .. note:: X.509 certificates to trust can also be provided
                         through a :ref:`known_hosts <KnownHosts>` file
                         if they are converted into OpenSSH format.
                         This allows their trust to be limited to only
                         specific host names.
       :param x509_trusted_cert_paths: (optional)
           A list of path names to "hash directories" containing certificates
           which should be trusted for X.509 server certificate authentication.
           Each certificate should be in a separate file with a name of the
           form *hash.number*, where *hash* is the OpenSSL hash value of the
           certificate subject name and *number* is an integer counting up
           from zero if multiple certificates have the same hash. If no
           paths are specified, an attempt with be made to use the directory
           :file:`.ssh/crt` as a certificate hash directory.
       :param x509_purposes: (optional)
           A list of purposes allowed in the ExtendedKeyUsage of a
           certificate used for X.509 server certificate authentication,
           defulting to 'secureShellServer'. If this argument is explicitly
           set to `None`, the server certificate's ExtendedKeyUsage will
           not be checked.
       :param username: (optional)
           Username to authenticate as on the server. If not specified,
           the currently logged in user on the local machine will be used.
       :param password: (optional)
           The password to use for client password authentication or
           keyboard-interactive authentication which prompts for a password.
           If this is not specified, client password authentication will
           not be performed.
       :param client_host_keys: (optional)
           A list of keys to use to authenticate this client via host-based
           authentication. If this is not specified, host-based public key
           authentication will not be performed.
       :param client_host: (optional)
           The host name to use when performing host-based authentication.
           If not specified, the value returned by :func:`socket.gethostname`
           will be used if it is a fully qualified name. Otherwise, the value
           used by :func:`socket.getfqdn` will be used.
       :param client_username: (optional)
           Username of the user on the local machine, used for host-based
           authentication. If not specified, the username of the currently
           logged in user will be used.
       :param client_keys: (optional)
           A list of keys which will be used to authenticate this client
           via public key authentication. If no client keys are specified,
           an attempt will be made to get them from an ssh-agent process.
           If that is not available, an attempt will be made to load them
           from the files :file:`.ssh/id_ed25519`, :file:`.ssh/id_ecdsa`,
           :file:`.ssh/id_rsa`, and :file:`.ssh/id_dsa` in the user's home
           directory, with optional certificates loaded from the files
           :file:`.ssh/id_ed25519-cert.pub`, :file:`.ssh/id_ecdsa-cert.pub`,
           :file:`.ssh/id_rsa-cert.pub`, and :file:`.ssh/id_dsa-cert.pub`.
           If this argument is explicitly set to `None`, client public
           key authentication will not be performed.
       :param passphrase: (optional)
           The passphrase to use to decrypt client keys when loading them,
           if they are encrypted. If this is not specified, only unencrypted
           client keys can be loaded. If the keys passed into client_keys
           are already loaded, this argument is ignored.
       :param gss_host: (optional)
           The principal name to use for the host in GSS key exchange and
           authentication. If not specified, this value will be the same
           as the `host` argument. If this argument is explicitly set to
           `None`, GSS key exchange and authentication will not be performed.
       :param gss_delegate_creds: (optional)
           Whether or not to forward GSS credentials to the server being
           accessed. By default, GSS credential delegation is disabled.
       :param agent_path: (optional)
           The path of a UNIX domain socket to use to contact an ssh-agent
           process which will perform the operations needed for client
           public key authentication, or the :class:`SSHServerConnection`
           to use to forward ssh-agent requests over. If this is not
           specified and the environment variable `SSH_AUTH_SOCK` is
           set, its value will be used as the path.  If `client_keys`
           is specified or this argument is explicitly set to `None`,
           an ssh-agent will not be used.
       :param agent_forwarding: (optional)
           Whether or not to allow forwarding of ssh-agent requests from
           processes running on the server. By default, ssh-agent forwarding
           requests from the server are not allowed.
       :param client_version: (optional)
           An ASCII string to advertise to the SSH server as the version of
           this client, defaulting to `'AsyncSSH'` and its version number.
       :param kex_algs: (optional)
           A list of allowed key exchange algorithms in the SSH handshake,
           taken from :ref:`key exchange algorithms <KexAlgs>`
       :param encryption_algs: (optional)
           A list of encryption algorithms to use during the SSH handshake,
           taken from :ref:`encryption algorithms <EncryptionAlgs>`
       :param mac_algs: (optional)
           A list of MAC algorithms to use during the SSH handshake, taken
           from :ref:`MAC algorithms <MACAlgs>`
       :param compression_algs: (optional)
           A list of compression algorithms to use during the SSH handshake,
           taken from :ref:`compression algorithms <CompressionAlgs>`, or
           `None` to disable compression
       :param signature_algs: (optional)
           A list of public key signature algorithms to use during the SSH
           handshake, taken from :ref:`signature algorithms <SignatureAlgs>`
       :param rekey_bytes: (optional)
           The number of bytes which can be sent before the SSH session
           key is renegotiated. This defaults to 1 GB.
       :param rekey_seconds: (optional)
           The maximum time in seconds before the SSH session key is
           renegotiated. This defaults to 1 hour.
       :type client_factory: `callable`
       :type host: `str`
       :type port: `int`
       :type loop: :class:`AbstractEventLoop <asyncio.AbstractEventLoop>`
       :type tunnel: :class:`SSHClientConnection`
       :type family: `socket.AF_UNSPEC`, `socket.AF_INET`, or `socket.AF_INET6`
       :type flags: flags to pass to :meth:`getaddrinfo() <socket.getaddrinfo>`
       :type local_addr: tuple of `str` and `int`
       :type known_hosts: *see* :ref:`SpecifyingKnownHosts`
       :type x509_trusted_certs: *see* :ref:`SpecifyingCertificates`
       :type x509_trusted_cert_paths: `list` of `str`
       :type x509_purposes: *see* :ref:`SpecifyingX509Purposes`
       :type username: `str`
       :type password: `str`
       :type client_host_keys: *see* :ref:`SpecifyingPrivateKeys`
       :type client_host: `str`
       :type client_username: `str`
       :type client_keys: *see* :ref:`SpecifyingPrivateKeys`
       :type passphrase: `str`
       :type gss_host: `str`
       :type gss_delegate_creds: `bool`
       :type agent_path: `str` or :class:`SSHServerConnection`
       :type agent_forwarding: `bool`
       :type client_version: `str`
       :type kex_algs: `list` of `str`
       :type encryption_algs: `list` of `str`
       :type mac_algs: `list` of `str`
       :type compression_algs: `list` of `str`
       :type signature_algs: `list` of `str`
       :type rekey_bytes: `int`
       :type rekey_seconds: `int`

       :returns: An :class:`SSHClientConnection` and :class:`SSHClient`

    """

    def conn_factory():
        """Return an SSH client connection handler"""

        return SSHClientConnection(client_factory, loop, client_version,
                                   x509_trusted_certs, x509_trusted_cert_paths,
                                   x509_purposes, kex_algs, encryption_algs,
                                   mac_algs, compression_algs, signature_algs,
                                   rekey_bytes, rekey_seconds, host, port,
                                   known_hosts, username, password,
                                   client_host_keys, client_host,
                                   client_username, client_keys, gss_host,
                                   gss_delegate_creds, agent, agent_path,
                                   auth_waiter)

    if not client_factory:
        client_factory = SSHClient

    if not loop:
        loop = asyncio.get_event_loop()

    client_version = _validate_version(client_version)

    kex_algs, encryption_algs, mac_algs, compression_algs, signature_algs = \
        _validate_algs(kex_algs, encryption_algs, mac_algs, compression_algs,
                       signature_algs, x509_trusted_certs is not None)

    if x509_trusted_certs == ():
        try:
            x509_trusted_certs = load_certificates(
                os.path.join(os.path.expanduser('~'), '.ssh', 'ca-bundle.crt'))
        except OSError:
            pass
    elif x509_trusted_certs is not None:
        x509_trusted_certs = load_certificates(x509_trusted_certs)

    if x509_trusted_cert_paths == ():
        path = os.path.join(os.path.expanduser('~'), '.ssh', 'crt')
        if os.path.isdir(path):
            x509_trusted_cert_paths = [path]
    elif x509_trusted_cert_paths:
        for path in x509_trusted_cert_paths:
            if not os.path.isdir(path):
                raise ValueError('Path not a directory: ' + str(path))

    if username is None:
        username = getpass.getuser()

    username = saslprep(username)

    client_host_keys = load_keypairs(client_host_keys, passphrase)

    if client_username is None:
        client_username = getpass.getuser()

    client_username = saslprep(client_username)

    if gss_host == ():
        gss_host = host

    agent = None

    if agent_path == ():
        agent_path = os.environ.get('SSH_AUTH_SOCK', None)

    if client_keys:
        client_keys = load_keypairs(client_keys, passphrase)
    elif client_keys == ():
        if agent_path:
            agent = yield from connect_agent(agent_path, loop=loop)

            if agent:
                client_keys = yield from agent.get_keys()
            else:
                agent_path = None

        if not client_keys:
            client_keys = load_default_keypairs(passphrase)

    if not agent_forwarding:
        agent_path = None

    auth_waiter = asyncio.Future(loop=loop)

    # pylint: disable=broad-except
    try:
        if tunnel:
            tunnel_logger = getattr(tunnel, 'logger', logger)
            tunnel_logger.info('Opening SSH tunnel to %s', (host, port))
            _, conn = yield from tunnel.create_connection(conn_factory, host,
                                                          port)
        else:
            logger.info('Opening SSH connection to %s', (host, port))
            _, conn = yield from loop.create_connection(conn_factory, host,
                                                        port, family=family,
                                                        flags=flags,
                                                        local_addr=local_addr)
    except Exception:
        if agent:
            agent.close()

        raise

    yield from auth_waiter

    return conn, conn.get_owner()


@asyncio.coroutine
def create_server(server_factory, host=None, port=_DEFAULT_PORT, *,
                  loop=None, family=0, flags=socket.AI_PASSIVE, backlog=100,
                  reuse_address=None, server_host_keys=None, passphrase=None,
                  known_client_hosts=None, trust_client_host=False,
                  authorized_client_keys=None, x509_trusted_certs=(),
                  x509_trusted_cert_paths=(), x509_purposes='secureShellClient',
                  gss_host=(), allow_pty=True, line_editor=True,
                  line_history=_DEFAULT_LINE_HISTORY,
                  x11_forwarding=False, x11_auth_path=None,
                  agent_forwarding=True, process_factory=None,
                  session_factory=None, session_encoding='utf-8',
                  sftp_factory=None, allow_scp=False, window=_DEFAULT_WINDOW,
                  max_pktsize=_DEFAULT_MAX_PKTSIZE, server_version=(),
                  kex_algs=(), encryption_algs=(), mac_algs=(),
                  compression_algs=(), signature_algs=(),
                  rekey_bytes=_DEFAULT_REKEY_BYTES,
                  rekey_seconds=_DEFAULT_REKEY_SECONDS,
                  login_timeout=_DEFAULT_LOGIN_TIMEOUT):
    """Create an SSH server

       This function is a coroutine which can be run to create an SSH server
       bound to the specified host and port. The return value is an object
       derived from :class:`asyncio.Server` which can be used to later shut
       down the server.

       :param server_factory:
           A `callable` which returns an :class:`SSHServer` object that will
           be created for each new inbound connection
       :param host: (optional)
           The hostname or address to listen on. If not specified, listeners
           are created for all addresses.
       :param port: (optional)
           The port number to listen on. If not specified, the default
           SSH port is used.
       :param loop: (optional)
           The event loop to use when creating the server. If not
           specified, the default event loop is used.
       :param family: (optional)
           The address family to use when creating the server. By default,
           the address families are automatically selected based on the host.
       :param flags: (optional)
           The flags to pass to getaddrinfo() when looking up the host
       :param backlog: (optional)
           The maximum number of queued connections allowed on listeners
       :param reuse_address: (optional)
           Whether or not to reuse a local socket in the TIME_WAIT state
           without waiting for its natural timeout to expire. If not
           specified, this will be automatically set to `True` on UNIX.
       :param server_host_keys: (optional)
           A list of private keys and optional certificates which can be
           used by the server as a host key. Either this argument or
           `gss_host` must be specified. If this is not specified,
           only GSS-based key exchange will be supported.
       :param passphrase: (optional)
           The passphrase to use to decrypt server host keys when loading
           them, if they are encrypted. If this is not specified, only
           unencrypted server host keys can be loaded. If the keys passed
           into server_host_keys are already loaded, this argument is
           ignored.
       :param known_client_hosts: (optional)
           A list of client hosts which should be trusted to perform
           host-based client authentication. If this is not specified,
           host-based client authentication will be not be performed.
       :param trust_client_host: (optional)
           Whether or not to use the hostname provided by the client
           when performing host-based authentication. By default, the
           client-provided hostname is not trusted and is instead
           determined by doing a reverse lookup of the IP address the
           client connected from.
       :param authorized_client_keys: (optional)
           A list of authorized user and CA public keys which should be
           trusted for certifcate-based client public key authentication.
       :param x509_trusted_certs: (optional)
           A list of certificates which should be trusted for X.509 client
           certificate authentication.  If this argument is explicitly set
           to `None`, X.509 client certificate authentication will not
           be performed.

               .. note:: X.509 certificates to trust can also be provided
                         through an :ref:`authorized_keys <AuthorizedKeys>`
                         file if they are converted into OpenSSH format.
                         This allows their trust to be limited to only
                         specific client IPs or user names and allows
                         SSH functions to be restricted when these
                         certificates are used.
       :param x509_trusted_cert_paths: (optional)
           A list of path names to "hash directories" containing certificates
           which should be trusted for X.509 client certificate authentication.
           Each certificate should be in a separate file with a name of the
           form *hash.number*, where *hash* is the OpenSSL hash value of the
           certificate subject name and *number* is an integer counting up
           from zero if multiple certificates have the same hash.
       :param x509_purposes: (optional)
           A list of purposes allowed in the ExtendedKeyUsage of a
           certificate used for X.509 client certificate authentication,
           defulting to 'secureShellClient'. If this argument is explicitly
           set to `None`, the client certificate's ExtendedKeyUsage will
           not be checked.
       :param gss_host: (optional)
           The principal name to use for the host in GSS key exchange and
           authentication. If not specified, the value returned by
           :func:`socket.gethostname` will be used if it is a fully qualified
           name. Otherwise, the value used by :func:`socket.getfqdn` will be
           used. If this argument is explicitly set to `None`, GSS
           key exchange and authentication will not be performed.
       :param allow_pty: (optional)
           Whether or not to allow allocation of a pseudo-tty in sessions,
           defaulting to `True`
       :param line_editor: (optional)
           Whether or not to enable input line editing on sessions which
           have a pseudo-tty allocated, defaulting to `True`
       :param line_history: (int)
           The number of lines of input line history to store in the
           line editor when it is enabled, defaulting to 1000
       :param x11_forwarding: (optional)
           Whether or not to allow forwarding of X11 connections back
           to the client when the client supports it, defaulting to `False`
       :param x11_auth_path: (optional)
           The path to the Xauthority file to write X11 authentication
           data to, defaulting to the value in the environment variable
           `XAUTHORITY` or the file :file:`.Xauthority` in the user's
           home directory if that's not set
       :param agent_forwarding: (optional)
           Whether or not to allow forwarding of ssh-agent requests back
           to the client when the client supports it, defaulting to `True`
       :param process_factory: (optional)
           A `callable` or coroutine handler function which takes an AsyncSSH
           :class:`SSHServerProcess` argument that will be called each time a
           new shell, exec, or subsystem other than SFTP is requested by the
           client. If set, this takes precedence over the `session_factory`
           argument.
       :param session_factory: (optional)
           A `callable` or coroutine handler function which takes AsyncSSH
           stream objects for stdin, stdout, and stderr that will be called
           each time a new shell, exec, or subsystem other than SFTP is
           requested by the client. If not specified, sessions are rejected
           by default unless the :meth:`session_requested()
           <SSHServer.session_requested>` method is overridden on the
           :class:`SSHServer` object returned by `server_factory` to make
           this decision.
       :param session_encoding: (optional)
           The Unicode encoding to use for data exchanged on sessions on
           this server, defaulting to UTF-8 (ISO 10646) format. If `None`
           is passed in, the application can send and receive raw bytes.
       :param sftp_factory: (optional)
           A `callable` which returns an :class:`SFTPServer` object that
           will be created each time an SFTP session is requested by the
           client, or `True` to use the base :class:`SFTPServer` class
           to handle SFTP requests. If not specified, SFTP sessions are
           rejected by default.
       :param allow_scp: (optional)
           Whether or not to allow incoming scp requests to be accepted.
           This option can only be used in conjunction with `sftp_factory`.
           If not specified, scp requests will be passed as regular
           commands to the `process_factory` or `session_factory`.
           to the client when the client supports it, defaulting to `True`
       :param window: (optional)
           The receive window size for sessions on this server
       :param max_pktsize: (optional)
           The maximum packet size for sessions on this server
       :param server_version: (optional)
           An ASCII string to advertise to SSH clients as the version of
           this server, defaulting to `'AsyncSSH'` and its version number.
       :param kex_algs: (optional)
           A list of allowed key exchange algorithms in the SSH handshake,
           taken from :ref:`key exchange algorithms <KexAlgs>`
       :param encryption_algs: (optional)
           A list of encryption algorithms to use during the SSH handshake,
           taken from :ref:`encryption algorithms <EncryptionAlgs>`
       :param mac_algs: (optional)
           A list of MAC algorithms to use during the SSH handshake, taken
           from :ref:`MAC algorithms <MACAlgs>`
       :param compression_algs: (optional)
           A list of compression algorithms to use during the SSH handshake,
           taken from :ref:`compression algorithms <CompressionAlgs>`, or
           `None` to disable compression
       :param signature_algs: (optional)
           A list of public key signature algorithms to use during the SSH
           handshake, taken from :ref:`signature algorithms <SignatureAlgs>`
       :param rekey_bytes: (optional)
           The number of bytes which can be sent before the SSH session
           key is renegotiated, defaulting to 1 GB
       :param rekey_seconds: (optional)
           The maximum time in seconds before the SSH session key is
           renegotiated, defaulting to 1 hour
       :param login_timeout: (optional)
           The maximum time in seconds allowed for authentication to
           complete, defaulting to 2 minutes
       :type server_factory: `callable`
       :type host: `str`
       :type port: `int`
       :type loop: :class:`AbstractEventLoop <asyncio.AbstractEventLoop>`
       :type family: `socket.AF_UNSPEC`, `socket.AF_INET`, or `socket.AF_INET6`
       :type flags: flags to pass to :meth:`getaddrinfo() <socket.getaddrinfo>`
       :type backlog: `int`
       :type reuse_address: `bool`
       :type server_host_keys: *see* :ref:`SpecifyingPrivateKeys`
       :type passphrase: `str`
       :type known_client_hosts: *see* :ref:`SpecifyingKnownHosts`
       :type trust_client_host: `bool`
       :type authorized_client_keys: *see* :ref:`SpecifyingAuthorizedKeys`
       :type x509_trusted_certs: *see* :ref:`SpecifyingCertificates`
       :type x509_trusted_cert_paths: `list` of `str`
       :type x509_purposes: *see* :ref:`SpecifyingX509Purposes`
       :type gss_host: `str`
       :type allow_pty: `bool`
       :type line_editor: `bool`
       :type line_history: `bool`
       :type x11_forwarding: `bool`
       :type x11_auth_path: `str`
       :type agent_forwarding: `bool`
       :type process_factory: `callable`
       :type session_factory: `callable`
       :type session_encoding: `str`
       :type sftp_factory: `callable`
       :type allow_scp: `bool`
       :type window: `int`
       :type max_pktsize: `int`
       :type server_version: `str`
       :type kex_algs: `list` of `str`
       :type encryption_algs: `list` of `str`
       :type mac_algs: `list` of `str`
       :type compression_algs: `list` of `str`
       :type signature_algs: `list` of `str`
       :type rekey_bytes: `int`
       :type rekey_seconds: `int`
       :type login_timeout: `int`

       :returns: :class:`asyncio.Server`

    """

    def conn_factory():
        """Return an SSH server connection handler"""

        return SSHServerConnection(server_factory, loop, server_version,
                                   x509_trusted_certs, x509_trusted_cert_paths,
                                   x509_purposes, kex_algs, encryption_algs,
                                   mac_algs, compression_algs, signature_algs,
                                   rekey_bytes, rekey_seconds,
                                   server_host_keys, known_client_hosts,
                                   trust_client_host, authorized_client_keys,
                                   gss_host, allow_pty, line_editor,
                                   line_history, x11_forwarding, x11_auth_path,
                                   agent_forwarding, process_factory,
                                   session_factory, session_encoding,
                                   sftp_factory, allow_scp, window,
                                   max_pktsize, login_timeout)

    if not server_factory:
        server_factory = SSHServer

    if sftp_factory is True:
        sftp_factory = SFTPServer

    if not loop:
        loop = asyncio.get_event_loop()

    server_version = _validate_version(server_version)

    if gss_host == ():
        gss_host = socket.gethostname()

        if '.' not in gss_host:
            gss_host = socket.getfqdn()

    kex_algs, encryption_algs, mac_algs, compression_algs, signature_algs = \
        _validate_algs(kex_algs, encryption_algs, mac_algs, compression_algs,
                       signature_algs, x509_trusted_certs is not None)

    server_keys = load_keypairs(server_host_keys, passphrase)

    if not server_keys and not gss_host:
        raise ValueError('No server host keys provided')

    server_host_keys = OrderedDict()

    for keypair in server_keys:
        for alg in keypair.host_key_algorithms:
            if alg in server_host_keys:
                raise ValueError('Multiple keys of type %s found' %
                                 alg.decode('ascii'))

            server_host_keys[alg] = keypair

    if isinstance(authorized_client_keys, str):
        authorized_client_keys = read_authorized_keys(authorized_client_keys)

    if x509_trusted_certs is not None:
        x509_trusted_certs = load_certificates(x509_trusted_certs)

    logger.info('Creating SSH server on %s', (host, port))

    return (yield from loop.create_server(conn_factory, host, port,
                                          family=family, flags=flags,
                                          backlog=backlog,
                                          reuse_address=reuse_address))


@async_context_manager
def connect(host, port=_DEFAULT_PORT, **kwargs):
    """Make an SSH client connection

       This function is a coroutine wrapper around :func:`create_connection`
       which can be used when a custom SSHClient instance is not needed.
       It takes all the same arguments as :func:`create_connection`
       except for `client_factory` and returns only the
       :class:`SSHClientConnection` object rather than a tuple of
       an :class:`SSHClientConnection` and :class:`SSHClient`.

       When using this call, the following restrictions apply:

           1. No callbacks are called when the connection is successfully
              opened, when it is closed, or when authentication completes.

           2. Any authentication information must be provided as arguments
              to this call, as any authentication callbacks will deny
              other authentication attempts. Also, authentication banner
              information will be ignored.

           3. Any debug messages sent by the server will be ignored.

    """

    conn, _ = yield from create_connection(None, host, port, **kwargs)

    return conn


@asyncio.coroutine
def listen(host=None, port=_DEFAULT_PORT, **kwargs):
    """Start an SSH server

       This function is a coroutine wrapper around :func:`create_server`
       which can be used when a custom SSHServer instance is not needed.
       It takes all the same arguments as :func:`create_server` except for
       `server_factory`.

       When using this call, the following restrictions apply:

           1. No callbacks are called when a new connection arrives,
              when a connection is closed, or when authentication
              completes.

           2. Any authentication information must be provided as arguments
              to this call, as any authentication callbacks will deny other
              authentication attempts. Currently, this allows only public
              key authentication to be used, by passing in the
              `authorized_client_keys` argument.

           3. Only handlers using the streams API are supported and the same
              handlers must be used for all clients. These handlers must
              be provided in the `process_factory`, `session_factory`,
              and `sftp_factory` arguments to this call.

           4. Any debug messages sent by the client will be ignored.

    """

    return (yield from create_server(None, host, port, **kwargs))
