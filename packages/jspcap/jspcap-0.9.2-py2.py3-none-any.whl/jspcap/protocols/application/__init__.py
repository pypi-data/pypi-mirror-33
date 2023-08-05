# -*- coding: utf-8 -*-
"""application layer protocols

`jspcap.protocols.application` is collection of all
protocols in application layer, with detailed
implementation and methods.

"""
# TODO: Implements BGP, DHCP, DNS, FTP, IMAP, IDAP, MQTT, NNTP, NTP, ONC:RPC, POP, RIP, RTP, SIP, SMTP, SNMP, SSH, SSL, TELNET, TLS, XMPP.

# Base Class for Internet Layer
from jspcap.protocols.application.application import Application

# Utility Classes for Protocols
from jspcap.protocols.application.httpv1 import HTTPv1
from jspcap.protocols.application.httpv2 import HTTPv2

# Deprecated / Base Classes
from jspcap.protocols.application.http import HTTP


__all__ = ['HTTPv1', 'HTTPv2']
