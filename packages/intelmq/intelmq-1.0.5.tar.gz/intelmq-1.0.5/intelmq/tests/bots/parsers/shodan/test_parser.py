# -*- coding: utf-8 -*-
import base64
import os
import unittest

import intelmq.lib.test as test
from intelmq.bots.parsers.shodan.parser import ShodanParserBot

with open(os.path.join(os.path.dirname(__file__), 'tests.json'), 'rb') as fh:
    RAWS = [base64.b64encode(x).decode() for x in fh.read().splitlines()]

REPORTS = [{"feed.name": "Test feed",
                    "raw": raw,
                    "__type": "Report",
                    } for raw in RAWS]
EVENTS = [{'__type': 'Event',
           'classification.identifier': 'shodan-scan',
           'classification.type': 'other',
           'event_description.target': 'Telekom Austria',
           'extra.data': '220-FileZilla Server version 0.9.41 beta\n'
                         '220-written by Tim Kosse (Tim.Kosse@gmx.de)\n'
                         '220 Please visit http://sourceforge.net/projects/filezilla/\r\n'
                         '530 Login or password incorrect!\r\n'
                         '214-The following commands are recognized:\n'
                         '   USER   PASS   QUIT   CWD    PWD    PORT   PASV   TYPE\n'
                         '   LIST   REST   CDUP   RETR   STOR   SIZE   DELE   RMD \n'
                         '   MKD    RNFR   RNTO   ABOR   SYST   NOOP   APPE   NLST\n'
                         '   MDTM   XPWD   XCUP   XMKD   XRMD   NOP    EPSV   EPRT\n'
                         '   AUTH   ADAT   PBSZ   PROT   FEAT   MODE   OPTS   HELP\n'
                         '   ALLO   MLST   MLSD   SITE   P@SW   STRU   CLNT   MFMT\n'
                         '   HASH\n'
                         '214 Have a nice day.\r\n'
                         '211-Features:\n'
                         ' MDTM\n'
                         ' REST STREAM\n'
                         ' SIZE\n'
                         ' MLST type*;size*;modify*;\n'
                         ' MLSD\n'
                         ' UTF8\n'
                         ' CLNT\n'
                         ' MFMT\n'
                         '211 End',
           'extra.event_hash_shodan': 2125142980,
           'extra.ftp.features.mlst': ['type', 'size', 'modify'],
           'extra.ftp.rest.parameters': ['STREAM'],
           'extra.geolocation.longitude': 16.36670000000001,
           'extra.isp': 'Telekom Austria',
           'feed.name': 'Test feed',
           'protocol.transport': 'tcp',
           'raw': RAWS[0],
           'source.asn': 8447,
           'source.fqdn': "['golfschaukel.at']",
           'source.geolocation.cc': 'AT',
           'source.geolocation.latitude': 48.19999999999999,
           'source.ip': '93.83.254.28',
           'source.port': 21,
           'source.reverse_dns': "['mail.golfschaukel.at']",
           'time.source': '2018-06-19T11:02:37.371273+00:00',
           },
                    {"feed.name": "Test feed",
                     "raw": 'eyJfX3R5cGUiOiAiRXZlbnQiLCAic291cmNlLmlwIjogIjEyNy4wLjAuMiIsICJjbGFzc2lmaWNhdGlvbi50eXBlIjogImMmYyJ9',
                     "__type": "Event",
                     "classification.type": "c&c",
                     "source.ip": "127.0.0.2"
                     },
                    ]


class TestShodanParserBot(test.BotTestCase, unittest.TestCase):
    """
    A TestCase for a ShodanParserBot.
    """

    @classmethod
    def set_bot(cls):
        cls.bot_reference = ShodanParserBot
        cls.default_input_message = REPORTS[0]

    def test_ftp(self):
        self.run_bot()
        self.assertMessageEqual(0, EVENTS[0])

    def test_http(self):
        self.input_message = REPORTS[1]
        self.run_bot()
        self.assertMessageEqual(0, EVENTS[1])

    def test_ike(self):
        self.input_message = REPORTS[2]
        self.run_bot()
        self.assertMessageEqual(0, EVENTS[2])


if __name__ == '__main__':  # pragma: no cover
    unittest.main()
