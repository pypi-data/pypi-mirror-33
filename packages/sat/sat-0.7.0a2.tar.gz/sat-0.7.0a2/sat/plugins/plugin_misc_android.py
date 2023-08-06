#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# SAT plugin for file tansfer
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

from sat.core.i18n import _, D_
from sat.core.constants import Const as C
from sat.core.log import getLogger

log = getLogger(__name__)
from sat.core import exceptions
import sys
import mmap


PLUGIN_INFO = {
    C.PI_NAME: "Android ",
    C.PI_IMPORT_NAME: "android",
    C.PI_TYPE: C.PLUG_TYPE_MISC,
    C.PI_MAIN: "AndroidPlugin",
    C.PI_HANDLER: "no",
    C.PI_DESCRIPTION: D_(
        """Manage Android platform specificities, like pause or notifications"""
    ),
}

if sys.platform != "android":
    raise exceptions.CancelError(u"this module is not needed on this platform")

from plyer import notification, vibrator

PARAM_VIBRATE_CATEGORY = "Notifications"
PARAM_VIBRATE_NAME = "vibrate"
PARAM_VIBRATE_LABEL = D_(u"Vibrate on notifications")


class AndroidPlugin(object):

    params = """
    <params>
    <individual>
    <category name="{category_name}" label="{category_label}">
        <param name="{param_name}" label="{param_label}" value="true" type="bool" security="0" />
     </category>
    </individual>
    </params>
    """.format(
        category_name=PARAM_VIBRATE_CATEGORY,
        category_label=D_(PARAM_VIBRATE_CATEGORY),
        param_name=PARAM_VIBRATE_NAME,
        param_label=PARAM_VIBRATE_LABEL,
    )

    def __init__(self, host):
        log.info(_("plugin Android initialization"))
        self.host = host
        host.memory.updateParams(self.params)
        self.cagou_status_fd = open(".cagou_status", "rb")
        self.cagou_status = mmap.mmap(
            self.cagou_status_fd.fileno(), 1, prot=mmap.PROT_READ
        )
        # we set a low priority because we want the notification to be sent after all plugins have done their job
        host.trigger.add("MessageReceived", self.messageReceivedTrigger, priority=-1000)

    @property
    def cagou_active(self):
        #  'R' status means Cagou is running in front
        return self.cagou_status[0] == "R"

    def _notifyMessage(self, mess_data, client):
        # send notification if there is a message and it is not a groupchat
        if mess_data["message"] and mess_data["type"] != C.MESS_TYPE_GROUPCHAT:
            message = mess_data["message"].itervalues().next()
            try:
                subject = mess_data["subject"].itervalues().next()
            except StopIteration:
                subject = u"Cagou new message"

            notification.notify(title=subject, message=message)
            if self.host.memory.getParamA(
                PARAM_VIBRATE_NAME, PARAM_VIBRATE_CATEGORY, profile_key=client.profile
            ):
                vibrator.vibrate()
        return mess_data

    def messageReceivedTrigger(self, client, message_elt, post_treat):
        if not self.cagou_active:
            # we only send notification is the frontend is not displayed
            post_treat.addCallback(self._notifyMessage, client)

        return True
