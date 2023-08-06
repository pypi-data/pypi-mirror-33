#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for Message Archive Management (XEP-0313)
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

from sat.core.constants import Const as C
from sat.core.i18n import _
from sat.core.log import getLogger

log = getLogger(__name__)
from sat.core import exceptions

from twisted.words.protocols.jabber import jid

from zope.interface import implements

from wokkel import disco
import uuid

# XXX: mam and rsm come from sat_tmp.wokkel
from wokkel import rsm
from wokkel import mam


MESSAGE_RESULT = "/message/result[@xmlns='{mam_ns}' and @queryid='{query_id}']"

PLUGIN_INFO = {
    C.PI_NAME: "Message Archive Management",
    C.PI_IMPORT_NAME: "XEP-0313",
    C.PI_TYPE: "XEP",
    C.PI_PROTOCOLS: ["XEP-0313"],
    C.PI_MAIN: "XEP_0313",
    C.PI_HANDLER: "yes",
    C.PI_DESCRIPTION: _("""Implementation of Message Archive Management"""),
}


class XEP_0313(object):
    def __init__(self, host):
        log.info(_("Message Archive Management plugin initialization"))
        self.host = host

    def getHandler(self, client):
        mam_client = client._mam = SatMAMClient()
        return mam_client

    def queryFields(self, client, service=None):
        """Ask the server about supported fields.

        @param service: entity offering the MAM service (None for user archives)
        @return (D(data_form.Form)): form with the implemented fields (cf XEP-0313 §4.1.5)
        """
        return client._mam.queryFields(service)

    def queryArchive(self, client, mam_query, service=None):
        """Query a user, MUC or pubsub archive.

        @param mam_query(mam.MAMRequest): MAM query instance
        @param service(jid.JID, None): entity offering the MAM service
            None for user server
        @return (D(domish.Element)): <IQ/> result
        """
        return client._mam.queryArchive(mam_query, service)

    def _appendMessage(self, elt_list, message_cb, message_elt):
        if message_cb is not None:
            elt_list.append(message_cb(message_elt))
        else:
            elt_list.append(message_elt)

    def _queryFinished(self, iq_result, client, elt_list, event):
        client.xmlstream.removeObserver(event, self._appendMessage)
        try:
            fin_elt = iq_result.elements(mam.NS_MAM, "fin").next()
        except StopIteration:
            raise exceptions.DataError(u"Invalid MAM result")

        try:
            rsm_response = rsm.RSMResponse.fromElement(fin_elt)
        except rsm.RSMNotFoundError:
            rsm_response = None

        return (elt_list, rsm_response)

    def getArchives(self, client, query, service=None, message_cb=None):
        """Query archive then grab and return them all in the result

        """
        if query.query_id is None:
            query.query_id = unicode(uuid.uuid4())
        elt_list = []
        event = MESSAGE_RESULT.format(mam_ns=mam.NS_MAM, query_id=query.query_id)
        client.xmlstream.addObserver(event, self._appendMessage, 0, elt_list, message_cb)
        d = self.queryArchive(client, query, service)
        d.addCallback(self._queryFinished, client, elt_list, event)
        return d

    def getPrefs(self, client, service=None):
        """Retrieve the current user preferences.

        @param service: entity offering the MAM service (None for user archives)
        @return: the server response as a Deferred domish.Element
        """
        # http://xmpp.org/extensions/xep-0313.html#prefs
        return client._mam.queryPrefs(service)

    def _setPrefs(
        self,
        service_s=None,
        default="roster",
        always=None,
        never=None,
        profile_key=C.PROF_KEY_NONE,
    ):
        service = jid.JID(service_s) if service_s else None
        always_jid = [jid.JID(entity) for entity in always]
        never_jid = [jid.JID(entity) for entity in never]
        # TODO: why not build here a MAMPrefs object instead of passing the args separately?
        return self.setPrefs(service, default, always_jid, never_jid, profile_key)

    def setPrefs(self, client, service=None, default="roster", always=None, never=None):
        """Set news user preferences.

        @param service: entity offering the MAM service (None for user archives)
        @param default (unicode): a value in ('always', 'never', 'roster')
        @param always (list): a list of JID instances
        @param never (list): a list of JID instances
        @param profile_key (unicode): %(doc_profile_key)s
        @return: the server response as a Deferred domish.Element
        """
        # http://xmpp.org/extensions/xep-0313.html#prefs
        return client._mam.setPrefs(service, default, always, never)


class SatMAMClient(mam.MAMClient):
    implements(disco.IDisco)

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return [disco.DiscoFeature(mam.NS_MAM)]

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []
