#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SàT plugin for managing raw XML log
# Copyright (C) 2011  Jérôme Poisson (goffi@goffi.org)

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
from twisted.words.xish import domish
from twisted.words.xish import xmlstream

PLUGIN_INFO = {
    C.PI_NAME: "Raw XML log Plugin",
    C.PI_IMPORT_NAME: "XmlLog",
    C.PI_TYPE: "Misc",
    C.PI_PROTOCOLS: [],
    C.PI_DEPENDENCIES: [],
    C.PI_MAIN: "XmlLog",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: _(u"""Send raw XML logs to bridge"""),
}

host = None


def send(self, obj):
    global host
    if isinstance(obj, basestring):
        log = unicode(obj)
    elif isinstance(obj, domish.Element):
        log = obj.toXml()
    else:
        log.error(_(u"INTERNAL ERROR: Unmanaged XML type"))
    host.bridge.xmlLog("OUT", log, self._profile)
    return self._original_send(obj)


def onElement(self, element):
    global host
    host.bridge.xmlLog("IN", element.toXml(), self._profile)
    return self._original_onElement(element)


class XmlLog(object):

    params = """
    <params>
    <general>
    <category name="Debug">
        <param name="Xml log" label="%(label_xmllog)s" value="false" type="bool" />
    </category>
    </general>
    </params>
    """ % {
        "label_xmllog": _("Activate XML log")
    }

    def __init__(self, host_):
        log.info(_("Plugin XML Log initialization"))
        global host
        host = host_

        # parameters
        host.memory.updateParams(self.params)

        # bridge
        host.bridge.addSignal(
            "xmlLog", ".plugin", signature="sss"
        )  # args: direction("IN" or "OUT"), xml_data, profile

        self.do_log = host.memory.getParamA("Xml log", "Debug")
        if self.do_log:
            XmlStream = xmlstream.XmlStream
            XmlStream._original_send = XmlStream.send
            XmlStream._original_onElement = XmlStream.onElement
            XmlStream.send = send
            XmlStream.onElement = onElement
            XmlStream._profile = ""
            host.trigger.add("XML Initialized", self.setProfile)
            log.info(_(u"XML log activated"))

    def setProfile(self, xmlstream, profile):
        xmlstream._profile = profile
        return True
