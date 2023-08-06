#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SàT: a XMPP client
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

from sat.core.log import getLogger

log = getLogger(__name__)
from sat.core import exceptions


class _Bridge(object):
    def __init__(self):
        log.debug(u"Init embedded bridge...")
        self._methods_cbs = {}
        self._signals_cbs = {"core": {}, "plugin": {}}

    def bridgeConnect(self, callback, errback):
        callback()

    def register_method(self, name, callback):
        log.debug(u"registering embedded bridge method [{}]".format(name))
        if name in self._methods_cbs:
            raise exceptions.ConflictError(u"method {} is already regitered".format(name))
        self._methods_cbs[name] = callback

    def register_signal(self, functionName, handler, iface="core"):
        iface_dict = self._signals_cbs[iface]
        if functionName in iface_dict:
            raise exceptions.ConflictError(
                u"signal {name} is already regitered for interface {iface}".format(
                    name=functionName, iface=iface
                )
            )
        iface_dict[functionName] = handler

    def call_method(self, name, out_sign, async_, args, kwargs):
        callback = kwargs.pop("callback", None)
        errback = kwargs.pop("errback", None)
        if async_:
            d = self._methods_cbs[name](*args, **kwargs)
            if callback is not None:
                d.addCallback(callback if out_sign else lambda dummy: callback())
            if errback is None:
                d.addErrback(lambda failure_: log.error(failure_))
            else:
                d.addErrback(errback)
            return d
        else:
            try:
                ret = self._methods_cbs[name](*args, **kwargs)
            except Exception as e:
                if errback is not None:
                    errback(e)
                else:
                    raise e
            else:
                if callback is None:
                    return ret
                else:
                    if out_sign:
                        callback(ret)
                    else:
                        callback()

    def send_signal(self, name, args, kwargs):
        try:
            cb = self._signals_cbs["plugin"][name]
        except KeyError:
            log.debug(u"ignoring signal {}: no callback registered".format(name))
        else:
            cb(*args, **kwargs)

    def addMethod(self, name, int_suffix, in_sign, out_sign, method, async=False, doc={}):
        # FIXME: doc parameter is kept only temporary, the time to remove it from calls
        log.debug("Adding method [{}] to embedded bridge".format(name))
        self.register_method(name, method)
        setattr(
            self.__class__,
            name,
            lambda self_, *args, **kwargs: self.call_method(
                name, out_sign, async, args, kwargs
            ),
        )

    def addSignal(self, name, int_suffix, signature, doc={}):
        setattr(
            self.__class__,
            name,
            lambda self_, *args, **kwargs: self.send_signal(name, args, kwargs),
        )

    ## signals ##


    def actionNew(self, action_data, id, security_limit, profile):
        try:
            cb = self._signals_cbs["core"]["actionNew"]
        except KeyError:
            log.warning(u"ignoring signal actionNew: no callback registered")
        else:
            cb(action_data, id, security_limit, profile)

    def connected(self, profile, jid_s):
        try:
            cb = self._signals_cbs["core"]["connected"]
        except KeyError:
            log.warning(u"ignoring signal connected: no callback registered")
        else:
            cb(profile, jid_s)

    def contactDeleted(self, entity_jid, profile):
        try:
            cb = self._signals_cbs["core"]["contactDeleted"]
        except KeyError:
            log.warning(u"ignoring signal contactDeleted: no callback registered")
        else:
            cb(entity_jid, profile)

    def disconnected(self, profile):
        try:
            cb = self._signals_cbs["core"]["disconnected"]
        except KeyError:
            log.warning(u"ignoring signal disconnected: no callback registered")
        else:
            cb(profile)

    def entityDataUpdated(self, jid, name, value, profile):
        try:
            cb = self._signals_cbs["core"]["entityDataUpdated"]
        except KeyError:
            log.warning(u"ignoring signal entityDataUpdated: no callback registered")
        else:
            cb(jid, name, value, profile)

    def messageNew(self, uid, timestamp, from_jid, to_jid, message, subject, mess_type, extra, profile):
        try:
            cb = self._signals_cbs["core"]["messageNew"]
        except KeyError:
            log.warning(u"ignoring signal messageNew: no callback registered")
        else:
            cb(uid, timestamp, from_jid, to_jid, message, subject, mess_type, extra, profile)

    def newContact(self, contact_jid, attributes, groups, profile):
        try:
            cb = self._signals_cbs["core"]["newContact"]
        except KeyError:
            log.warning(u"ignoring signal newContact: no callback registered")
        else:
            cb(contact_jid, attributes, groups, profile)

    def paramUpdate(self, name, value, category, profile):
        try:
            cb = self._signals_cbs["core"]["paramUpdate"]
        except KeyError:
            log.warning(u"ignoring signal paramUpdate: no callback registered")
        else:
            cb(name, value, category, profile)

    def presenceUpdate(self, entity_jid, show, priority, statuses, profile):
        try:
            cb = self._signals_cbs["core"]["presenceUpdate"]
        except KeyError:
            log.warning(u"ignoring signal presenceUpdate: no callback registered")
        else:
            cb(entity_jid, show, priority, statuses, profile)

    def progressError(self, id, error, profile):
        try:
            cb = self._signals_cbs["core"]["progressError"]
        except KeyError:
            log.warning(u"ignoring signal progressError: no callback registered")
        else:
            cb(id, error, profile)

    def progressFinished(self, id, metadata, profile):
        try:
            cb = self._signals_cbs["core"]["progressFinished"]
        except KeyError:
            log.warning(u"ignoring signal progressFinished: no callback registered")
        else:
            cb(id, metadata, profile)

    def progressStarted(self, id, metadata, profile):
        try:
            cb = self._signals_cbs["core"]["progressStarted"]
        except KeyError:
            log.warning(u"ignoring signal progressStarted: no callback registered")
        else:
            cb(id, metadata, profile)

    def subscribe(self, sub_type, entity_jid, profile):
        try:
            cb = self._signals_cbs["core"]["subscribe"]
        except KeyError:
            log.warning(u"ignoring signal subscribe: no callback registered")
        else:
            cb(sub_type, entity_jid, profile)

