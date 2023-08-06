#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# helper class for making a SAT frontend
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
from sat_frontends.quick_frontend.constants import Const as C


NEW_INSTANCE_SUFF = "_new_instance_"
classes_map = {}


try:
    # FIXME: to be removed when an acceptable solution is here
    unicode("")  # XXX: unicode doesn't exist in pyjamas
except (
    TypeError,
    AttributeError,
):  # Error raised is not the same depending on pyjsbuild options
    unicode = str


def register(base_cls, child_cls=None):
    """Register a child class to use by default when a base class is needed

    @param base_cls: "Quick..." base class (like QuickChat or QuickContact), must inherit from QuickWidget
    @param child_cls: inherited class to use when Quick... class is requested, must inherit from base_cls.
        Can be None if it's the base_cls itself which register
    """
    # FIXME: we use base_cls.__name__ instead of base_cls directly because pyjamas because
    #        in the second case
    classes_map[base_cls.__name__] = child_cls


class WidgetAlreadyExistsError(Exception):
    pass


class QuickWidgetsManager(object):
    """This class is used to manage all the widgets of a frontend
    A widget can be a window, a graphical thing, or someting else depending of the frontend"""

    def __init__(self, host):
        self.host = host
        self._widgets = {}

    def __iter__(self):
        """Iterate throught all widgets"""
        for widget_map in self._widgets.itervalues():
            for widget in widget_map.itervalues():
                yield widget

    def getRealClass(self, class_):
        """Return class registered for given class_

        @param class_: subclass of QuickWidget
        @return: class actually used to create widget
        """
        try:
            # FIXME: we use base_cls.__name__ instead of base_cls directly because pyjamas bugs
            #        in the second case
            cls = classes_map[class_.__name__]
        except KeyError:
            cls = class_
        if cls is None:
            raise exceptions.InternalError(
                "There is not class registered for {}".format(class_)
            )
        return cls

    def getRootHash(self, hash_):
        """Return root hash (i.e. hash without new instance suffix for recreated widgets

        @param hash_(immutable): hash of a widget
        @return (unicode): root hash (transtyped to unicode)
        """
        return unicode(hash_).split(NEW_INSTANCE_SUFF)[0]

    def getWidgets(self, class_, target=None, profiles=None):
        """Get all subclassed widgets instances

        @param class_: subclass of QuickWidget, same parameter as used in [getOrCreateWidget]
        @param target: if not None, construct a hash with this target and filter corresponding widgets
            recreated widgets (with new instance suffix) are handled
        @param profiles(iterable, None): if not None, filter on instances linked to these profiles
        @return: iterator on widgets
        """
        class_ = self.getRealClass(class_)
        try:
            widgets_map = self._widgets[class_.__name__]
        except KeyError:
            return
        else:
            if target is not None:
                filter_hash = unicode(class_.getWidgetHash(target, profiles))
            else:
                filter_hash = None
            for w_hash, w in widgets_map.iteritems():
                if profiles is None or w.profiles.intersection(profiles):
                    if (
                        filter_hash is not None
                        and self.getRootHash(w_hash) != filter_hash
                    ):
                        continue
                    yield w

    def getWidget(self, class_, target=None, profiles=None):
        """Get a widget without creating it if it doesn't exist.

        @param class_(class): class of the widget to create
        @param target: target depending of the widget, usually a JID instance
        @param profiles (unicode, iterable[unicode], None): profile(s) to use (may or may not be
            used, depending of the widget class)
        @return: a class_ instance or None if the widget doesn't exist
        """
        assert (target is not None) or (profiles is not None)
        if profiles is not None and isinstance(profiles, unicode):
            profiles = [profiles]
        class_ = self.getRealClass(class_)
        hash_ = class_.getWidgetHash(target, profiles)
        try:
            return self._widgets[class_.__name__][hash_]
        except KeyError:
            return None

    def getOrCreateWidget(self, class_, target, *args, **kwargs):
        """Get an existing widget or create a new one when necessary

        If the widget is new, self.host.newWidget will be called with it.
        @param class_(class): class of the widget to create
        @param target: target depending of the widget, usually a JID instance
        @param args(list): optional args to create a new instance of class_
        @param kwargs(dict): optional kwargs to create a new instance of class_
            if 'profile' key is present, it will be popped and put in 'profiles'
            if there is neither 'profile' nor 'profiles', None will be used for 'profiles'
            if 'on_new_widget' is present it can have the following values:
                C.WIDGET_NEW [default]: self.host.newWidget will be called on widget creation
                [callable]: this method will be called instead of self.host.newWidget
                None: do nothing
            if 'on_existing_widget' is present it can have the following values:
                C.WIDGET_KEEP  [default]: return the existing widget
                C.WIDGET_RAISE: raise WidgetAlreadyExistsError
                C.WIDGET_RECREATE: create a new widget *WITH A NEW HASH*
                    if the existing widget has a "recreateArgs" method, it will be called with args list and kwargs dict
                    so the values can be completed to create correctly the new instance
                [callable]: this method will be called with existing widget as argument
            if 'force_hash' is present, the hash given in value will be used instead of the one returned by class_.getWidgetHash
            other keys will be used to instanciate class_ if the case happen (e.g. if type_ is present and class_ is a QuickChat subclass,
                it will be used to create a new QuickChat instance).
        @return: a class_ instance, either new or already existing
        """
        cls = self.getRealClass(class_)

        ## arguments management ##
        _args = [self.host, target] + list(
            args
        ) or []  # FIXME: check if it's really necessary to use optional args
        _kwargs = kwargs or {}
        if "profiles" in _kwargs and "profile" in _kwargs:
            raise ValueError(
                "You can't have 'profile' and 'profiles' keys at the same time"
            )
        try:
            _kwargs["profiles"] = [_kwargs.pop("profile")]
        except KeyError:
            if not "profiles" in _kwargs:
                _kwargs["profiles"] = None

        # on_new_widget tell what to do for the new widget creation
        try:
            on_new_widget = _kwargs.pop("on_new_widget")
        except KeyError:
            on_new_widget = C.WIDGET_NEW

        # on_existing_widget tell what to do when the widget already exists
        try:
            on_existing_widget = _kwargs.pop("on_existing_widget")
        except KeyError:
            on_existing_widget = C.WIDGET_KEEP

        ## we get the hash ##
        try:
            hash_ = _kwargs.pop("force_hash")
        except KeyError:
            hash_ = cls.getWidgetHash(target, _kwargs["profiles"])

        ## widget creation or retrieval ##

        widgets_map = self._widgets.setdefault(
            cls.__name__, {}
        )  # we sorts widgets by classes
        if not cls.SINGLE:
            widget = None  # if the class is not SINGLE, we always create a new widget
        else:
            try:
                widget = widgets_map[hash_]
                widget.addTarget(target)
            except KeyError:
                widget = None

        if widget is None:
            # we need to create a new widget
            log.debug(u"Creating new widget for target {} {}".format(target, cls))
            widget = cls(*_args, **_kwargs)
            widgets_map[hash_] = widget

            if on_new_widget == C.WIDGET_NEW:
                self.host.newWidget(widget)
            elif callable(on_new_widget):
                on_new_widget(widget)
            else:
                assert on_new_widget is None
        else:
            # the widget already exists
            if on_existing_widget == C.WIDGET_KEEP:
                pass
            elif on_existing_widget == C.WIDGET_RAISE:
                raise WidgetAlreadyExistsError(hash_)
            elif on_existing_widget == C.WIDGET_RECREATE:
                # we use getOrCreateWidget to recreate the new widget
                # /!\ we use args and kwargs and not _args and _kwargs because we need the original args
                #     we need to get rid of kwargs special options
                new_kwargs = kwargs.copy()
                try:
                    new_kwargs.pop(
                        "force_hash"
                    )  # FIXME: we use pop instead of del here because pyjamas doesn't raise error on del
                except KeyError:
                    pass
                else:
                    raise ValueError(
                        "force_hash option can't be used with on_existing_widget=RECREATE"
                    )

                new_kwargs["on_new_widget"] = on_new_widget

                # XXX: keep up-to-date if new special kwargs are added (i.e.: delete these keys here)
                new_kwargs["on_existing_widget"] = C.WIDGET_RAISE
                try:
                    recreateArgs = widget.recreateArgs
                except AttributeError:
                    pass
                else:
                    recreateArgs(args, new_kwargs)
                hash_idx = 1
                while True:
                    new_kwargs["force_hash"] = "{}{}{}".format(
                        hash_, NEW_INSTANCE_SUFF, hash_idx
                    )
                    try:
                        widget = self.getOrCreateWidget(
                            class_, target, *args, **new_kwargs
                        )
                    except WidgetAlreadyExistsError:
                        hash_idx += 1
                    else:
                        log.debug(
                            u"Widget already exists, a new one has been recreated with hash {}".format(
                                new_kwargs["force_hash"]
                            )
                        )
                        break
            elif callable(on_existing_widget):
                on_existing_widget(widget)
            else:
                raise exceptions.InternalError(
                    "Unexpected on_existing_widget value ({})".format(on_existing_widget)
                )

        return widget

    def deleteWidget(self, widget_to_delete, *args, **kwargs):
        """Delete a widget

        this method must be called by frontends when a widget is deleted
        widget's onDelete method will be called before deletion
        @param widget_to_delete(QuickWidget): widget which need to deleted
        @param *args: extra arguments to pass to onDelete
        @param *kwargs: extra keywords arguments to pass to onDelete
            the extra arguments are not use by QuickFrontend, it's is up to
            the frontend to use them or not
        """
        if widget_to_delete.onDelete(*args, **kwargs) == False:
            return

        if self.host.selected_widget == widget_to_delete:
            self.host.selected_widget = None

        for widget_map in self._widgets.itervalues():
            to_delete = set()
            for hash_, widget in widget_map.iteritems():
                if widget_to_delete is widget:
                    to_delete.add(hash_)
            for hash_ in to_delete:
                del widget_map[hash_]


