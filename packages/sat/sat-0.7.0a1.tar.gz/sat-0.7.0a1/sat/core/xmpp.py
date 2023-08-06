#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT: a jabber client
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

from sat.core.i18n import _
from sat.core.constants import Const as C
from sat.memory import cache
from twisted.internet import task, defer
from twisted.words.protocols.jabber.xmlstream import XMPPHandler
from twisted.words.protocols.jabber import xmlstream
from twisted.words.protocols.jabber import error
from twisted.words.protocols.jabber import jid
from twisted.words.xish import domish
from twisted.python import failure
from wokkel import client as wokkel_client, disco, xmppim, generic, iwokkel
from wokkel import component
from wokkel import delay
from sat.core.log import getLogger

log = getLogger(__name__)
from sat.core import exceptions
from zope.interface import implements
import time
import calendar
import uuid
import sys


class SatXMPPEntity(object):
    """Common code for Client and Component"""

    def __init__(self, host_app, profile, max_retries):

        self.factory.clientConnectionLost = self.connectionLost
        self.factory.maxRetries = max_retries
        # when self._connected is None, we are not connected
        # else, it's a deferred which fire on disconnection
        self._connected = None
        self.profile = profile
        self.host_app = host_app
        self.cache = cache.Cache(host_app, profile)
        self._mess_id_uid = {}  # map from message id to uid used in history. Key: (full_jid,message_id) Value: uid
        self.conn_deferred = defer.Deferred()
        self._progress_cb = {}  # callback called when a progress is requested (key = progress id)
        self.actions = {}  # used to keep track of actions for retrieval (key = action_id)

    ## initialisation ##

    @defer.inlineCallbacks
    def _callConnectionTriggers(self):
        """Call conneting trigger prepare connected trigger

        @param plugins(iterable): plugins to use
        @return (list[object, callable]): plugin to trigger tuples with:
            - plugin instance
            - profileConnected* triggers (to call after connection)
        """
        plugin_conn_cb = []
        for plugin in self._getPluginsList():
            # we check if plugin handle client mode
            if plugin.is_handler:
                plugin.getHandler(self).setHandlerParent(self)

            # profileConnecting/profileConnected methods handling

            # profile connecting is called right now (before actually starting client)
            connecting_cb = getattr(plugin, "profileConnecting", None)
            if connecting_cb is not None:
                yield connecting_cb(self)

            # profile connected is called after client is ready and roster is got
            connected_cb = getattr(plugin, "profileConnected", None)
            if connected_cb is not None:
                plugin_conn_cb.append((plugin, connected_cb))

        defer.returnValue(plugin_conn_cb)

    def _getPluginsList(self):
        """Return list of plugin to use

        need to be implemented by subclasses
        this list is used to call profileConnect* triggers
        @return(iterable[object]): plugins to use
        """
        raise NotImplementedError

    def _createSubProtocols(self):
        return

    def entityConnected(self):
        """Called once connection is done

        may return a Deferred, to perform initialisation tasks
        """
        return

    @classmethod
    @defer.inlineCallbacks
    def startConnection(cls, host, profile, max_retries):
        """instantiate the entity and start the connection"""
        # FIXME: reconnection doesn't seems to be handled correclty (client is deleted then recreated from scrash
        #        most of methods called here should be called once on first connection (e.g. adding subprotocols)
        #        but client should not be deleted except if session is finished (independently of connection/deconnection
        #
        try:
            port = int(
                host.memory.getParamA(
                    C.FORCE_PORT_PARAM, "Connection", profile_key=profile
                )
            )
        except ValueError:
            log.debug(_("Can't parse port value, using default value"))
            port = (
                None
            )  # will use default value 5222 or be retrieved from a DNS SRV record

        password = yield host.memory.asyncGetParamA(
            "Password", "Connection", profile_key=profile
        )
        entity = host.profiles[profile] = cls(
            host,
            profile,
            jid.JID(host.memory.getParamA("JabberID", "Connection", profile_key=profile)),
            password,
            host.memory.getParamA(C.FORCE_SERVER_PARAM, "Connection", profile_key=profile)
            or None,
            port,
            max_retries,
        )

        entity._createSubProtocols()

        entity.fallBack = SatFallbackHandler(host)
        entity.fallBack.setHandlerParent(entity)

        entity.versionHandler = SatVersionHandler(C.APP_NAME_FULL, host.full_version)
        entity.versionHandler.setHandlerParent(entity)

        entity.identityHandler = SatIdentityHandler()
        entity.identityHandler.setHandlerParent(entity)

        log.debug(_("setting plugins parents"))

        plugin_conn_cb = yield entity._callConnectionTriggers()

        entity.startService()

        yield entity.getConnectionDeferred()

        yield defer.maybeDeferred(entity.entityConnected)

        # Call profileConnected callback for all plugins, and print error message if any of them fails
        conn_cb_list = []
        for dummy, callback in plugin_conn_cb:
            conn_cb_list.append(defer.maybeDeferred(callback, entity))
        list_d = defer.DeferredList(conn_cb_list)

        def logPluginResults(results):
            all_succeed = all([success for success, result in results])
            if not all_succeed:
                log.error(_(u"Plugins initialisation error"))
                for idx, (success, result) in enumerate(results):
                    if not success:
                        log.error(
                            u"error (plugin %(name)s): %(failure)s"
                            % {
                                "name": plugin_conn_cb[idx][0]._info["import_name"],
                                "failure": result,
                            }
                        )

        yield list_d.addCallback(
            logPluginResults
        )  # FIXME: we should have a timeout here, and a way to know if a plugin freeze
        # TODO: mesure launch time of each plugin

    def getConnectionDeferred(self):
        """Return a deferred which fire when the client is connected"""
        return self.conn_deferred

    def _disconnectionCb(self, dummy):
        self._connected = None

    def _disconnectionEb(self, failure_):
        log.error(_(u"Error while disconnecting: {}".format(failure_)))

    def _authd(self, xmlstream):
        if not self.host_app.trigger.point("XML Initialized", xmlstream, self.profile):
            return
        super(SatXMPPEntity, self)._authd(xmlstream)

        # the following Deferred is used to know when we are connected
        # so we need to be set it to None when connection is lost
        self._connected = defer.Deferred()
        self._connected.addCallback(self._cleanConnection)
        self._connected.addCallback(self._disconnectionCb)
        self._connected.addErrback(self._disconnectionEb)

        log.info(
            _(u"********** [{profile}] CONNECTED **********").format(profile=self.profile)
        )
        self.streamInitialized()
        self.host_app.bridge.connected(
            self.profile, unicode(self.jid)
        )  # we send the signal to the clients

    def _finish_connection(self, dummy):
        self.conn_deferred.callback(None)

    def streamInitialized(self):
        """Called after _authd"""
        log.debug(_(u"XML stream is initialized"))
        self.keep_alife = task.LoopingCall(
            self.xmlstream.send, " "
        )  # Needed to avoid disconnection (specially with openfire)
        self.keep_alife.start(C.XMPP_KEEP_ALIFE)

        self.disco = SatDiscoProtocol(self)
        self.disco.setHandlerParent(self)
        self.discoHandler = disco.DiscoHandler()
        self.discoHandler.setHandlerParent(self)
        disco_d = defer.succeed(None)

        if not self.host_app.trigger.point("Disco handled", disco_d, self.profile):
            return

        disco_d.addCallback(self._finish_connection)

    def initializationFailed(self, reason):
        log.error(
            _(
                u"ERROR: XMPP connection failed for profile '%(profile)s': %(reason)s"
                % {"profile": self.profile, "reason": reason}
            )
        )
        self.conn_deferred.errback(reason.value)
        try:
            super(SatXMPPEntity, self).initializationFailed(reason)
        except:
            # we already chained an errback, no need to raise an exception
            pass

    ## connection ##

    def connectionLost(self, connector, reason):
        try:
            self.keep_alife.stop()
        except AttributeError:
            log.debug(_("No keep_alife"))
        if self._connected is not None:
            self.host_app.bridge.disconnected(
                self.profile
            )  # we send the signal to the clients
            self._connected.callback(None)
            self.host_app.purgeEntity(
                self.profile
            )  # and we remove references to this client
            log.info(
                _(u"********** [{profile}] DISCONNECTED **********").format(
                    profile=self.profile
                )
            )
        if not self.conn_deferred.called:
            # FIXME: real error is not gotten here (e.g. if jid is not know by Prosody,
            #        we should have the real error)
            self.conn_deferred.errback(
                error.StreamError(u"Server unexpectedly closed the connection")
            )

    @defer.inlineCallbacks
    def _cleanConnection(self, dummy):
        """method called on disconnection

        used to call profileDisconnected* triggers
        """
        trigger_name = "profileDisconnected"
        for plugin in self._getPluginsList():
            disconnected_cb = getattr(plugin, trigger_name, None)
            if disconnected_cb is not None:
                yield disconnected_cb(self)

    def isConnected(self):
        return self._connected is not None

    def entityDisconnect(self):
        log.info(_(u"Disconnecting..."))
        self.stopService()
        if self._connected is not None:
            return self._connected
        else:
            return defer.succeed(None)

    ## sending ##

    def IQ(self, type_=u"set", timeout=60):
        """shortcut to create an IQ element managing deferred

        @param type_(unicode): IQ type ('set' or 'get')
        @param timeout(None, int): timeout in seconds
        @return((D)domish.Element: result stanza
            errback is called if and error stanza is returned
        """
        iq_elt = xmlstream.IQ(self.xmlstream, type_)
        iq_elt.timeout = timeout
        return iq_elt

    def sendError(self, iq_elt, condition):
        """Send error stanza build from iq_elt

        @param iq_elt(domish.Element): initial IQ element
        @param condition(unicode): error condition
        """
        iq_error_elt = error.StanzaError(condition).toResponse(iq_elt)
        self.xmlstream.send(iq_error_elt)

    def generateMessageXML(self, data):
        """Generate <message/> stanza from message data

        @param data(dict): message data
            domish element will be put in data['xml']
            following keys are needed:
                - from
                - to
                - uid: can be set to '' if uid attribute is not wanted
                - message
                - type
                - subject
                - extra
        @return (dict) message data
        """
        data["xml"] = message_elt = domish.Element((None, "message"))
        message_elt["to"] = data["to"].full()
        message_elt["from"] = data["from"].full()
        message_elt["type"] = data["type"]
        if data["uid"]:  # key must be present but can be set to ''
            # by a plugin to avoid id on purpose
            message_elt["id"] = data["uid"]
        for lang, subject in data["subject"].iteritems():
            subject_elt = message_elt.addElement("subject", content=subject)
            if lang:
                subject_elt[(C.NS_XML, "lang")] = lang
        for lang, message in data["message"].iteritems():
            body_elt = message_elt.addElement("body", content=message)
            if lang:
                body_elt[(C.NS_XML, "lang")] = lang
        try:
            thread = data["extra"]["thread"]
        except KeyError:
            if "thread_parent" in data["extra"]:
                raise exceptions.InternalError(
                    u"thread_parent found while there is not associated thread"
                )
        else:
            thread_elt = message_elt.addElement("thread", content=thread)
            try:
                thread_elt["parent"] = data["extra"]["thread_parent"]
            except KeyError:
                pass
        return data

    def addPostXmlCallbacks(self, post_xml_treatments):
        """Used to add class level callbacks at the end of the workflow

        @param post_xml_treatments(D): the same Deferred as in sendMessage trigger
        """
        raise NotImplementedError

    def sendMessage(
        self,
        to_jid,
        message,
        subject=None,
        mess_type="auto",
        extra=None,
        uid=None,
        no_trigger=False,
    ):
        """Send a message to an entity

        @param to_jid(jid.JID): destinee of the message
        @param message(dict): message body, key is the language (use '' when unknown)
        @param subject(dict): message subject, key is the language (use '' when unknown)
        @param mess_type(str): one of standard message type (cf RFC 6121 §5.2.2) or:
            - auto: for automatic type detection
            - info: for information ("info_type" can be specified in extra)
        @param extra(dict, None): extra data. Key can be:
            - info_type: information type, can be
                TODO
        @param uid(unicode, None): unique id:
            should be unique at least in this XMPP session
            if None, an uuid will be generated
        @param no_trigger (bool): if True, sendMessage[suffix] trigger will no be used
            useful when a message need to be sent without any modification
        """
        if subject is None:
            subject = {}
        if extra is None:
            extra = {}

        assert mess_type in C.MESS_TYPE_ALL

        data = {  # dict is similar to the one used in client.onMessage
            "from": self.jid,
            "to": to_jid,
            "uid": uid or unicode(uuid.uuid4()),
            "message": message,
            "subject": subject,
            "type": mess_type,
            "extra": extra,
            "timestamp": time.time(),
        }
        pre_xml_treatments = (
            defer.Deferred()
        )  # XXX: plugin can add their pre XML treatments to this deferred
        post_xml_treatments = (
            defer.Deferred()
        )  # XXX: plugin can add their post XML treatments to this deferred

        if data["type"] == C.MESS_TYPE_AUTO:
            # we try to guess the type
            if data["subject"]:
                data["type"] = C.MESS_TYPE_NORMAL
            elif not data[
                "to"
            ].resource:  # if to JID has a resource, the type is not 'groupchat'
                # we may have a groupchat message, we check if the we know this jid
                try:
                    entity_type = self.host_app.memory.getEntityData(
                        data["to"], ["type"], self.profile
                    )["type"]
                    # FIXME: should entity_type manage resources ?
                except (exceptions.UnknownEntityError, KeyError):
                    entity_type = "contact"

                if entity_type == "chatroom":
                    data["type"] = C.MESS_TYPE_GROUPCHAT
                else:
                    data["type"] = C.MESS_TYPE_CHAT
            else:
                data["type"] == C.MESS_TYPE_CHAT
            data["type"] == C.MESS_TYPE_CHAT if data["subject"] else C.MESS_TYPE_NORMAL

        # FIXME: send_only is used by libervia's OTR plugin to avoid
        #        the triggers from frontend, and no_trigger do the same
        #        thing internally, this could be unified
        send_only = data["extra"].get("send_only", False)

        if not no_trigger and not send_only:
            if not self.host_app.trigger.point(
                "sendMessage" + self.trigger_suffix,
                self,
                data,
                pre_xml_treatments,
                post_xml_treatments,
            ):
                return defer.succeed(None)

        log.debug(
            _(u"Sending message (type {type}, to {to})").format(
                type=data["type"], to=to_jid.full()
            )
        )

        pre_xml_treatments.addCallback(lambda dummy: self.generateMessageXML(data))
        pre_xml_treatments.chainDeferred(post_xml_treatments)
        post_xml_treatments.addCallback(self.sendMessageData)
        if send_only:
            log.debug(
                _(
                    "Triggers, storage and echo have been inhibited by the 'send_only' parameter"
                )
            )
        else:
            self.addPostXmlCallbacks(post_xml_treatments)
            post_xml_treatments.addErrback(self._cancelErrorTrap)
            post_xml_treatments.addErrback(self.host_app.logErrback)
        pre_xml_treatments.callback(data)
        return pre_xml_treatments

    def _cancelErrorTrap(self, failure):
        """A message sending can be cancelled by a plugin treatment"""
        failure.trap(exceptions.CancelError)

    def messageAddToHistory(self, data):
        """Store message into database (for local history)

        @param data: message data dictionnary
        @param client: profile's client
        """
        if data[u"type"] != C.MESS_TYPE_GROUPCHAT:
            # we don't add groupchat message to history, as we get them back
            # and they will be added then
            if data[u"message"] or data[u"subject"]:  # we need a message to store
                self.host_app.memory.addToHistory(self, data)
            else:
                log.warning(
                    u"No message found"
                )  # empty body should be managed by plugins before this point
        return data

    def messageSendToBridge(self, data):
        """Send message to bridge, so frontends can display it

        @param data: message data dictionnary
        @param client: profile's client
        """
        if data[u"type"] != C.MESS_TYPE_GROUPCHAT:
            # we don't send groupchat message to bridge, as we get them back
            # and they will be added the
            if (
                data[u"message"] or data[u"subject"]
            ):  # we need a message to send something
                # We send back the message, so all frontends are aware of it
                self.host_app.bridge.messageNew(
                    data[u"uid"],
                    data[u"timestamp"],
                    data[u"from"].full(),
                    data[u"to"].full(),
                    data[u"message"],
                    data[u"subject"],
                    data[u"type"],
                    data[u"extra"],
                    profile=self.profile,
                )
            else:
                log.warning(_(u"No message found"))
        return data