## methods ##

    def actionsGet(self, profile_key="@DEFAULT@", callback=None, errback=None):
        try:
            ret = self._methods_cbs["actionsGet"](profile_key)
        except Exception as e:
            if errback is not None:
                errback(e)
            else:
                raise e
        else:
            if callback is None:
                return ret
            else:
                callback(ret)

    def addContact(self, entity_jid, profile_key="@DEFAULT@", callback=None, errback=None):
        try:
            ret = self._methods_cbs["addContact"](entity_jid, profile_key)
        except Exception as e:
            if errback is not None:
                errback(e)
            else:
                raise e
        else:
            if callback is None:
                return ret
            else:
                callback()

    def asyncDeleteProfile(self, profile, callback=None, errback=None):
        d = self._methods_cbs["asyncDeleteProfile"](profile)
        if callback is not None:
            d.addCallback(lambda dummy: callback())
        if errback is None:
            d.addErrback(lambda failure_: log.error(failure_))
        else:
            d.addErrback(errback)
        return d
        

    def asyncGetParamA(self, name, category, attribute="value", security_limit=-1, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self._methods_cbs["asyncGetParamA"](name, category, attribute, security_limit, profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(lambda failure_: log.error(failure_))
        else:
            d.addErrback(errback)
        return d
        

    def asyncGetParamsValuesFromCategory(self, category, security_limit=-1, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self._methods_cbs["asyncGetParamsValuesFromCategory"](category, security_limit, profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(lambda failure_: log.error(failure_))
        else:
            d.addErrback(errback)
        return d
        

    def connect(self, profile_key="@DEFAULT@", password='', options={}, callback=None, errback=None):
        d = self._methods_cbs["connect"](profile_key, password, options)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(lambda failure_: log.error(failure_))
        else:
            d.addErrback(errback)
        return d
        

    def delContact(self, entity_jid, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self._methods_cbs["delContact"](entity_jid, profile_key)
        if callback is not None:
            d.addCallback(lambda dummy: callback())
        if errback is None:
            d.addErrback(lambda failure_: log.error(failure_))
        else:
            d.addErrback(errback)
        return d
        

    def discoFindByFeatures(self, namespaces, identities, bare_jid=False, service=True, roster=True, own_jid=True, local_device=False, profile_key=u"@DEFAULT@", callback=None, errback=None):
        d = self._methods_cbs["discoFindByFeatures"](namespaces, identities, bare_jid, service, roster, own_jid, local_device, profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(lambda failure_: log.error(failure_))
        else:
            d.addErrback(errback)
        return d
        

    def discoInfos(self, entity_jid, node=u'', use_cache=True, profile_key=u"@DEFAULT@", callback=None, errback=None):
        d = self._methods_cbs["discoInfos"](entity_jid, node, use_cache, profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(lambda failure_: log.error(failure_))
        else:
            d.addErrback(errback)
        return d
        

    def discoItems(self, entity_jid, node=u'', use_cache=True, profile_key=u"@DEFAULT@", callback=None, errback=None):
        d = self._methods_cbs["discoItems"](entity_jid, node, use_cache, profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(lambda failure_: log.error(failure_))
        else:
            d.addErrback(errback)
        return d
        

    def disconnect(self, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self._methods_cbs["disconnect"](profile_key)
        if callback is not None:
            d.addCallback(lambda dummy: callback())
        if errback is None:
            d.addErrback(lambda failure_: log.error(failure_))
        else:
            d.addErrback(errback)
        return d
        

    def getConfig(self, section, name, callback=None, errback=None):
        try:
            ret = self._methods_cbs["getConfig"](section, name)
        except Exception as e:
            if errback is not None:
                errback(e)
            else:
                raise e
        else:
            if callback is None:
                return ret
            else:
                callback(ret)

    def getContacts(self, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self._methods_cbs["getContacts"](profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(lambda failure_: log.error(failure_))
        else:
            d.addErrback(errback)
        return d
        

    def getContactsFromGroup(self, group, profile_key="@DEFAULT@", callback=None, errback=None):
        try:
            ret = self._methods_cbs["getContactsFromGroup"](group, profile_key)
        except Exception as e:
            if errback is not None:
                errback(e)
            else:
                raise e
        else:
            if callback is None:
                return ret
            else:
                callback(ret)

    def getEntitiesData(self, jids, keys, profile, callback=None, errback=None):
        try:
            ret = self._methods_cbs["getEntitiesData"](jids, keys, profile)
        except Exception as e:
            if errback is not None:
                errback(e)
            else:
                raise e
        else:
            if callback is None:
                return ret
            else:
                callback(ret)

    def getEntityData(self, jid, keys, profile, callback=None, errback=None):
        try:
            ret = self._methods_cbs["getEntityData"](jid, keys, profile)
        except Exception as e:
            if errback is not None:
                errback(e)
            else:
                raise e
        else:
            if callback is None:
                return ret
            else:
                callback(ret)

    def getFeatures(self, profile_key, callback=None, errback=None):
        d = self._methods_cbs["getFeatures"](profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(lambda failure_: log.error(failure_))
        else:
            d.addErrback(errback)
        return d
        

    def getMainResource(self, contact_jid, profile_key="@DEFAULT@", callback=None, errback=None):
        try:
            ret = self._methods_cbs["getMainResource"](contact_jid, profile_key)
        except Exception as e:
            if errback is not None:
                errback(e)
            else:
                raise e
        else:
            if callback is None:
                return ret
            else:
                callback(ret)

    def getParamA(self, name, category, attribute="value", profile_key="@DEFAULT@", callback=None, errback=None):
        try:
            ret = self._methods_cbs["getParamA"](name, category, attribute, profile_key)
        except Exception as e:
            if errback is not None:
                errback(e)
            else:
                raise e
        else:
            if callback is None:
                return ret
            else:
                callback(ret)

    def getParamsCategories(self, callback=None, errback=None):
        try:
            ret = self._methods_cbs["getParamsCategories"]()
        except Exception as e:
            if errback is not None:
                errback(e)
            else:
                raise e
        else:
            if callback is None:
                return ret
            else:
                callback(ret)

    def getParamsUI(self, security_limit=-1, app='', profile_key="@DEFAULT@", callback=None, errback=None):
        d = self._methods_cbs["getParamsUI"](security_limit, app, profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(lambda failure_: log.error(failure_))
        else:
            d.addErrback(errback)
        return d
        

    def getPresenceStatuses(self, profile_key="@DEFAULT@", callback=None, errback=None):
        try:
            ret = self._methods_cbs["getPresenceStatuses"](profile_key)
        except Exception as e:
            if errback is not None:
                errback(e)
            else:
                raise e
        else:
            if callback is None:
                return ret
            else:
                callback(ret)

    def getReady(self, callback=None, errback=None):
        d = self._methods_cbs["getReady"]()
        if callback is not None:
            d.addCallback(lambda dummy: callback())
        if errback is None:
            d.addErrback(lambda failure_: log.error(failure_))
        else:
            d.addErrback(errback)
        return d
        

    def getVersion(self, callback=None, errback=None):
        try:
            ret = self._methods_cbs["getVersion"]()
        except Exception as e:
            if errback is not None:
                errback(e)
            else:
                raise e
        else:
            if callback is None:
                return ret
            else:
                callback(ret)

    def getWaitingSub(self, profile_key="@DEFAULT@", callback=None, errback=None):
        try:
            ret = self._methods_cbs["getWaitingSub"](profile_key)
        except Exception as e:
            if errback is not None:
                errback(e)
            else:
                raise e
        else:
            if callback is None:
                return ret
            else:
                callback(ret)

    def historyGet(self, from_jid, to_jid, limit, between=True, filters='', profile="@NONE@", callback=None, errback=None):
        d = self._methods_cbs["historyGet"](from_jid, to_jid, limit, between, filters, profile)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(lambda failure_: log.error(failure_))
        else:
            d.addErrback(errback)
        return d
        

    def isConnected(self, profile_key="@DEFAULT@", callback=None, errback=None):
        try:
            ret = self._methods_cbs["isConnected"](profile_key)
        except Exception as e:
            if errback is not None:
                errback(e)
            else:
                raise e
        else:
            if callback is None:
                return ret
            else:
                callback(ret)

    def launchAction(self, callback_id, data, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self._methods_cbs["launchAction"](callback_id, data, profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(lambda failure_: log.error(failure_))
        else:
            d.addErrback(errback)
        return d
        

    def loadParamsTemplate(self, filename, callback=None, errback=None):
        try:
            ret = self._methods_cbs["loadParamsTemplate"](filename)
        except Exception as e:
            if errback is not None:
                errback(e)
            else:
                raise e
        else:
            if callback is None:
                return ret
            else:
                callback(ret)

    def menuHelpGet(self, menu_id, language, callback=None, errback=None):
        try:
            ret = self._methods_cbs["menuHelpGet"](menu_id, language)
        except Exception as e:
            if errback is not None:
                errback(e)
            else:
                raise e
        else:
            if callback is None:
                return ret
            else:
                callback(ret)

    def menuLaunch(self, menu_type, path, data, security_limit, profile_key, callback=None, errback=None):
        d = self._methods_cbs["menuLaunch"](menu_type, path, data, security_limit, profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(lambda failure_: log.error(failure_))
        else:
            d.addErrback(errback)
        return d
        

    def menusGet(self, language, security_limit, callback=None, errback=None):
        try:
            ret = self._methods_cbs["menusGet"](language, security_limit)
        except Exception as e:
            if errback is not None:
                errback(e)
            else:
                raise e
        else:
            if callback is None:
                return ret
            else:
                callback(ret)

    def messageSend(self, to_jid, message, subject={}, mess_type="auto", extra={}, profile_key="@NONE@", callback=None, errback=None):
        d = self._methods_cbs["messageSend"](to_jid, message, subject, mess_type, extra, profile_key)
        if callback is not None:
            d.addCallback(lambda dummy: callback())
        if errback is None:
            d.addErrback(lambda failure_: log.error(failure_))
        else:
            d.addErrback(errback)
        return d
        

    def namespacesGet(self, callback=None, errback=None):
        try:
            ret = self._methods_cbs["namespacesGet"]()
        except Exception as e:
            if errback is not None:
                errback(e)
            else:
                raise e
        else:
            if callback is None:
                return ret
            else:
                callback(ret)

    def paramsRegisterApp(self, xml, security_limit=-1, app='', callback=None, errback=None):
        try:
            ret = self._methods_cbs["paramsRegisterApp"](xml, security_limit, app)
        except Exception as e:
            if errback is not None:
                errback(e)
            else:
                raise e
        else:
            if callback is None:
                return ret
            else:
                callback()

    def profileCreate(self, profile, password='', component='', callback=None, errback=None):
        d = self._methods_cbs["profileCreate"](profile, password, component)
        if callback is not None:
            d.addCallback(lambda dummy: callback())
        if errback is None:
            d.addErrback(lambda failure_: log.error(failure_))
        else:
            d.addErrback(errback)
        return d
        

    def profileIsSessionStarted(self, profile_key="@DEFAULT@", callback=None, errback=None):
        try:
            ret = self._methods_cbs["profileIsSessionStarted"](profile_key)
        except Exception as e:
            if errback is not None:
                errback(e)
            else:
                raise e
        else:
            if callback is None:
                return ret
            else:
                callback(ret)

    def profileNameGet(self, profile_key="@DEFAULT@", callback=None, errback=None):
        try:
            ret = self._methods_cbs["profileNameGet"](profile_key)
        except Exception as e:
            if errback is not None:
                errback(e)
            else:
                raise e
        else:
            if callback is None:
                return ret
            else:
                callback(ret)

    def profileSetDefault(self, profile, callback=None, errback=None):
        try:
            ret = self._methods_cbs["profileSetDefault"](profile)
        except Exception as e:
            if errback is not None:
                errback(e)
            else:
                raise e
        else:
            if callback is None:
                return ret
            else:
                callback()

    def profileStartSession(self, password='', profile_key="@DEFAULT@", callback=None, errback=None):
        d = self._methods_cbs["profileStartSession"](password, profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(lambda failure_: log.error(failure_))
        else:
            d.addErrback(errback)
        return d
        

    def profilesListGet(self, clients=True, components=False, callback=None, errback=None):
        try:
            ret = self._methods_cbs["profilesListGet"](clients, components)
        except Exception as e:
            if errback is not None:
                errback(e)
            else:
                raise e
        else:
            if callback is None:
                return ret
            else:
                callback(ret)

    def progressGet(self, id, profile, callback=None, errback=None):
        try:
            ret = self._methods_cbs["progressGet"](id, profile)
        except Exception as e:
            if errback is not None:
                errback(e)
            else:
                raise e
        else:
            if callback is None:
                return ret
            else:
                callback(ret)

    def progressGetAll(self, profile, callback=None, errback=None):
        try:
            ret = self._methods_cbs["progressGetAll"](profile)
        except Exception as e:
            if errback is not None:
                errback(e)
            else:
                raise e
        else:
            if callback is None:
                return ret
            else:
                callback(ret)

    def progressGetAllMetadata(self, profile, callback=None, errback=None):
        try:
            ret = self._methods_cbs["progressGetAllMetadata"](profile)
        except Exception as e:
            if errback is not None:
                errback(e)
            else:
                raise e
        else:
            if callback is None:
                return ret
            else:
                callback(ret)

    def saveParamsTemplate(self, filename, callback=None, errback=None):
        try:
            ret = self._methods_cbs["saveParamsTemplate"](filename)
        except Exception as e:
            if errback is not None:
                errback(e)
            else:
                raise e
        else:
            if callback is None:
                return ret
            else:
                callback(ret)

    def sessionInfosGet(self, profile_key, callback=None, errback=None):
        d = self._methods_cbs["sessionInfosGet"](profile_key)
        if callback is not None:
            d.addCallback(callback)
        if errback is None:
            d.addErrback(lambda failure_: log.error(failure_))
        else:
            d.addErrback(errback)
        return d
        

    def setParam(self, name, value, category, security_limit=-1, profile_key="@DEFAULT@", callback=None, errback=None):
        try:
            ret = self._methods_cbs["setParam"](name, value, category, security_limit, profile_key)
        except Exception as e:
            if errback is not None:
                errback(e)
            else:
                raise e
        else:
            if callback is None:
                return ret
            else:
                callback()

    def setPresence(self, to_jid='', show='', statuses={}, profile_key="@DEFAULT@", callback=None, errback=None):
        try:
            ret = self._methods_cbs["setPresence"](to_jid, show, statuses, profile_key)
        except Exception as e:
            if errback is not None:
                errback(e)
            else:
                raise e
        else:
            if callback is None:
                return ret
            else:
                callback()

    def subscription(self, sub_type, entity, profile_key="@DEFAULT@", callback=None, errback=None):
        try:
            ret = self._methods_cbs["subscription"](sub_type, entity, profile_key)
        except Exception as e:
            if errback is not None:
                errback(e)
            else:
                raise e
        else:
            if callback is None:
                return ret
            else:
                callback()

    def updateContact(self, entity_jid, name, groups, profile_key="@DEFAULT@", callback=None, errback=None):
        d = self._methods_cbs["updateContact"](entity_jid, name, groups, profile_key)
        if callback is not None:
            d.addCallback(lambda dummy: callback())
        if errback is None:
            d.addErrback(lambda failure_: log.error(failure_))
        else:
            d.addErrback(errback)
        return d
        


# we want the same instance for both core and frontend
bridge = None


def Bridge():
    global bridge
    if bridge is None:
        bridge = _Bridge()
    return bridge