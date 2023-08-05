# -*- coding: utf-8 -*-
"""frame header

`jspcap.protocols.pcap.frame` contains `Frame` only,
which implements extractor for frame headers of PCAP,
whose structure is described as below.

typedef struct pcaprec_hdr_s {
    guint32 ts_sec;     /* timestamp seconds */
    guint32 ts_usec;    /* timestamp microseconds */
    guint32 incl_len;   /* number of octets of packet saved in file */
    guint32 orig_len;   /* actual length of packet */
} pcaprec_hdr_t;

"""
import datetime
import io
import os

from jspcap.corekit.infoclass import Info
from jspcap.corekit.protochain import ProtoChain
from jspcap.protocols.protocol import Protocol
from jspcap.utilities.decorators import beholder
from jspcap.utilities.exceptions import ProtocolNotFound, ProtocolUnbound

###############################################################################
# from jspcap.protocols.link import Ethernet
# from jspcap.protocols.internet import IPv4
# from jspcap.protocols.internet import IPv6
# from jspcap.protocols.raw import Raw
###############################################################################


__all__ = ['Frame']


class Frame(Protocol):
    """Per packet frame header extractor.

    Properties:
        * name -- str, name of corresponding protocol
        * info -- Info, info dict of current instance
        * alias -- str, acronym of corresponding protocol
        * length -- int, header length of corresponding protocol
        * protocol -- str, name of next layer protocol
        * protochain -- ProtoChain, protocol chain of current frame

    Methods:
        * index -- call `ProtoChain.index`
        * read_frame -- read each block after global header

    Attributes:
        * _file -- BytesIO, bytes to be extracted
        * _info -- Info, info dict of current instance
        * _protos -- ProtoChain, protocol chain of current instance

    Utilities:
        * _read_protos -- read next layer protocol type
        * _read_fileng -- read file buffer
        * _read_unpack -- read bytes and unpack to integers
        * _read_binary -- read bytes and convert into binaries
        * _read_packet -- read raw packet data
        * _decode_next_layer -- decode next layer protocol type
        * _import_next_layer -- import next layer protocol extractor

    """
    ##########################################################################
    # Properties.
    ##########################################################################

    @property
    def name(self):
        """Name of corresponding protocol."""
        return f'Frame {self._fnum}'

    @property
    def length(self):
        """Header length of corresponding protocol."""
        return 16

    ##########################################################################
    # Methods.
    ##########################################################################

    def index(self, name):
        return self._proto.index(name)

    def read_frame(self):
        """Read each block after global header.

        Structure of record/package header (C):
            typedef struct pcaprec_hdr_s {
                guint32 ts_sec;     /* timestamp seconds */
                guint32 ts_usec;    /* timestamp microseconds */
                guint32 incl_len;   /* number of octets of packet saved in file */
                guint32 orig_len;   /* actual length of packet */
            } pcaprec_hdr_t;

        """
        # _scur = self._file.tell()
        _temp = self._read_unpack(4, lilendian=True, quiet=True)
        if _temp is None:
            raise EOFError

        _tsss = _temp
        _tsus = self._read_unpack(4, lilendian=True)
        _ilen = self._read_unpack(4, lilendian=True)
        _olen = self._read_unpack(4, lilendian=True)

        _epch = float(f'{_tsss}.{_tsus}')
        _time = datetime.datetime.fromtimestamp(_epch)

        frame = dict(
            frame_info = dict(
                ts_sec = _tsss,
                ts_usec = _tsus,
                incl_len = _ilen,
                orig_len = _olen,
            ),
            time = _time,
            number = self._fnum,
            time_epoch = _epch,
            len = _ilen,
            cap_len = _olen,
        )

        # make BytesIO from frame package data
        length = frame['len']
        self._file = io.BytesIO(self._file.read(length))
        frame['packet'] = self._read_packet(header=0, payload=length, discard=True)

        return self._decode_next_layer(frame, length)

    ##########################################################################
    # Data models.
    ##########################################################################

    def __init__(self, file, *, num, proto):
        self._fnum = num
        self._file = file
        self._prot = proto
        self._info = Info(self.read_frame())

    def __length_hint__(self):
        return 16

    def __getitem__(self, key):
        if isinstance(key, type) and issubclass(key, Protocol):
            key = key.__index__()

        # if requests attributes in info dict
        if key in self._info:
            return self._info[key]

        def _getitem_from_ProtoChain(key):
            proto = self._protos[key]
            if not proto:
                raise ProtocolNotFound('ProtoChain index out of range')
            elif isinstance(proto, tuple):
                if len(proto) > 1:  # if it's a slice with step & stop
                    raise ProtocolUnbound('frame slice unbound')
                else:
                    start = proto[0]
            else:
                start = self._protos.index(proto)
            return start

        # fetch slice start point from ProtoChain
        if not isinstance(key, tuple):
            key = (key,)
        start = None
        for item in key:
            try:
                start = _getitem_from_ProtoChain(item)
            except ProtocolNotFound:
                continue
            else:
                break
        if start is None:
            raise IndexNotFound(f"'{key}' not in Frame")

        # make return Info item
        dict_ = self._info.infotodict()
        for (level, proto) in enumerate(self._protos):
            proto = proto or 'raw'
            dict_ = dict_[proto.lower()]
            if level >= start:
                return Info(dict_)
        return Info(dict_)

    def __index__(self):
        return self._fnum

    def __contains__(self, name):
        if isinstance(name, type) and issubclass(name, Protocol):
            name = name.__index__()
        if isinstance(name, tuple):
            for item in name:
                flag = (item in self._protos)
                if flag:    break
            return flag
        return ((name in self._info) or (name in self._protos))

    ##########################################################################
    # Utilities.
    ##########################################################################

    def _decode_next_layer(self, dict_, length=None):
        """Decode next layer protocol.

        Positional arguments:
            dict_ -- dict, info buffer
            proto -- str, next layer protocol name
            length -- int, valid (not padding) length

        Returns:
            * dict -- current protocol with packet extracted

        """
        seek_cur = self._file.tell()
        try:
            flag, info, chain, alias = self._import_next_layer(self._prot, length)
        except Exception as error:
            dict_['error'] = str(error)
            self._file.seek(seek_cur, os.SEEK_SET)
            flag, info, chain, alias = beholder(self._import_next_layer)(self, self._prot, length, error=True)

        # make next layer protocol name
        if flag:
            proto, name = str(self._prot or 'Raw').lower(), self._prot
        else:
            proto, name = 'raw', 'Raw'

        # write info and protocol chain into dict
        self._protos = ProtoChain(name, chain, alias)
        dict_[proto] = info
        dict_['protocols'] = self._protos.chain
        return dict_

    def _import_next_layer(self, proto, length, error=False):
        """Import next layer extractor.

        Positional arguments:
            * proto -- str, next layer protocol name
            * length -- int, valid (not padding) length

        Keyword arguments:
            * error -- bool, if function call on error

        Returns:
            * bool -- flag if extraction of next layer succeeded
            * Info -- info of next layer
            * ProtoChain -- protocol chain of next layer
            * str -- alias of next layer

        Protocols:
            * Ethernet (data link layer)
            * IPv4 (internet layer)
            * IPv6 (internet layer)

        """
        if proto == 'Ethernet':
            from jspcap.protocols.link import Ethernet as Protocol
        elif proto == 'IPv4':
            from jspcap.protocols.internet import IPv4 as Protocol
        elif proto == 'IPv6':
            from jspcap.protocols.internet import IPv6 as Protocol
        else:
            from jspcap.protocols.raw import Raw as Protocol
        next_ = Protocol(self._file, length, error=error)
        return True, next_.info, next_.protochain, next_.alias
