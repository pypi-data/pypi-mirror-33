#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# jp: a SAT command line tool
# Copyright (C) 2009-2018 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from sat_frontends.jp import base
import sys
from sat.core.i18n import _
from sat.core.constants import Const as C
from sat.tools.utils import clean_ustr

__commands__ = ["Message"]


class Send(base.CommandBase):
    def __init__(self, host):
        super(Send, self).__init__(host, "send", help=_("send a message to a contact"))

    def add_parser_options(self):
        self.parser.add_argument(
            "-l", "--lang", type=str, default="", help=_(u"language of the message")
        )
        self.parser.add_argument(
            "-s",
            "--separate",
            action="store_true",
            help=_(
                u"separate xmpp messages: send one message per line instead of one message alone."
            ),
        )
        self.parser.add_argument(
            "-n",
            "--new-line",
            action="store_true",
            help=_(
                u"add a new line at the beginning of the input (usefull for ascii art ;))"
            ),
        )
        self.parser.add_argument(
            "-S",
            "--subject",
            type=base.unicode_decoder,
            help=_(u"subject of the message"),
        )
        self.parser.add_argument(
            "-L", "--subject_lang", type=str, default="", help=_(u"language of subject")
        )
        self.parser.add_argument(
            "-t",
            "--type",
            choices=C.MESS_TYPE_STANDARD + (C.MESS_TYPE_AUTO,),
            default=C.MESS_TYPE_AUTO,
            help=_("type of the message"),
        )
        syntax = self.parser.add_mutually_exclusive_group()
        syntax.add_argument("-x", "--xhtml", action="store_true", help=_(u"XHTML body"))
        syntax.add_argument("-r", "--rich", action="store_true", help=_(u"rich body"))
        self.parser.add_argument(
            "jid", type=base.unicode_decoder, help=_(u"the destination jid")
        )

    def start(self):
        if self.args.xhtml and self.args.separate:
            self.disp(
                u"argument -s/--separate is not compatible yet with argument -x/--xhtml",
                error=True,
            )
            self.host.quit(2)

        jids = self.host.check_jids([self.args.jid])
        jid = jids[0]
        self.sendStdin(jid)

    def sendStdin(self, dest_jid):
        """Send incomming data on stdin to jabber contact

        @param dest_jid: destination jid
        """
        header = "\n" if self.args.new_line else ""
        stdin_lines = [
            stream.decode("utf-8", "ignore") for stream in sys.stdin.readlines()
        ]
        extra = {}
        if self.args.subject is None:
            subject = {}
        else:
            subject = {self.args.subject_lang: self.args.subject}

        if self.args.xhtml or self.args.rich:
            key = u"xhtml" if self.args.xhtml else u"rich"
            if self.args.lang:
                key = u"{}_{}".format(key, self.args.lang)
            extra[key] = clean_ustr(u"".join(stdin_lines))
            stdin_lines = []

        if self.args.separate:  # we send stdin in several messages
            if header:
                self.host.bridge.messageSend(
                    dest_jid,
                    {self.args.lang: header},
                    subject,
                    self.args.type,
                    profile_key=self.profile,
                    callback=lambda: None,
                    errback=lambda ignore: ignore,
                )

            for line in stdin_lines:
                self.host.bridge.messageSend(
                    dest_jid,
                    {self.args.lang: line.replace("\n", "")},
                    subject,
                    self.args.type,
                    extra,
                    profile_key=self.host.profile,
                    callback=lambda: None,
                    errback=lambda ignore: ignore,
                )

        else:
            msg = (
                {self.args.lang: header + clean_ustr(u"".join(stdin_lines))}
                if not (self.args.xhtml or self.args.rich)
                else {}
            )
            self.host.bridge.messageSend(
                dest_jid,
                msg,
                subject,
                self.args.type,
                extra,
                profile_key=self.host.profile,
                callback=lambda: None,
                errback=lambda ignore: ignore,
            )


class Message(base.CommandBase):
    subcommands = (Send,)

    def __init__(self, host):
        super(Message, self).__init__(
            host, "message", use_profile=False, help=_("messages handling")
        )