class SatXMPPClient(SatXMPPEntity, wokkel_client.XMPPClient):
    implements(iwokkel.IDisco)
    trigger_suffix = ""
    is_component = False

    def __init__(
        self,
        host_app,
        profile,
        user_jid,
        password,
        host=None,
        port=C.XMPP_C2S_PORT,
        max_retries=C.XMPP_MAX_RETRIES,
    ):
        # XXX: DNS SRV records are checked when the host is not specified.
        # If no SRV record is found, the host is directly extracted from the JID.
        self.started = time.time()

        # Currently, we use "client/pc/Salut à Toi", but as
        # SàT is multi-frontends and can be used on mobile devices, as a bot, with a web frontend,
        # etc., we should implement a way to dynamically update identities through the bridge
        self.identities = [disco.DiscoIdentity(u"client", u"pc", C.APP_NAME)]
        if sys.platform == "android":
            # FIXME: temporary hack as SRV is not working on android
            # TODO: remove this hack and fix SRV
            log.info(u"FIXME: Android hack, ignoring SRV")
            if host is None:
                host = user_jid.host
            # for now we consider Android devices to be always phones
            self.identities = [disco.DiscoIdentity(u"client", u"phone", C.APP_NAME)]

        hosts_map = host_app.memory.getConfig(None, "hosts_dict", {})
        if host is None and user_jid.host in hosts_map:
            host_data = hosts_map[user_jid.host]
            if isinstance(host_data, basestring):
                host = host_data
            elif isinstance(host_data, dict):
                if u"host" in host_data:
                    host = host_data[u"host"]
                if u"port" in host_data:
                    port = host_data[u"port"]
            else:
                log.warning(
                    _(u"invalid data used for host: {data}").format(data=host_data)
                )
                host_data = None
            if host_data is not None:
                log.info(
                    u"using {host}:{port} for host {host_ori} as requested in config".format(
                        host_ori=user_jid.host, host=host, port=port
                    )
                )

        wokkel_client.XMPPClient.__init__(
            self, user_jid, password, host or None, port or C.XMPP_C2S_PORT
        )
        SatXMPPEntity.__init__(self, host_app, profile, max_retries)

    def _getPluginsList(self):
        for p in self.host_app.plugins.itervalues():
            if C.PLUG_MODE_CLIENT in p._info[u"modes"]:
                yield p

    def _createSubProtocols(self):
        self.messageProt = SatMessageProtocol(self.host_app)
        self.messageProt.setHandlerParent(self)

        self.roster = SatRosterProtocol(self.host_app)
        self.roster.setHandlerParent(self)

        self.presence = SatPresenceProtocol(self.host_app)
        self.presence.setHandlerParent(self)

    def entityConnected(self):
        # we want to be sure that we got the roster
        return self.roster.got_roster

    def addPostXmlCallbacks(self, post_xml_treatments):
        post_xml_treatments.addCallback(self.messageAddToHistory)
        post_xml_treatments.addCallback(self.messageSendToBridge)

    def send(self, obj):
        # original send method accept string
        # but we restrict to domish.Element to make trigger treatments easier
        assert isinstance(obj, domish.Element)
        # XXX: this trigger is the last one before sending stanza on wire
        #      it is intended for things like end 2 end encryption.
        #      *DO NOT* cancel (i.e. return False) without very good reason
        #      (out of band transmission for instance).
        #      e2e should have a priority of 0 here, and out of band transmission
        #      a lower priority
        #  FIXME: trigger not used yet, can be uncommented when e2e full stanza encryption is implemented
        #  if not self.host_app.trigger.point("send", self, obj):
        #      return
        super(SatXMPPClient, self).send(obj)

    def sendMessageData(self, mess_data):
        """Convenient method to send message data to stream

        This method will send mess_data[u'xml'] to stream, but a trigger is there
        The trigger can't be cancelled, it's a good place for e2e encryption which
        don't handle full stanza encryption
        @param mess_data(dict): message data as constructed by onMessage workflow
        @return (dict): mess_data (so it can be used in a deferred chain)
        """
        # XXX: This is the last trigger before u"send" (last but one globally) for sending message.
        #      This is intented for e2e encryption which doesn't do full stanza encryption (e.g. OTR)
        #      This trigger point can't cancel the method
        self.host_app.trigger.point("sendMessageData", self, mess_data)
        self.send(mess_data[u"xml"])
        return mess_data

    def feedback(self, to_jid, message):
        """Send message to frontends

        This message will be an info message, not recorded in history.
        It can be used to give feedback of a command
        @param to_jid(jid.JID): destinee jid
        @param message(unicode): message to send to frontends
        """
        self.host_app.bridge.messageNew(
            uid=unicode(uuid.uuid4()),
            timestamp=time.time(),
            from_jid=self.jid.full(),
            to_jid=to_jid.full(),
            message={u"": message},
            subject={},
            mess_type=C.MESS_TYPE_INFO,
            extra={},
            profile=self.profile,
        )

    def _finish_connection(self, dummy):
        self.roster.requestRoster()
        self.presence.available()
        super(SatXMPPClient, self)._finish_connection(dummy)