class QuickWidget(object):
    """generic widget base"""

    SINGLE = True  # if True, there can be only one widget per target(s)
    PROFILES_MULTIPLE = False  # If True, this widget can handle several profiles at once
    PROFILES_ALLOW_NONE = False  # If True, this widget can be used without profile

    def __init__(self, host, target, profiles=None):
        """
        @param host: %(doc_host)s
        @param target: target specific for this widget class
        @param profiles: can be either:
            - (unicode): used when widget class manage a unique profile
            - (iterable): some widget class can manage several profiles, several at once can be specified here
            - None: no profile is managed by this widget class (rare)
        @raise: ValueError when (iterable) or None is given to profiles for a widget class which manage one unique profile.
        """
        self.host = host
        self.targets = set()
        self.addTarget(target)
        self.profiles = set()
        if isinstance(profiles, basestring):
            self.addProfile(profiles)
        elif profiles is None:
            if not self.PROFILES_ALLOW_NONE:
                raise ValueError("profiles can't have a value of None")
        else:
            for profile in profiles:
                self.addProfile(profile)
            if not self.profiles:
                raise ValueError("no profile found, use None for no profile classes")

    @property
    def profile(self):
        assert (
            len(self.profiles) == 1
            and not self.PROFILES_MULTIPLE
            and not self.PROFILES_ALLOW_NONE
        )
        return list(self.profiles)[0]

    def addTarget(self, target):
        """Add a target if it doesn't already exists

        @param target: target to add
        """
        self.targets.add(target)

    def addProfile(self, profile):
        """Add a profile is if doesn't already exists

        @param profile: profile to add
        """
        if self.profiles and not self.PROFILES_MULTIPLE:
            raise ValueError("multiple profiles are not allowed")
        self.profiles.add(profile)

    @staticmethod
    def getWidgetHash(target, profiles):
        """Return the hash associated with this target for this widget class

        some widget classes can manage several target on the same instance
        (e.g.: a chat widget with multiple resources on the same bare jid),
        this method allow to return a hash associated to one or several targets
        to retrieve the good instance. For example, a widget managing JID targets,
        and all resource of the same bare jid would return the bare jid as hash.

        @param target: target to check
        @param profiles: profile(s) associated to target, see __init__ docstring
        @return: a hash (can correspond to one or many targets or profiles, depending of widget class)
        """
        return unicode(target)  # by defaut, there is one hash for one target

    def onDelete(self, *args, **kwargs):
        """Called when a widget is being deleted

        @return (boot, None): False to cancel deletion
            all other value continue deletion
        """
        log.debug(u"widget {} deleted".format(self))
        return True
