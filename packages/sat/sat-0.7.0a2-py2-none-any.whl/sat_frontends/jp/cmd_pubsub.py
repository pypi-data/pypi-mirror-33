#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# jp: a SàT command line tool
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


import base
from sat.core.i18n import _
from sat.core import exceptions
from sat_frontends.jp.constants import Const as C
from sat_frontends.jp import common
from sat_frontends.jp import arg_tools
from functools import partial
from sat.tools.common import uri
from sat.tools.common.ansi import ANSI as A
from sat_frontends.tools import jid, strings
import argparse
import os.path
import re
import subprocess
import sys

__commands__ = ["Pubsub"]

PUBSUB_TMP_DIR = u"pubsub"
PUBSUB_SCHEMA_TMP_DIR = PUBSUB_TMP_DIR + "_schema"
ALLOWED_SUBSCRIPTIONS_OWNER = ("subscribed", "pending", "none")

# TODO: need to split this class in several modules, plugin should handle subcommands


class NodeInfo(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "info",
            use_output=C.OUTPUT_DICT,
            use_pubsub=True,
            pubsub_flags={C.NODE},
            help=_(u"retrieve node configuration"),
        )
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument(
            "-k",
            "--key",
            type=base.unicode_decoder,
            action="append",
            dest="keys",
            help=_(u"data key to filter"),
        )

    def removePrefix(self, key):
        return key[7:] if key.startswith(u"pubsub#") else key

    def filterKey(self, key):
        return any((key == k or key == u"pubsub#" + k) for k in self.args.keys)

    def psNodeConfigurationGetCb(self, config_dict):
        key_filter = (lambda k: True) if not self.args.keys else self.filterKey
        config_dict = {
            self.removePrefix(k): v for k, v in config_dict.iteritems() if key_filter(k)
        }
        self.output(config_dict)
        self.host.quit()

    def psNodeConfigurationGetEb(self, failure_):
        self.disp(
            u"can't get node configuration: {reason}".format(reason=failure_), error=True
        )
        self.host.quit(C.EXIT_BRIDGE_ERRBACK)

    def start(self):
        self.host.bridge.psNodeConfigurationGet(
            self.args.service,
            self.args.node,
            self.profile,
            callback=self.psNodeConfigurationGetCb,
            errback=self.psNodeConfigurationGetEb,
        )


class NodeCreate(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "create",
            use_output=C.OUTPUT_DICT,
            use_pubsub=True,
            pubsub_flags={C.NODE},
            use_verbose=True,
            help=_(u"create a node"),
        )
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument(
            "-f",
            "--field",
            type=base.unicode_decoder,
            action="append",
            nargs=2,
            dest="fields",
            default=[],
            metavar=(u"KEY", u"VALUE"),
            help=_(u"configuration field to set"),
        )
        self.parser.add_argument(
            "-F",
            "--full-prefix",
            action="store_true",
            help=_(u'don\'t prepend "pubsub#" prefix to field names'),
        )

    def psNodeCreateCb(self, node_id):
        if self.host.verbosity:
            announce = _(u"node created successfully: ")
        else:
            announce = u""
        self.disp(announce + node_id)
        self.host.quit()

    def psNodeCreateEb(self, failure_):
        self.disp(u"can't create: {reason}".format(reason=failure_), error=True)
        self.host.quit(C.EXIT_BRIDGE_ERRBACK)

    def start(self):
        if not self.args.full_prefix:
            options = {u"pubsub#" + k: v for k, v in self.args.fields}
        else:
            options = dict(self.args.fields)
        self.host.bridge.psNodeCreate(
            self.args.service,
            self.args.node,
            options,
            self.profile,
            callback=self.psNodeCreateCb,
            errback=partial(
                self.errback,
                msg=_(u"can't create node: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )


class NodeDelete(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "delete",
            use_pubsub=True,
            pubsub_flags={C.NODE},
            help=_(u"delete a node"),
        )
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help=_(u"delete node without confirmation"),
        )

    def psNodeDeleteCb(self):
        self.disp(_(u"node [{node}] deleted successfully").format(node=self.args.node))
        self.host.quit()

    def start(self):
        if not self.args.force:
            if not self.args.service:
                message = _(u"Are you sure to delete pep node [{node_id}] ?").format(
                    node_id=self.args.node
                )
            else:
                message = _(
                    u"Are you sure to delete node [{node_id}] on service [{service}] ?"
                ).format(node_id=self.args.node, service=self.args.service)
            self.host.confirmOrQuit(message, _(u"node deletion cancelled"))

        self.host.bridge.psNodeDelete(
            self.args.service,
            self.args.node,
            self.profile,
            callback=self.psNodeDeleteCb,
            errback=partial(
                self.errback,
                msg=_(u"can't delete node: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )


class NodeSet(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "set",
            use_output=C.OUTPUT_DICT,
            use_pubsub=True,
            pubsub_flags={C.NODE},
            use_verbose=True,
            help=_(u"set node configuration"),
        )
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument(
            "-f",
            "--field",
            type=base.unicode_decoder,
            action="append",
            nargs=2,
            dest="fields",
            required=True,
            metavar=(u"KEY", u"VALUE"),
            help=_(u"configuration field to set (required)"),
        )

    def psNodeConfigurationSetCb(self):
        self.disp(_(u"node configuration successful"), 1)
        self.host.quit()

    def psNodeConfigurationSetEb(self, failure_):
        self.disp(
            u"can't set node configuration: {reason}".format(reason=failure_), error=True
        )
        self.host.quit(C.EXIT_BRIDGE_ERRBACK)

    def getKeyName(self, k):
        if not k.startswith(u"pubsub#"):
            return u"pubsub#" + k
        else:
            return k

    def start(self):
        self.host.bridge.psNodeConfigurationSet(
            self.args.service,
            self.args.node,
            {self.getKeyName(k): v for k, v in self.args.fields},
            self.profile,
            callback=self.psNodeConfigurationSetCb,
            errback=self.psNodeConfigurationSetEb,
        )


class NodeAffiliationsGet(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "get",
            use_output=C.OUTPUT_DICT,
            use_pubsub=True,
            pubsub_flags={C.NODE},
            help=_(u"retrieve node affiliations (for node owner)"),
        )
        self.need_loop = True

    def add_parser_options(self):
        pass

    def psNodeAffiliationsGetCb(self, affiliations):
        self.output(affiliations)
        self.host.quit()

    def psNodeAffiliationsGetEb(self, failure_):
        self.disp(
            u"can't get node affiliations: {reason}".format(reason=failure_), error=True
        )
        self.host.quit(C.EXIT_BRIDGE_ERRBACK)

    def start(self):
        self.host.bridge.psNodeAffiliationsGet(
            self.args.service,
            self.args.node,
            self.profile,
            callback=self.psNodeAffiliationsGetCb,
            errback=self.psNodeAffiliationsGetEb,
        )


class NodeAffiliationsSet(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "set",
            use_pubsub=True,
            pubsub_flags={C.NODE},
            use_verbose=True,
            help=_(u"set affiliations (for node owner)"),
        )
        self.need_loop = True

    def add_parser_options(self):
        # XXX: we use optional argument syntax for a required one because list of list of 2 elements
        #      (uses to construct dicts) don't work with positional arguments
        self.parser.add_argument(
            "-a",
            "--affiliation",
            dest="affiliations",
            metavar=("JID", "AFFILIATION"),
            required=True,
            type=base.unicode_decoder,
            action="append",
            nargs=2,
            help=_(u"entity/affiliation couple(s)"),
        )

    def psNodeAffiliationsSetCb(self):
        self.disp(_(u"affiliations have been set"), 1)
        self.host.quit()

    def psNodeAffiliationsSetEb(self, failure_):
        self.disp(
            u"can't set node affiliations: {reason}".format(reason=failure_), error=True
        )
        self.host.quit(C.EXIT_BRIDGE_ERRBACK)

    def start(self):
        affiliations = dict(self.args.affiliations)
        self.host.bridge.psNodeAffiliationsSet(
            self.args.service,
            self.args.node,
            affiliations,
            self.profile,
            callback=self.psNodeAffiliationsSetCb,
            errback=self.psNodeAffiliationsSetEb,
        )


class NodeAffiliations(base.CommandBase):
    subcommands = (NodeAffiliationsGet, NodeAffiliationsSet)

    def __init__(self, host):
        super(NodeAffiliations, self).__init__(
            host,
            "affiliations",
            use_profile=False,
            help=_(u"set or retrieve node affiliations"),
        )


class NodeSubscriptionsGet(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "get",
            use_output=C.OUTPUT_DICT,
            use_pubsub=True,
            pubsub_flags={C.NODE},
            help=_(u"retrieve node subscriptions (for node owner)"),
        )
        self.need_loop = True

    def add_parser_options(self):
        pass

    def psNodeSubscriptionsGetCb(self, subscriptions):
        self.output(subscriptions)
        self.host.quit()

    def psNodeSubscriptionsGetEb(self, failure_):
        self.disp(
            u"can't get node subscriptions: {reason}".format(reason=failure_), error=True
        )
        self.host.quit(C.EXIT_BRIDGE_ERRBACK)

    def start(self):
        self.host.bridge.psNodeSubscriptionsGet(
            self.args.service,
            self.args.node,
            self.profile,
            callback=self.psNodeSubscriptionsGetCb,
            errback=self.psNodeSubscriptionsGetEb,
        )


class StoreSubscriptionAction(argparse.Action):
    """Action which handle subscription parameter for owner

    list is given by pairs: jid and subscription state
    if subscription state is not specified, it default to "subscribed"
    """

    def __call__(self, parser, namespace, values, option_string):
        dest_dict = getattr(namespace, self.dest)
        while values:
            jid_s = values.pop(0)
            try:
                subscription = values.pop(0)
            except IndexError:
                subscription = "subscribed"
            if subscription not in ALLOWED_SUBSCRIPTIONS_OWNER:
                parser.error(
                    _(u"subscription must be one of {}").format(
                        u", ".join(ALLOWED_SUBSCRIPTIONS_OWNER)
                    )
                )
            dest_dict[jid_s] = subscription


class NodeSubscriptionsSet(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "set",
            use_pubsub=True,
            pubsub_flags={C.NODE},
            use_verbose=True,
            help=_(u"set/modify subscriptions (for node owner)"),
        )
        self.need_loop = True

    def add_parser_options(self):
        # XXX: we use optional argument syntax for a required one because list of list of 2 elements
        #      (uses to construct dicts) don't work with positional arguments
        self.parser.add_argument(
            "-S",
            "--subscription",
            dest="subscriptions",
            default={},
            nargs="+",
            metavar=("JID [SUSBSCRIPTION]"),
            required=True,
            type=base.unicode_decoder,
            action=StoreSubscriptionAction,
            help=_(u"entity/subscription couple(s)"),
        )

    def psNodeSubscriptionsSetCb(self):
        self.disp(_(u"subscriptions have been set"), 1)
        self.host.quit()

    def psNodeSubscriptionsSetEb(self, failure_):
        self.disp(
            u"can't set node subscriptions: {reason}".format(reason=failure_), error=True
        )
        self.host.quit(C.EXIT_BRIDGE_ERRBACK)

    def start(self):
        self.host.bridge.psNodeSubscriptionsSet(
            self.args.service,
            self.args.node,
            self.args.subscriptions,
            self.profile,
            callback=self.psNodeSubscriptionsSetCb,
            errback=self.psNodeSubscriptionsSetEb,
        )


class NodeSubscriptions(base.CommandBase):
    subcommands = (NodeSubscriptionsGet, NodeSubscriptionsSet)

    def __init__(self, host):
        super(NodeSubscriptions, self).__init__(
            host,
            "subscriptions",
            use_profile=False,
            help=_(u"get or modify node subscriptions"),
        )


class NodeSchemaSet(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "set",
            use_pubsub=True,
            pubsub_flags={C.NODE},
            use_verbose=True,
            help=_(u"set/replace a schema"),
        )
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument("schema", help=_(u"schema to set (must be XML)"))

    def psSchemaSetCb(self):
        self.disp(_(u"schema has been set"), 1)
        self.host.quit()

    def start(self):
        self.host.bridge.psSchemaSet(
            self.args.service,
            self.args.node,
            self.args.schema,
            self.profile,
            callback=self.psSchemaSetCb,
            errback=partial(
                self.errback,
                msg=_(u"can't set schema: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )


class NodeSchemaEdit(base.CommandBase, common.BaseEdit):
    use_items = False

    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "edit",
            use_pubsub=True,
            pubsub_flags={C.NODE},
            use_draft=True,
            use_verbose=True,
            help=_(u"edit a schema"),
        )
        common.BaseEdit.__init__(self, self.host, PUBSUB_SCHEMA_TMP_DIR)
        self.need_loop = True

    def add_parser_options(self):
        pass

    def psSchemaSetCb(self):
        self.disp(_(u"schema has been set"), 1)
        self.host.quit()

    def publish(self, schema):
        self.host.bridge.psSchemaSet(
            self.args.service,
            self.args.node,
            schema,
            self.profile,
            callback=self.psSchemaSetCb,
            errback=partial(
                self.errback,
                msg=_(u"can't set schema: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )

    def psSchemaGetCb(self, schema):
        try:
            from lxml import etree
        except ImportError:
            self.disp(
                u'lxml module must be installed to use edit, please install it with "pip install lxml"',
                error=True,
            )
            self.host.quit(1)
        content_file_obj, content_file_path = self.getTmpFile()
        schema = schema.strip()
        if schema:
            parser = etree.XMLParser(remove_blank_text=True)
            schema_elt = etree.fromstring(schema, parser)
            content_file_obj.write(
                etree.tostring(schema_elt, encoding="utf-8", pretty_print=True)
            )
            content_file_obj.seek(0)
        self.runEditor("pubsub_schema_editor_args", content_file_path, content_file_obj)

    def start(self):
        self.host.bridge.psSchemaGet(
            self.args.service,
            self.args.node,
            self.profile,
            callback=self.psSchemaGetCb,
            errback=partial(
                self.errback,
                msg=_(u"can't edit schema: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )


class NodeSchemaGet(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "get",
            use_output=C.OUTPUT_XML,
            use_pubsub=True,
            pubsub_flags={C.NODE},
            use_verbose=True,
            help=_(u"get schema"),
        )
        self.need_loop = True

    def add_parser_options(self):
        pass

    def psSchemaGetCb(self, schema):
        if not schema:
            self.disp(_(u"no schema found"), 1)
            self.host.quit(1)
        self.output(schema)
        self.host.quit()

    def start(self):
        self.host.bridge.psSchemaGet(
            self.args.service,
            self.args.node,
            self.profile,
            callback=self.psSchemaGetCb,
            errback=partial(
                self.errback,
                msg=_(u"can't get schema: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )


class NodeSchema(base.CommandBase):
    subcommands = (NodeSchemaSet, NodeSchemaEdit, NodeSchemaGet)

    def __init__(self, host):
        super(NodeSchema, self).__init__(
            host, "schema", use_profile=False, help=_(u"data schema manipulation")
        )


class Node(base.CommandBase):
    subcommands = (
        NodeInfo,
        NodeCreate,
        NodeDelete,
        NodeSet,
        NodeAffiliations,
        NodeSubscriptions,
        NodeSchema,
    )

    def __init__(self, host):
        super(Node, self).__init__(
            host, "node", use_profile=False, help=_("node handling")
        )


class Set(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "set",
            use_pubsub=True,
            pubsub_flags={C.NODE},
            help=_(u"publish a new item or update an existing one"),
        )
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument(
            "item",
            type=base.unicode_decoder,
            nargs="?",
            default=u"",
            help=_(u"id, URL of the item to update, keyword, or nothing for new item"),
        )

    def psItemsSendCb(self, published_id):
        if published_id:
            self.disp(u"Item published at {pub_id}".format(pub_id=published_id))
        else:
            self.disp(u"Item published")
        self.host.quit(C.EXIT_OK)

    def start(self):
        try:
            from lxml import etree
        except ImportError:
            self.disp(
                u'lxml module must be installed to use edit, please install it with "pip install lxml"',
                error=True,
            )
            self.host.quit(1)
        try:
            element = etree.parse(sys.stdin).getroot()
        except Exception as e:
            self.parser.error(
                _(u"Can't parse the payload XML in input: {msg}").format(msg=e)
            )
        if element.tag in ("item", "{http://jabber.org/protocol/pubsub}item"):
            if len(element) > 1:
                self.parser.error(
                    _(u"<item> can only have one child element (the payload)")
                )
            element = element[0]
        payload = etree.tostring(element, encoding="unicode")

        self.host.bridge.psItemSend(
            self.args.service,
            self.args.node,
            payload,
            self.args.item,
            {},
            self.profile,
            callback=self.psItemsSendCb,
            errback=partial(
                self.errback,
                msg=_(u"can't send item: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )


class Get(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "get",
            use_output=C.OUTPUT_LIST_XML,
            use_pubsub=True,
            pubsub_flags={C.NODE, C.MULTI_ITEMS},
            help=_(u"get pubsub item(s)"),
        )
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument(
            "-S",
            "--sub-id",
            type=base.unicode_decoder,
            default=u"",
            help=_(u"subscription id"),
        )
        #  TODO: a key(s) argument to select keys to display
        # TODO: add MAM filters

    def psItemsGetCb(self, ps_result):
        self.output(ps_result[0])
        self.host.quit(C.EXIT_OK)

    def psItemsGetEb(self, failure_):
        self.disp(u"can't get pubsub items: {reason}".format(reason=failure_), error=True)
        self.host.quit(C.EXIT_BRIDGE_ERRBACK)

    def start(self):
        self.host.bridge.psItemsGet(
            self.args.service,
            self.args.node,
            self.args.max,
            self.args.items,
            self.args.sub_id,
            {},
            self.profile,
            callback=self.psItemsGetCb,
            errback=self.psItemsGetEb,
        )


class Delete(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "delete",
            use_pubsub=True,
            pubsub_flags={C.NODE, C.SINGLE_ITEM},
            help=_(u"delete an item"),
        )
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument(
            "-f", "--force", action="store_true", help=_(u"delete without confirmation")
        )
        self.parser.add_argument(
            "-N", "--notify", action="store_true", help=_(u"notify deletion")
        )

    def psItemsDeleteCb(self):
        self.disp(_(u"item {item_id} has been deleted").format(item_id=self.args.item))
        self.host.quit(C.EXIT_OK)

    def start(self):
        if not self.args.item:
            self.parser.error(_(u"You need to specify an item to delete"))
        if not self.args.force:
            message = _(u"Are you sure to delete item {item_id} ?").format(
                item_id=self.args.item
            )
            self.host.confirmOrQuit(message, _(u"item deletion cancelled"))
        self.host.bridge.psRetractItem(
            self.args.service,
            self.args.node,
            self.args.item,
            self.args.notify,
            self.profile,
            callback=self.psItemsDeleteCb,
            errback=partial(
                self.errback,
                msg=_(u"can't delete item: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )


class Edit(base.CommandBase, common.BaseEdit):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "edit",
            use_verbose=True,
            use_pubsub=True,
            pubsub_flags={C.NODE, C.SINGLE_ITEM},
            use_draft=True,
            help=_(u"edit an existing or new pubsub item"),
        )
        common.BaseEdit.__init__(self, self.host, PUBSUB_TMP_DIR)

    def add_parser_options(self):
        pass

    def edit(self, content_file_path, content_file_obj):
        # we launch editor
        self.runEditor("pubsub_editor_args", content_file_path, content_file_obj)

    def publish(self, content):
        published_id = self.host.bridge.psItemSend(
            self.pubsub_service,
            self.pubsub_node,
            content,
            self.pubsub_item or "",
            {},
            self.profile,
        )
        if published_id:
            self.disp(u"Item published at {pub_id}".format(pub_id=published_id))
        else:
            self.disp(u"Item published")

    def getItemData(self, service, node, item):
        try:
            from lxml import etree
        except ImportError:
            self.disp(
                u'lxml module must be installed to use edit, please install it with "pip install lxml"',
                error=True,
            )
            self.host.quit(1)
        items = [item] if item is not None else []
        item_raw = self.host.bridge.psItemsGet(
            service, node, 1, items, "", {}, self.profile
        )[0][0]
        parser = etree.XMLParser(remove_blank_text=True)
        item_elt = etree.fromstring(item_raw, parser)
        item_id = item_elt.get("id")
        try:
            payload = item_elt[0]
        except IndexError:
            self.disp(_(u"Item has not payload"), 1)
            return u""
        return etree.tostring(payload, encoding="unicode", pretty_print=True), item_id

    def start(self):
        self.pubsub_service, self.pubsub_node, self.pubsub_item, content_file_path, content_file_obj = (
            self.getItemPath()
        )
        self.edit(content_file_path, content_file_obj)


class Subscribe(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "subscribe",
            use_pubsub=True,
            pubsub_flags={C.NODE},
            use_verbose=True,
            help=_(u"subscribe to a node"),
        )
        self.need_loop = True

    def add_parser_options(self):
        pass

    def psSubscribeCb(self, sub_id):
        self.disp(_(u"subscription done"), 1)
        if sub_id:
            self.disp(_(u"subscription id: {sub_id}").format(sub_id=sub_id))
        self.host.quit()

    def start(self):
        self.host.bridge.psSubscribe(
            self.args.service,
            self.args.node,
            {},
            self.profile,
            callback=self.psSubscribeCb,
            errback=partial(
                self.errback,
                msg=_(u"can't subscribe to node: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )


class Unsubscribe(base.CommandBase):
    # TODO: voir pourquoi NodeNotFound sur subscribe juste après unsubscribe

    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "unsubscribe",
            use_pubsub=True,
            pubsub_flags={C.NODE},
            use_verbose=True,
            help=_(u"unsubscribe from a node"),
        )
        self.need_loop = True

    def add_parser_options(self):
        pass

    def psUnsubscribeCb(self):
        self.disp(_(u"subscription removed"), 1)
        self.host.quit()

    def start(self):
        self.host.bridge.psUnsubscribe(
            self.args.service,
            self.args.node,
            self.profile,
            callback=self.psUnsubscribeCb,
            errback=partial(
                self.errback,
                msg=_(u"can't unsubscribe from node: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )


class Subscriptions(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "subscriptions",
            use_output=C.OUTPUT_LIST_DICT,
            use_pubsub=True,
            help=_(u"retrieve all subscriptions on a service"),
        )
        self.need_loop = True

    def add_parser_options(self):
        pass

    def psSubscriptionsGetCb(self, subscriptions):
        self.output(subscriptions)
        self.host.quit()

    def start(self):
        self.host.bridge.psSubscriptionsGet(
            self.args.service,
            self.args.node,
            self.profile,
            callback=self.psSubscriptionsGetCb,
            errback=partial(
                self.errback,
                msg=_(u"can't retrieve subscriptions: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )


class Affiliations(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "affiliations",
            use_output=C.OUTPUT_DICT,
            use_pubsub=True,
            help=_(u"retrieve all affiliations on a service"),
        )
        self.need_loop = True

    def add_parser_options(self):
        pass

    def psAffiliationsGetCb(self, affiliations):
        self.output(affiliations)
        self.host.quit()

    def psAffiliationsGetEb(self, failure_):
        self.disp(
            u"can't get node affiliations: {reason}".format(reason=failure_), error=True
        )
        self.host.quit(C.EXIT_BRIDGE_ERRBACK)

    def start(self):
        self.host.bridge.psAffiliationsGet(
            self.args.service,
            self.args.node,
            self.profile,
            callback=self.psAffiliationsGetCb,
            errback=self.psAffiliationsGetEb,
        )


class Search(base.CommandBase):
    """this command to a search without using MAM, i.e. by checking every items if dound by itself, so it may be heavy in resources both for server and client"""

    RE_FLAGS = re.MULTILINE | re.UNICODE
    EXEC_ACTIONS = (u"exec", u"external")

    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "search",
            use_output=C.OUTPUT_XML,
            use_pubsub=True,
            pubsub_flags={C.MULTI_ITEMS, C.NO_MAX},
            use_verbose=True,
            help=_(u"search items corresponding to filters"),
        )
        self.need_loop = True

    @property
    def etree(self):
        """load lxml.etree only if needed"""
        if self._etree is None:
            from lxml import etree

            self._etree = etree
        return self._etree

    def filter_opt(self, value, type_):
        value = base.unicode_decoder(value)
        return (type_, value)

    def filter_flag(self, value, type_):
        value = C.bool(value)
        return (type_, value)

    def add_parser_options(self):
        self.parser.add_argument(
            "-D",
            "--max-depth",
            type=int,
            default=0,
            help=_(
                u"maximum depth of recursion (will search linked nodes if > 0, default: 0)"
            ),
        )
        self.parser.add_argument(
            "-m",
            "--max",
            type=int,
            default=30,
            help=_(
                u"maximum number of items to get per node ({} to get all items, default: 30)".format(
                    C.NO_LIMIT
                )
            ),
        )
        self.parser.add_argument(
            "-N",
            "--namespace",
            action="append",
            nargs=2,
            default=[],
            metavar="NAME NAMESPACE",
            help=_(u"namespace to use for xpath"),
        )

        # filters
        filter_text = partial(self.filter_opt, type_=u"text")
        filter_re = partial(self.filter_opt, type_=u"regex")
        filter_xpath = partial(self.filter_opt, type_=u"xpath")
        filter_python = partial(self.filter_opt, type_=u"python")
        filters = self.parser.add_argument_group(
            _(u"filters"),
            _(u"only items corresponding to following filters will be kept"),
        )
        filters.add_argument(
            "-t",
            "--text",
            action="append",
            dest="filters",
            type=filter_text,
            metavar="TEXT",
            help=_(u"full text filter, item must contain this string (XML included)"),
        )
        filters.add_argument(
            "-r",
            "--regex",
            action="append",
            dest="filters",
            type=filter_re,
            metavar="EXPRESSION",
            help=_(u"like --text but using a regular expression"),
        )
        filters.add_argument(
            "-x",
            "--xpath",
            action="append",
            dest="filters",
            type=filter_xpath,
            metavar="XPATH",
            help=_(u"filter items which has elements matching this xpath"),
        )
        filters.add_argument(
            "-P",
            "--python",
            action="append",
            dest="filters",
            type=filter_python,
            metavar="PYTHON_CODE",
            help=_(
                u'Python expression which much return a bool (True to keep item, False to reject it). "item" is raw text item, "item_xml" is lxml\'s etree.Element'
            ),
        )

        # filters flags
        flag_case = partial(self.filter_flag, type_=u"ignore-case")
        flag_invert = partial(self.filter_flag, type_=u"invert")
        flag_dotall = partial(self.filter_flag, type_=u"dotall")
        flag_matching = partial(self.filter_flag, type_=u"only-matching")
        flags = self.parser.add_argument_group(
            _(u"filters flags"),
            _(u"filters modifiers (change behaviour of following filters)"),
        )
        flags.add_argument(
            "-C",
            "--ignore-case",
            action="append",
            dest="filters",
            type=flag_case,
            const=("ignore-case", True),
            nargs="?",
            metavar="BOOLEAN",
            help=_(u"(don't) ignore case in following filters (default: case sensitive)"),
        )
        flags.add_argument(
            "-I",
            "--invert",
            action="append",
            dest="filters",
            type=flag_invert,
            const=("invert", True),
            nargs="?",
            metavar="BOOLEAN",
            help=_(u"(don't) invert effect of following filters (default: don't invert)"),
        )
        flags.add_argument(
            "-A",
            "--dot-all",
            action="append",
            dest="filters",
            type=flag_dotall,
            const=("dotall", True),
            nargs="?",
            metavar="BOOLEAN",
            help=_(u"(don't) use DOTALL option for regex (default: don't use)"),
        )
        flags.add_argument(
            "-o",
            "--only-matching",
            action="append",
            dest="filters",
            type=flag_matching,
            const=("only-matching", True),
            nargs="?",
            metavar="BOOLEAN",
            help=_(u"keep only the matching part of the item"),
        )

        # action
        self.parser.add_argument(
            "action",
            default="print",
            nargs="?",
            choices=("print", "exec", "external"),
            help=_(u"action to do on found items (default: print)"),
        )
        self.parser.add_argument("command", nargs=argparse.REMAINDER)

    def psItemsGetEb(self, failure_, service, node):
        self.disp(
            u"can't get pubsub items at {service} (node: {node}): {reason}".format(
                service=service, node=node, reason=failure_
            ),
            error=True,
        )
        self.to_get -= 1

    def getItems(self, depth, service, node, items):
        search = partial(self.search, depth=depth)
        errback = partial(self.psItemsGetEb, service=service, node=node)
        self.host.bridge.psItemsGet(
            service,
            node,
            self.args.max,
            items,
            "",
            {},
            self.profile,
            callback=search,
            errback=errback,
        )
        self.to_get += 1

    def _checkPubsubURL(self, match, found_nodes):
        """check that the matched URL is an xmpp: one

        @param found_nodes(list[unicode]): found_nodes
            this list will be filled while xmpp: URIs are discovered
        """
        url = match.group(0)
        if url.startswith(u"xmpp"):
            try:
                url_data = uri.parseXMPPUri(url)
            except ValueError:
                return
            if url_data[u"type"] == u"pubsub":
                found_node = {u"service": url_data[u"path"], u"node": url_data[u"node"]}
                if u"item" in url_data:
                    found_node[u"item"] = url_data[u"item"]
                found_nodes.append(found_node)

    def getSubNodes(self, item, depth):
        """look for pubsub URIs in item, and getItems on the linked nodes"""
        found_nodes = []
        checkURI = partial(self._checkPubsubURL, found_nodes=found_nodes)
        strings.RE_URL.sub(checkURI, item)
        for data in found_nodes:
            self.getItems(
                depth + 1,
                data[u"service"],
                data[u"node"],
                [data[u"item"]] if u"item" in data else [],
            )

    def parseXml(self, item):
        try:
            return self.etree.fromstring(item)
        except self.etree.XMLSyntaxError:
            self.disp(
                _(
                    u"item doesn't looks like XML, you have probably used --only-matching somewhere before and we have no more XML"
                ),
                error=True,
            )
            self.host.quit(C.EXIT_BAD_ARG)

    def filter(self, item):
        """apply filters given on command line

        if only-matching is used, item may be modified
        @return (tuple[bool, unicode]): a tuple with:
            - keep: True if item passed the filters
            - item: it is returned in case of modifications
        """
        ignore_case = False
        invert = False
        dotall = False
        only_matching = False
        item_xml = None
        for type_, value in self.args.filters:
            keep = True

            ## filters

            if type_ == u"text":
                if ignore_case:
                    if value.lower() not in item.lower():
                        keep = False
                else:
                    if value not in item:
                        keep = False
                if keep and only_matching:
                    # doesn't really make sens to keep a fixed string
                    # so we raise an error
                    self.host.disp(
                        _(
                            u"--only-matching used with fixed --text string, are you sure?"
                        ),
                        error=True,
                    )
                    self.host.quit(C.EXIT_BAD_ARG)
            elif type_ == u"regex":
                flags = self.RE_FLAGS
                if ignore_case:
                    flags |= re.IGNORECASE
                if dotall:
                    flags |= re.DOTALL
                match = re.search(value, item, flags)
                keep = match != None
                if keep and only_matching:
                    item = match.group()
                    item_xml = None
            elif type_ == u"xpath":
                if item_xml is None:
                    item_xml = self.parseXml(item)
                try:
                    elts = item_xml.xpath(value, namespaces=self.args.namespace)
                except self.etree.XPathEvalError as e:
                    self.disp(
                        _(u"can't use xpath: {reason}").format(reason=e), error=True
                    )
                    self.host.quit(C.EXIT_BAD_ARG)
                keep = bool(elts)
                if keep and only_matching:
                    item_xml = elts[0]
                    try:
                        item = self.etree.tostring(item_xml, encoding="unicode")
                    except TypeError:
                        # we have a string only, not an element
                        item = unicode(item_xml)
                        item_xml = None
            elif type_ == u"python":
                if item_xml is None:
                    item_xml = self.parseXml(item)
                cmd_ns = {u"item": item, u"item_xml": item_xml}
                try:
                    keep = eval(value, cmd_ns)
                except SyntaxError as e:
                    self.disp(unicode(e), error=True)
                    self.host.quit(C.EXIT_BAD_ARG)

            ## flags

            elif type_ == u"ignore-case":
                ignore_case = value
            elif type_ == u"invert":
                invert = value
                #  we need to continue, else loop would end here
                continue
            elif type_ == u"dotall":
                dotall = value
            elif type_ == u"only-matching":
                only_matching = value
            else:
                raise exceptions.InternalError(
                    _(u"unknown filter type {type}").format(type=type_)
                )

            if invert:
                keep = not keep
            if not keep:
                return False, item

        return True, item

    def doItemAction(self, item, metadata):
        """called when item has been kepts and the action need to be done

        @param item(unicode): accepted item
        """
        action = self.args.action
        if action == u"print" or self.host.verbosity > 0:
            try:
                self.output(item)
            except self.etree.XMLSyntaxError:
                # item is not valid XML, but a string
                # can happen when --only-matching is used
                self.disp(item)
        if action in self.EXEC_ACTIONS:
            item_elt = self.parseXml(item)
            if action == u"exec":
                use = {
                    "service": metadata[u"service"],
                    "node": metadata[u"node"],
                    "item": item_elt.get("id"),
                    "profile": self.profile,
                }
                # we need to send a copy of self.args.command
                # else it would be modified
                parser_args, use_args = arg_tools.get_use_args(
                    self.host, self.args.command, use, verbose=self.host.verbosity > 1
                )
                cmd_args = sys.argv[0:1] + parser_args + use_args
            else:
                cmd_args = self.args.command

            self.disp(
                u"COMMAND: {command}".format(
                    command=u" ".join([arg_tools.escape(a) for a in cmd_args])
                ),
                2,
            )
            if action == u"exec":
                ret = subprocess.call(cmd_args)
            else:
                p = subprocess.Popen(cmd_args, stdin=subprocess.PIPE)
                p.communicate(item.encode("utf-8"))
                ret = p.wait()
            if ret != 0:
                self.disp(
                    A.color(
                        C.A_FAILURE,
                        _(u"executed command failed with exit code {code}").format(
                            code=ret
                        ),
                    )
                )

    def search(self, items_data, depth):
        """callback of getItems

        this method filters items, get sub nodes if needed,
        do the requested action, and exit the command when everything is done
        @param items_data(tuple): result of getItems
        @param depth(int): current depth level
            0 for first node, 1 for first children, and so on
        """
        items, metadata = items_data
        for item in items:
            if depth < self.args.max_depth:
                self.getSubNodes(item, depth)
            keep, item = self.filter(item)
            if not keep:
                continue
            self.doItemAction(item, metadata)

        #  we check if we got all getItems results
        self.to_get -= 1
        if self.to_get == 0:
            # yes, we can quit
            self.host.quit()
        assert self.to_get > 0

    def start(self):
        if self.args.command:
            if self.args.action not in self.EXEC_ACTIONS:
                self.parser.error(
                    _(u"Command can only be used with {actions} actions").format(
                        actions=u", ".join(self.EXEC_ACTIONS)
                    )
                )
        else:
            if self.args.action in self.EXEC_ACTIONS:
                self.parser.error(_(u"you need to specify a command to execute"))
        if not self.args.node:
            # TODO: handle get service affiliations when node is not set
            self.parser.error(_(u"empty node is not handled yet"))
        # to_get is increased on each get and decreased on each answer
        # when it reach 0 again, the command is finished
        self.to_get = 0
        self._etree = None
        if self.args.filters is None:
            self.args.filters = []
        self.args.namespace = dict(
            self.args.namespace + [("pubsub", "http://jabber.org/protocol/pubsub")]
        )
        self.getItems(0, self.args.service, self.args.node, self.args.items)


class Uri(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "uri",
            use_profile=False,
            use_pubsub=True,
            pubsub_flags={C.NODE, C.SINGLE_ITEM},
            help=_(u"build URI"),
        )
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument(
            "-p",
            "--profile",
            type=base.unicode_decoder,
            default=C.PROF_KEY_DEFAULT,
            help=_(u"profile (used when no server is specified)"),
        )

    def display_uri(self, jid_):
        uri_args = {}
        if not self.args.service:
            self.args.service = jid.JID(jid_).bare

        for key in ("node", "service", "item"):
            value = getattr(self.args, key)
            if key == "service":
                key = "path"
            if value:
                uri_args[key] = value
        self.disp(uri.buildXMPPUri(u"pubsub", **uri_args))
        self.host.quit()

    def start(self):
        if not self.args.service:
            self.host.bridge.asyncGetParamA(
                u"JabberID",
                u"Connection",
                profile_key=self.args.profile,
                callback=self.display_uri,
                errback=partial(
                    self.errback,
                    msg=_(u"can't retrieve jid: {}"),
                    exit_code=C.EXIT_BRIDGE_ERRBACK,
                ),
            )
        else:
            self.display_uri(None)


class HookCreate(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "create",
            use_pubsub=True,
            pubsub_flags={C.NODE},
            help=_(u"create a Pubsub hook"),
        )
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument(
            "-t",
            "--type",
            default=u"python",
            choices=("python", "python_file", "python_code"),
            help=_(u"hook type"),
        )
        self.parser.add_argument(
            "-P",
            "--persistent",
            action="store_true",
            help=_(u"make hook persistent across restarts"),
        )
        self.parser.add_argument(
            "hook_arg",
            type=base.unicode_decoder,
            help=_(u"argument of the hook (depend of the type)"),
        )

    @staticmethod
    def checkArgs(self):
        if self.args.type == u"python_file":
            self.args.hook_arg = os.path.abspath(self.args.hook_arg)
            if not os.path.isfile(self.args.hook_arg):
                self.parser.error(
                    _(u"{path} is not a file").format(path=self.args.hook_arg)
                )

    def start(self):
        self.checkArgs(self)
        self.host.bridge.psHookAdd(
            self.args.service,
            self.args.node,
            self.args.type,
            self.args.hook_arg,
            self.args.persistent,
            self.profile,
            callback=self.host.quit,
            errback=partial(
                self.errback,
                msg=_(u"can't create hook: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )


class HookDelete(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "delete",
            use_pubsub=True,
            pubsub_flags={C.NODE},
            help=_(u"delete a Pubsub hook"),
        )
        self.need_loop = True

    def add_parser_options(self):
        self.parser.add_argument(
            "-t",
            "--type",
            default=u"",
            choices=("", "python", "python_file", "python_code"),
            help=_(u"hook type to remove, empty to remove all (default: remove all)"),
        )
        self.parser.add_argument(
            "-a",
            "--arg",
            dest="hook_arg",
            type=base.unicode_decoder,
            default=u"",
            help=_(
                u"argument of the hook to remove, empty to remove all (default: remove all)"
            ),
        )

    def psHookRemoveCb(self, nb_deleted):
        self.disp(
            _(u"{nb_deleted} hook(s) have been deleted").format(nb_deleted=nb_deleted)
        )
        self.host.quit()

    def start(self):
        HookCreate.checkArgs(self)
        self.host.bridge.psHookRemove(
            self.args.service,
            self.args.node,
            self.args.type,
            self.args.hook_arg,
            self.profile,
            callback=self.psHookRemoveCb,
            errback=partial(
                self.errback,
                msg=_(u"can't delete hook: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )


class HookList(base.CommandBase):
    def __init__(self, host):
        base.CommandBase.__init__(
            self,
            host,
            "list",
            use_output=C.OUTPUT_LIST_DICT,
            help=_(u"list hooks of a profile"),
        )
        self.need_loop = True

    def add_parser_options(self):
        pass

    def psHookListCb(self, data):
        if not data:
            self.disp(_(u"No hook found."))
        self.output(data)
        self.host.quit()

    def start(self):
        self.host.bridge.psHookList(
            self.profile,
            callback=self.psHookListCb,
            errback=partial(
                self.errback,
                msg=_(u"can't list hooks: {}"),
                exit_code=C.EXIT_BRIDGE_ERRBACK,
            ),
        )


class Hook(base.CommandBase):
    subcommands = (HookCreate, HookDelete, HookList)

    def __init__(self, host):
        super(Hook, self).__init__(
            host,
            "hook",
            use_profile=False,
            use_verbose=True,
            help=_("trigger action on Pubsub notifications"),
        )


class Pubsub(base.CommandBase):
    subcommands = (
        Set,
        Get,
        Delete,
        Edit,
        Subscribe,
        Unsubscribe,
        Subscriptions,
        Node,
        Affiliations,
        Search,
        Hook,
        Uri,
    )

    def __init__(self, host):
        super(Pubsub, self).__init__(
            host, "pubsub", use_profile=False, help=_("PubSub nodes/items management")
        )