class SatXMPPComponent(SatXMPPEntity, component.Component):
    """XMPP component

    This component are similar but not identical to clients.
    An entry point plugin is launched after component is connected.
    Component need to instantiate MessageProtocol itself
    """

    implements(iwokkel.IDisco)
    trigger_suffix = (
        "Component"
    )  # used for to distinguish some trigger points set in SatXMPPEntity
    is_component = True
    sendHistory = (
        False
    )  # XXX: set to True from entry plugin to keep messages in history for received messages

    def __init__(
        self,
        host_app,
        profile,
        component_jid,
        password,
        host=None,
        port=None,
        max_retries=C.XMPP_MAX_RETRIES,
    ):
        self.started = time.time()
        if port is None:
            port = C.XMPP_COMPONENT_PORT

        ## entry point ##
        entry_point = host_app.memory.getEntryPoint(profile)
        try:
            self.entry_plugin = host_app.plugins[entry_point]
        except KeyError:
            raise exceptions.NotFound(
                _(u"The requested entry point ({entry_point}) is not available").format(
                    entry_point=entry_point
                )
            )

        self.identities = [disco.DiscoIdentity(u"component", u"generic", C.APP_NAME)]
        # jid is set automatically on bind by Twisted for Client, but not for Component
        self.jid = component_jid
        if host is None:
            try:
                host = component_jid.host.split(u".", 1)[1]
            except IndexError:
                raise ValueError(u"Can't guess host from jid, please specify a host")
        # XXX: component.Component expect unicode jid, while Client expect jid.JID.
        #      this is not consistent, so we use jid.JID for SatXMPP*
        component.Component.__init__(self, host, port, component_jid.full(), password)
        SatXMPPEntity.__init__(self, host_app, profile, max_retries)

    def _buildDependencies(self, current, plugins, required=True):
        """build recursively dependencies needed for a plugin

        this method build list of plugin needed for a component and raises
        errors if they are not available or not allowed for components
        @param current(object): parent plugin to check
            use entry_point for first call
        @param plugins(list): list of validated plugins, will be filled by the method
            give an empty list for first call
        @param required(bool): True if plugin is mandatory
            for recursive calls only, should not be modified by inital caller
        @raise InternalError: one of the plugin is not handling components
        @raise KeyError: one plugin should be present in self.host_app.plugins but it is not
        """
        if C.PLUG_MODE_COMPONENT not in current._info[u"modes"]:
            if not required:
                return
            else:
                log.error(
                    _(
                        u"Plugin {current_name} is needed for {entry_name}, but it doesn't handle component mode"
                    ).format(
                        current_name=current._info[u"import_name"],
                        entry_name=self.entry_plugin._info[u"import_name"],
                    )
                )
                raise exceptions.InternalError(_(u"invalid plugin mode"))

        for import_name in current._info.get(C.PI_DEPENDENCIES, []):
            # plugins are already loaded as dependencies
            # so we know they are in self.host_app.plugins
            dep = self.host_app.plugins[import_name]
            self._buildDependencies(dep, plugins)

        for import_name in current._info.get(C.PI_RECOMMENDATIONS, []):
            # here plugins are only recommendations,
            # so they may not exist in self.host_app.plugins
            try:
                dep = self.host_app.plugins[import_name]
            except KeyError:
                continue
            self._buildDependencies(dep, plugins, required=False)

        if current not in plugins:
            # current can be required for several plugins and so
            # it can already be present in the list
            plugins.append(current)

    def _getPluginsList(self):
        # XXX: for component we don't launch all plugins triggers
        #      but only the ones from which there is a dependency
        plugins = []
        self._buildDependencies(self.entry_plugin, plugins)
        return plugins

    def entityConnected(self):
        # we can now launch entry point
        try:
            start_cb = self.entry_plugin.componentStart
        except AttributeError:
            return
        else:
            return start_cb(self)

    def addPostXmlCallbacks(self, post_xml_treatments):
        if self.sendHistory:
            post_xml_treatments.addCallback(self.messageAddToHistory)


