#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for Result Set Management (XEP-0059)
# Copyright (C) 2009-2018 Jérôme Poisson (goffi@goffi.org)
# Copyright (C) 2013-2016 Adrien Cossa (souliane@mailoo.org)

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

from sat.core.i18n import _
from sat.core.constants import Const as C
from sat.core.log import getLogger

log = getLogger(__name__)

from wokkel import disco
from wokkel import iwokkel
from wokkel import rsm

from twisted.words.protocols.jabber import xmlstream
from zope.interface import implements


PLUGIN_INFO = {
    C.PI_NAME: "Result Set Management",
    C.PI_IMPORT_NAME: "XEP-0059",
    C.PI_TYPE: "XEP",
    C.PI_PROTOCOLS: ["XEP-0059"],
    C.PI_MAIN: "XEP_0059",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _("""Implementation of Result Set Management"""),
}


class XEP_0059(object):
    # XXX: RSM management is done directly in Wokkel.

    def __init__(self, host):
        log.info(_("Result Set Management plugin initialization"))

    def getHandler(self, client):
        return XEP_0059_handler()


class XEP_0059_handler(xmlstream.XMPPHandler):
    implements(iwokkel.IDisco)

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [disco.DiscoFeature(rsm.NS_RSM)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []
