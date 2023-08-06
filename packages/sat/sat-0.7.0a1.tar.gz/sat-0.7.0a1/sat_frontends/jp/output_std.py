#! /usr/bin/python
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
"""Standard outputs"""


from sat_frontends.jp.constants import Const as C
from sat.tools.common.ansi import ANSI as A
import json

__outputs__ = ["Simple", "Json"]
SIMPLE = u"simple"
JSON = u"json"
JSON_RAW = u"json_raw"


class Simple(object):
    """Default outputs"""

    def __init__(self, host):
        self.host = host
        host.register_output(C.OUTPUT_TEXT, SIMPLE, self.simple_print)
        host.register_output(C.OUTPUT_LIST, SIMPLE, self.list)
        host.register_output(C.OUTPUT_DICT, SIMPLE, self.dict)
        host.register_output(C.OUTPUT_LIST_DICT, SIMPLE, self.list_dict)
        host.register_output(C.OUTPUT_DICT_DICT, SIMPLE, self.dict_dict)
        host.register_output(C.OUTPUT_COMPLEX, SIMPLE, self.simple_print)

    def simple_print(self, data):
        self.host.disp(unicode(data))

    def list(self, data):
        self.host.disp(u"\n".join(data))

    def dict(self, data, indent=0, header_color=C.A_HEADER):
        options = self.host.parse_output_options()
        self.host.check_output_options({u"no-header"}, options)
        show_header = not u"no-header" in options
        for k, v in data.iteritems():
            if show_header:
                header = A.color(header_color, k) + u": "
            else:
                header = u""

            self.host.disp(
                (
                    u"{indent}{header}{value}".format(
                        indent=indent * u" ", header=header, value=v
                    )
                )
            )

    def list_dict(self, data):
        for idx, datum in enumerate(data):
            if idx:
                self.host.disp(u"\n")
            self.dict(datum)

    def dict_dict(self, data):
        for key, sub_dict in data.iteritems():
            self.host.disp(A.color(C.A_HEADER, key))
            self.dict(sub_dict, indent=4, header_color=C.A_SUBHEADER)


class Json(object):
    """outputs in json format"""

    def __init__(self, host):
        self.host = host
        host.register_output(C.OUTPUT_TEXT, JSON, self.dump)
        host.register_output(C.OUTPUT_LIST, JSON, self.dump_pretty)
        host.register_output(C.OUTPUT_LIST, JSON_RAW, self.dump)
        host.register_output(C.OUTPUT_DICT, JSON, self.dump_pretty)
        host.register_output(C.OUTPUT_DICT, JSON_RAW, self.dump)
        host.register_output(C.OUTPUT_LIST_DICT, JSON, self.dump_pretty)
        host.register_output(C.OUTPUT_LIST_DICT, JSON_RAW, self.dump)
        host.register_output(C.OUTPUT_DICT_DICT, JSON, self.dump_pretty)
        host.register_output(C.OUTPUT_DICT_DICT, JSON_RAW, self.dump)
        host.register_output(C.OUTPUT_COMPLEX, JSON, self.dump_pretty)
        host.register_output(C.OUTPUT_COMPLEX, JSON_RAW, self.dump)

    def dump(self, data):
        self.host.disp(json.dumps(data, default=str))

    def dump_pretty(self, data):
        self.host.disp(json.dumps(data, indent=4, default=str))