class SatMessageProtocol(xmppim.MessageProtocol):
    def __init__(self, host):
        xmppim.MessageProtocol.__init__(self)
        self.host = host

    @staticmethod
    def parseMessage(message_elt, client=None):
        """parse a message XML and return message_data

        @param message_elt(domish.Element): raw <message> xml
        @param client(SatXMPPClient, None): client to map message id to uid
            if None, mapping will not be done
        @return(dict): message data
        """
        message = {}
        subject = {}
        extra = {}
        data = {
            "from": jid.JID(message_elt["from"]),
            "to": jid.JID(message_elt["to"]),
            "uid": message_elt.getAttribute(
                "uid", unicode(uuid.uuid4())
            ),  # XXX: uid is not a standard attribute but may be added by plugins
            "message": message,
            "subject": subject,
            "type": message_elt.getAttribute("type", "normal"),
            "extra": extra,
        }

        if client is not None:
            try:
                data["stanza_id"] = message_elt["id"]
            except KeyError:
                pass
            else:
                client._mess_id_uid[(data["from"], data["stanza_id"])] = data["uid"]

        # message
        for e in message_elt.elements(C.NS_CLIENT, "body"):
            message[e.getAttribute((C.NS_XML, "lang"), "")] = unicode(e)

        # subject
        for e in message_elt.elements(C.NS_CLIENT, "subject"):
            subject[e.getAttribute((C.NS_XML, "lang"), "")] = unicode(e)

        # delay and timestamp
        try:
            delay_elt = message_elt.elements(delay.NS_DELAY, "delay").next()
        except StopIteration:
            data["timestamp"] = time.time()
        else:
            parsed_delay = delay.Delay.fromElement(delay_elt)
            data["timestamp"] = calendar.timegm(parsed_delay.stamp.utctimetuple())
            data["received_timestamp"] = unicode(time.time())
            if parsed_delay.sender:
                data["delay_sender"] = parsed_delay.sender.full()
        return data

    def onMessage(self, message_elt):
        # TODO: handle threads
        client = self.parent
        if not "from" in message_elt.attributes:
            message_elt["from"] = client.jid.host
        log.debug(_(u"got message from: {from_}").format(from_=message_elt["from"]))
        post_treat = (
            defer.Deferred()
        )  # XXX: plugin can add their treatments to this deferred

        if not self.host.trigger.point(
            "MessageReceived", client, message_elt, post_treat
        ):
            return

        data = self.parseMessage(message_elt, client)

        post_treat.addCallback(self.skipEmptyMessage)
        post_treat.addCallback(self.addToHistory, client)
        post_treat.addCallback(self.bridgeSignal, client, data)
        post_treat.addErrback(self.cancelErrorTrap)
        post_treat.callback(data)

    def skipEmptyMessage(self, data):
        if not data["message"] and not data["extra"] and not data["subject"]:
            raise failure.Failure(exceptions.CancelError("Cancelled empty message"))
        return data

    def addToHistory(self, data, client):
        if data.pop(u"history", None) == C.HISTORY_SKIP:
            log.info(u"history is skipped as requested")
            data[u"extra"][u"history"] = C.HISTORY_SKIP
        else:
            return self.host.memory.addToHistory(client, data)

    def bridgeSignal(self, dummy, client, data):
        try:
            data["extra"]["received_timestamp"] = data["received_timestamp"]
            data["extra"]["delay_sender"] = data["delay_sender"]
        except KeyError:
            pass
        if data is not None:
            self.host.bridge.messageNew(
                data["uid"],
                data["timestamp"],
                data["from"].full(),
                data["to"].full(),
                data["message"],
                data["subject"],
                data["type"],
                data["extra"],
                profile=client.profile,
            )
        return data

    def cancelErrorTrap(self, failure_):
        """A message sending can be cancelled by a plugin treatment"""
        failure_.trap(exceptions.CancelError)


class SatRosterProtocol(xmppim.RosterClientProtocol):
    def __init__(self, host):
        xmppim.RosterClientProtocol.__init__(self)
        self.host = host
        self.got_roster = defer.Deferred()  # called when roster is received and ready
        # XXX: the two following dicts keep a local copy of the roster
        self._groups = {}  # map from groups to jids: key=group value=set of jids
        self._jids = None  # map from jids to RosterItem: key=jid value=RosterItem

    def rosterCb(self, roster):
        assert roster is not None  # FIXME: must be managed with roster versioning
        self._groups.clear()
        self._jids = roster
        for item in roster.itervalues():
            if not item.subscriptionTo and not item.subscriptionFrom and not item.ask:
                # XXX: current behaviour: we don't want contact in our roster list
                # if there is no presence subscription
                # may change in the future
                log.info(
                    u"Removing contact {} from roster because there is no presence subscription".format(
                        item.jid
                    )
                )
                self.removeItem(item.entity)  # FIXME: to be checked
            else:
                self._registerItem(item)

    def _registerItem(self, item):
        """Register item in local cache

        item must be already registered in self._jids before this method is called
        @param item (RosterIem): item added
        """
        log.debug(u"registering item: {}".format(item.entity.full()))
        if item.entity.resource:
            log.warning(
                u"Received a roster item with a resource, this is not common but not restricted by RFC 6121, this case may be not well tested."
            )
        if not item.subscriptionTo:
            if not item.subscriptionFrom:
                log.info(
                    _(u"There's no subscription between you and [{}]!").format(
                        item.entity.full()
                    )
                )
            else:
                log.info(_(u"You are not subscribed to [{}]!").format(item.entity.full()))
        if not item.subscriptionFrom:
            log.info(_(u"[{}] is not subscribed to you!").format(item.entity.full()))

        for group in item.groups:
            self._groups.setdefault(group, set()).add(item.entity)

    def requestRoster(self):
        """ ask the server for Roster list """
        log.debug("requestRoster")
        d = self.getRoster().addCallback(self.rosterCb)
        d.chainDeferred(self.got_roster)

    def removeItem(self, to_jid):
        """Remove a contact from roster list
        @param to_jid: a JID instance
        @return: Deferred
        """
        return xmppim.RosterClientProtocol.removeItem(self, to_jid)

    def getAttributes(self, item):
        """Return dictionary of attributes as used in bridge from a RosterItem

        @param item: RosterItem
        @return: dictionary of attributes
        """
        item_attr = {
            "to": unicode(item.subscriptionTo),
            "from": unicode(item.subscriptionFrom),
            "ask": unicode(item.ask),
        }
        if item.name:
            item_attr["name"] = item.name
        return item_attr

    def setReceived(self, request):
        # TODO: implement roster versioning (cf RFC 6121 §2.6)
        item = request.item
        try:  # update the cache for the groups the contact has been removed from
            left_groups = set(self._jids[item.entity].groups).difference(item.groups)
            for group in left_groups:
                jids_set = self._groups[group]
                jids_set.remove(item.entity)
                if not jids_set:
                    del self._groups[group]
        except KeyError:
            pass  # no previous item registration (or it's been cleared)
        self._jids[item.entity] = item
        self._registerItem(item)
        self.host.bridge.newContact(
            item.entity.full(), self.getAttributes(item), item.groups, self.parent.profile
        )

    def removeReceived(self, request):
        entity = request.item.entity
        log.info(u"removing %s from roster list" % entity.full())

        # we first remove item from local cache (self._groups and self._jids)
        try:
            item = self._jids.pop(entity)
        except KeyError:
            log.error(
                u"Received a roster remove event for an item not in cache ({})".format(
                    entity
                )
            )
            return
        for group in item.groups:
            try:
                jids_set = self._groups[group]
                jids_set.remove(entity)
                if not jids_set:
                    del self._groups[group]
            except KeyError:
                log.warning(
                    u"there is no cache for the group [%(group)s] of the removed roster item [%(jid)s]"
                    % {"group": group, "jid": entity}
                )

        # then we send the bridge signal
        self.host.bridge.contactDeleted(entity.full(), self.parent.profile)

    def getGroups(self):
        """Return a list of groups"""
        return self._groups.keys()

    def getItem(self, entity_jid):
        """Return RosterItem for a given jid

        @param entity_jid(jid.JID): jid of the contact
        @return(RosterItem, None): RosterItem instance
            None if contact is not in cache
        """
        return self._jids.get(entity_jid, None)

    def getJids(self):
        """Return all jids of the roster"""
        return self._jids.keys()

    def isJidInRoster(self, entity_jid):
        """Return True if jid is in roster"""
        return entity_jid in self._jids

    def isPresenceAuthorised(self, entity_jid):
        """Return True if entity is authorised to see our presence"""
        try:
            item = self._jids[entity_jid.userhostJID()]
        except KeyError:
            return False
        return item.subscriptionFrom

    def getItems(self):
        """Return all items of the roster"""
        return self._jids.values()

    def getJidsFromGroup(self, group):
        try:
            return self._groups[group]
        except KeyError:
            raise exceptions.UnknownGroupError(group)

    def getJidsSet(self, type_, groups=None):
        """Helper method to get a set of jids

        @param type_(unicode): one of:
            C.ALL: get all jids from roster
            C.GROUP: get jids from groups (listed in "groups")
        @groups(list[unicode]): list of groups used if type_==C.GROUP
        @return (set(jid.JID)): set of selected jids
        """
        if type_ == C.ALL and groups is not None:
            raise ValueError("groups must not be set for {} type".format(C.ALL))

        if type_ == C.ALL:
            return set(self.getJids())
        elif type_ == C.GROUP:
            jids = set()
            for group in groups:
                jids.update(self.getJidsFromGroup(group))
            return jids
        else:
            raise ValueError(u"Unexpected type_ {}".format(type_))

    def getNick(self, entity_jid):
        """Return a nick name for an entity

        return nick choosed by user if available
        else return user part of entity_jid
        """
        item = self.getItem(entity_jid)
        if item is None:
            return entity_jid.user
        else:
            return item.name or entity_jid.user


class SatPresenceProtocol(xmppim.PresenceClientProtocol):
    def __init__(self, host):
        xmppim.PresenceClientProtocol.__init__(self)
        self.host = host

    def send(self, obj):
        presence_d = defer.succeed(None)
        if not self.host.trigger.point("Presence send", self.parent, obj, presence_d):
            return
        presence_d.addCallback(lambda __: super(SatPresenceProtocol, self).send(obj))

    def availableReceived(self, entity, show=None, statuses=None, priority=0):
        log.debug(
            _(
                u"presence update for [%(entity)s] (available, show=%(show)s statuses=%(statuses)s priority=%(priority)d)"
            )
            % {
                "entity": entity,
                C.PRESENCE_SHOW: show,
                C.PRESENCE_STATUSES: statuses,
                C.PRESENCE_PRIORITY: priority,
            }
        )

        if not statuses:
            statuses = {}

        if None in statuses:  # we only want string keys
            statuses[C.PRESENCE_STATUSES_DEFAULT] = statuses.pop(None)

        if not self.host.trigger.point(
            "presenceReceived", entity, show, priority, statuses, self.parent.profile
        ):
            return

        self.host.memory.setPresenceStatus(
            entity, show or "", int(priority), statuses, self.parent.profile
        )

        # now it's time to notify frontends
        self.host.bridge.presenceUpdate(
            entity.full(), show or "", int(priority), statuses, self.parent.profile
        )

    def unavailableReceived(self, entity, statuses=None):
        log.debug(
            _(u"presence update for [%(entity)s] (unavailable, statuses=%(statuses)s)")
            % {"entity": entity, C.PRESENCE_STATUSES: statuses}
        )

        if not statuses:
            statuses = {}

        if None in statuses:  # we only want string keys
            statuses[C.PRESENCE_STATUSES_DEFAULT] = statuses.pop(None)

        if not self.host.trigger.point(
            "presenceReceived", entity, "unavailable", 0, statuses, self.parent.profile
        ):
            return

        # now it's time to notify frontends
        # if the entity is not known yet in this session or is already unavailable, there is no need to send an unavailable signal
        try:
            presence = self.host.memory.getEntityDatum(
                entity, "presence", self.parent.profile
            )
        except (KeyError, exceptions.UnknownEntityError):
            # the entity has not been seen yet in this session
            pass
        else:
            if presence.show != C.PRESENCE_UNAVAILABLE:
                self.host.bridge.presenceUpdate(
                    entity.full(),
                    C.PRESENCE_UNAVAILABLE,
                    0,
                    statuses,
                    self.parent.profile,
                )

        self.host.memory.setPresenceStatus(
            entity, C.PRESENCE_UNAVAILABLE, 0, statuses, self.parent.profile
        )

    def available(self, entity=None, show=None, statuses=None, priority=None):
        """Set a presence and statuses.

        @param entity (jid.JID): entity
        @param show (unicode): value in ('unavailable', '', 'away', 'xa', 'chat', 'dnd')
        @param statuses (dict{unicode: unicode}): multilingual statuses with
            the entry key beeing a language code on 2 characters or "default".
        """
        if priority is None:
            try:
                priority = int(
                    self.host.memory.getParamA(
                        "Priority", "Connection", profile_key=self.parent.profile
                    )
                )
            except ValueError:
                priority = 0

        if statuses is None:
            statuses = {}

        # default for us is None for wokkel
        # so we must temporarily switch to wokkel's convention...
        if C.PRESENCE_STATUSES_DEFAULT in statuses:
            statuses[None] = statuses.pop(C.PRESENCE_STATUSES_DEFAULT)

        presence_elt = xmppim.AvailablePresence(entity, show, statuses, priority)

        # ... before switching back
        if None in statuses:
            statuses["default"] = statuses.pop(None)

        if not self.host.trigger.point("presence_available", presence_elt, self.parent):
            return
        self.send(presence_elt)

    @defer.inlineCallbacks
    def subscribed(self, entity):
        yield self.parent.roster.got_roster
        xmppim.PresenceClientProtocol.subscribed(self, entity)
        self.host.memory.delWaitingSub(entity.userhost(), self.parent.profile)
        item = self.parent.roster.getItem(entity)
        if (
            not item or not item.subscriptionTo
        ):  # we automatically subscribe to 'to' presence
            log.debug(_('sending automatic "from" subscription request'))
            self.subscribe(entity)

    def unsubscribed(self, entity):
        xmppim.PresenceClientProtocol.unsubscribed(self, entity)
        self.host.memory.delWaitingSub(entity.userhost(), self.parent.profile)

    def subscribedReceived(self, entity):
        log.debug(_(u"subscription approved for [%s]") % entity.userhost())
        self.host.bridge.subscribe("subscribed", entity.userhost(), self.parent.profile)

    def unsubscribedReceived(self, entity):
        log.debug(_(u"unsubscription confirmed for [%s]") % entity.userhost())
        self.host.bridge.subscribe("unsubscribed", entity.userhost(), self.parent.profile)

    @defer.inlineCallbacks
    def subscribeReceived(self, entity):
        log.debug(_(u"subscription request from [%s]") % entity.userhost())
        yield self.parent.roster.got_roster
        item = self.parent.roster.getItem(entity)
        if item and item.subscriptionTo:
            # We automatically accept subscription if we are already subscribed to contact presence
            log.debug(_("sending automatic subscription acceptance"))
            self.subscribed(entity)
        else:
            self.host.memory.addWaitingSub(
                "subscribe", entity.userhost(), self.parent.profile
            )
            self.host.bridge.subscribe(
                "subscribe", entity.userhost(), self.parent.profile
            )

    @defer.inlineCallbacks
    def unsubscribeReceived(self, entity):
        log.debug(_(u"unsubscription asked for [%s]") % entity.userhost())
        yield self.parent.roster.got_roster
        item = self.parent.roster.getItem(entity)
        if item and item.subscriptionFrom:  # we automatically remove contact
            log.debug(_("automatic contact deletion"))
            self.host.delContact(entity, self.parent.profile)
        self.host.bridge.subscribe("unsubscribe", entity.userhost(), self.parent.profile)


