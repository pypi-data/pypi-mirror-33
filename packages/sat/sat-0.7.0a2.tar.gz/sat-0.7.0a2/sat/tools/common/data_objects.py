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

"""Objects handling bridge data, with jinja2 safe markup handling"""

from sat.tools.common import data_format

try:
    from jinja2 import Markup as safe
except ImportError:
    safe = unicode

from sat.tools.common import uri as xmpp_uri
import urllib

q = lambda value: urllib.quote(value.encode("utf-8"), safe="@")


class BlogItem(object):
    def __init__(self, mb_data, parent):
        self.mb_data = mb_data
        self.parent = parent
        self._tags = None
        self._groups = None
        self._comments = None
        self._comments_items_list = None

    @property
    def id(self):
        return self.mb_data.get(u"id")

    @property
    def atom_id(self):
        return self.mb_data.get(u"atom_id")

    @property
    def uri(self):
        node = self.parent.node
        service = self.parent.service
        return xmpp_uri.buildXMPPUri(
            u"pubsub", subtype=u"microblog", path=service, node=node, item=self.id
        )

    @property
    def published(self):
        return self.mb_data.get(u"published")

    @property
    def updated(self):
        return self.mb_data.get(u"updated")

    @property
    def language(self):
        return self.mb_data.get(u"language")

    @property
    def author(self):
        return self.mb_data.get(u"author")

    @property
    def author_jid(self):
        return self.mb_data.get(u"author_jid")

    @property
    def author_jid_verified(self):
        return self.mb_data.get(u"author_jid_verified")

    @property
    def author_email(self):
        return self.mb_data.get(u"author_email")

    @property
    def tags(self):
        if self._tags is None:
            self._tags = list(data_format.dict2iter("tag", self.mb_data))
        return self._tags

    @property
    def groups(self):
        if self._groups is None:
            self._groups = list(data_format.dict2iter("group", self.mb_data))
        return self._groups

    @property
    def title(self):
        return self.mb_data.get(u"title")

    @property
    def title_xhtml(self):
        try:
            return safe(self.mb_data[u"title_xhtml"])
        except KeyError:
            return None

    @property
    def content(self):
        return self.mb_data.get(u"content")

    @property
    def content_xhtml(self):
        try:
            return safe(self.mb_data[u"content_xhtml"])
        except KeyError:
            return None

    @property
    def comments(self):
        if self._comments is None:
            self._comments = data_format.dict2iterdict(
                u"comments", self.mb_data, (u"node", u"service")
            )
        return self._comments

    @property
    def comments_service(self):
        return self.mb_data.get(u"comments_service")

    @property
    def comments_node(self):
        return self.mb_data.get(u"comments_node")

    @property
    def comments_items_list(self):
        return [] if self._comments_items_list is None else self._comments_items_list

    def appendCommentsItems(self, items):
        """append comments items to self.comments_items"""
        if self._comments_items_list is None:
            self._comments_items_list = []
        self._comments_items_list.append(items)


class BlogItems(object):
    def __init__(self, mb_data):
        self.items = [BlogItem(i, self) for i in mb_data[0]]
        self.metadata = mb_data[1]

    @property
    def service(self):
        return self.metadata[u"service"]

    @property
    def node(self):
        return self.metadata[u"node"]

    @property
    def uri(self):
        return self.metadata[u"uri"]

    def __len__(self):
        return self.items.__len__()

    def __missing__(self, key):
        return self.items.__missing__(key)

    def __getitem__(self, key):
        return self.items.__getitem__(key)

    def __iter__(self):
        return self.items.__iter__()

    def __reversed__(self):
        return self.items.__reversed__()

    def __contains__(self, item):
        return self.items.__contains__(item)


class Message(object):
    def __init__(self, msg_data):
        self._uid = msg_data[0]
        self._timestamp = msg_data[1]
        self._from_jid = msg_data[2]
        self._to_jid = msg_data[3]
        self._message_data = msg_data[4]
        self._subject_data = msg_data[5]
        self._type = msg_data[6]
        self._extra = msg_data[7]
        self._html = dict(data_format.getSubDict("xhtml", self._extra))

    @property
    def id(self):
        return self._uid

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def from_(self):
        return self._from_jid

    @property
    def text(self):
        try:
            return self._message_data[""]
        except KeyError:
            return next(self._message_data.itervalues())

    @property
    def subject(self):
        try:
            return self._subject_data[""]
        except KeyError:
            return next(self._subject_data.itervalues())

    @property
    def type(self):
        return self._type

    @property
    def thread(self):
        return self._extra.get("thread")

    @property
    def thread_parent(self):
        return self._extra.get("thread_parent")

    @property
    def received(self):
        return self._extra.get("received_timestamp", self._timestamp)

    @property
    def delay_sender(self):
        return self._extra.get("delay_sender")

    @property
    def info_type(self):
        return self._extra.get("info_type")

    @property
    def html(self):
        if not self._html:
            return None
        try:
            return safe(self._html[""])
        except KeyError:
            return safe(next(self._html.itervalues()))


class Messages(object):
    def __init__(self, msgs_data):
        self.messages = [Message(m) for m in msgs_data]

    def __len__(self):
        return self.messages.__len__()

    def __missing__(self, key):
        return self.messages.__missing__(key)

    def __getitem__(self, key):
        return self.messages.__getitem__(key)

    def __iter__(self):
        return self.messages.__iter__()

    def __reversed__(self):
        return self.messages.__reversed__()

    def __contains__(self, item):
        return self.messages.__contains__(item)


class Room(object):
    def __init__(self, jid, name=None, url=None):
        self.jid = jid
        self.name = name or jid
        if url is not None:
            self.url = url


class Identity(object):
    def __init__(self, jid_str, data=None):
        self.jid_str = jid_str
        self.data = data if data is not None else {}

    def __getitem__(self, key):
        return self.data[key]

    def __getattr__(self, key):
        try:
            return self.data[key]
        except KeyError:
            raise AttributeError(key)


class Identities(object):
    def __init__(self):
        self.identities = {}

    def __getitem__(self, jid_str):
        try:
            return self.identities[jid_str]
        except KeyError:
            return None

    def __setitem__(self, jid_str, data):
        self.identities[jid_str] = Identity(jid_str, data)

    def __contains__(self, jid_str):
        return jid_str in self.identities


class ObjectQuoter(object):
    """object wrapper which quote attribues (to be used in templates)"""

    def __init__(self, obj):
        self.obj = obj

    def __unicode__(self):
        return q(self.obj.__unicode__())

    def __str__(self):
        return self.__unicode__()

    def __getattr__(self, name):
        return q(self.obj.__getattr__(name))

    def __getitem__(self, key):
        return q(self.obj.__getitem__(key))


class OnClick(object):
    """Class to handle clickable elements targets"""

    def __init__(self, url=None):
        self.url = url

    def formatUrl(self, *args, **kwargs):
        """format URL using Python formatting

        values will be quoted before being used
        """
        return self.url.format(
            *[q(a) for a in args], **{k: ObjectQuoter(v) for k, v in kwargs.iteritems()}
        )