class SatDiscoProtocol(disco.DiscoClientProtocol):
    def __init__(self, host):
        disco.DiscoClientProtocol.__init__(self)


class SatFallbackHandler(generic.FallbackHandler):
    def __init__(self, host):
        generic.FallbackHandler.__init__(self)

    def iqFallback(self, iq):
        if iq.handled is True:
            return
        log.debug(u"iqFallback: xml = [%s]" % (iq.toXml()))
        generic.FallbackHandler.iqFallback(self, iq)


class SatVersionHandler(generic.VersionHandler):
    def getDiscoInfo(self, requestor, target, node):
        # XXX: We need to work around wokkel's behaviour (namespace not added if there is a
        # node) as it cause issues with XEP-0115 & PEP (XEP-0163): there is a node when server
        # ask for disco info, and not when we generate the key, so the hash is used with different
        # disco features, and when the server (seen on ejabberd) generate its own hash for security check
        # it reject our features (resulting in e.g. no notification on PEP)
        return generic.VersionHandler.getDiscoInfo(self, requestor, target, None)


class SatIdentityHandler(XMPPHandler):
    """ Manage disco Identity of SàT.

    """

    # TODO: dynamic identity update (see docstring). Note that a XMPP entity can have several identities
    implements(iwokkel.IDisco)

    def getDiscoInfo(self, requestor, target, nodeIdentifier=""):
        return self.parent.identities

    def getDiscoItems(self, requestor, target, nodeIdentifier=""):
        return []
