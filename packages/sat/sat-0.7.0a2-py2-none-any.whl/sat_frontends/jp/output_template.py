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
from sat.core.i18n import _
from sat.tools.common import template
import webbrowser
import tempfile
import os.path

__outputs__ = ["Template"]
TEMPLATE = u"template"
OPTIONS = {u"template", u"browser", u"inline-css"}


class Template(object):
    """outputs data using SàT templates"""

    def __init__(self, jp):
        self.host = jp
        jp.register_output(C.OUTPUT_COMPLEX, TEMPLATE, self.render)

    def render(self, data):
        """render output data using requested template

        template to render the data can be either command's TEMPLATE or
        template output_option requested by user.
        @param data(dict): data is a dict which map from variable name to use in template
            to the variable itself.
            command's template_data_mapping attribute will be used if it exists to convert
            data to a dict usable by the template.
        """
        # media_dir is needed for the template
        self.host.media_dir = self.host.bridge.getConfig("", "media_dir")
        cmd = self.host.command
        try:
            template_path = cmd.TEMPLATE
        except AttributeError:
            if not "template" in cmd.args.output_opts:
                self.host.disp(
                    u"no default template set for this command, "
                    u"you need to specify a template using --oo template=[path/to/template.html]",
                    error=True,
                )
                self.host.quit(C.EXIT_BAD_ARG)

        options = self.host.parse_output_options()
        self.host.check_output_options(OPTIONS, options)
        self.renderer = template.Renderer(self.host)
        try:
            template_path = options["template"]
        except KeyError:
            # template is not specified, we use default one
            pass
        if template_path is None:
            self.host.disp(u"Can't parse template, please check its syntax", error=True)
            self.host.quit(C.EXIT_BAD_ARG)

        try:
            mapping_cb = cmd.template_data_mapping
        except AttributeError:
            kwargs = data
        else:
            kwargs = mapping_cb(data)

        css_inline = u"inline-css" in options
        rendered = self.renderer.render(template_path, css_inline=css_inline, **kwargs)

        if "browser" in options:
            template_name = os.path.basename(template_path)
            tmp_dir = tempfile.mkdtemp()
            self.host.disp(
                _(
                    u"Browser opening requested.\nTemporary files are put in the following directory, "
                    u"you'll have to delete it yourself once finished viewing: {}"
                ).format(tmp_dir)
            )
            tmp_file = os.path.join(tmp_dir, template_name)
            with open(tmp_file, "w") as f:
                f.write(rendered.encode("utf-8"))
            theme, theme_root_path = self.renderer.getThemeAndRoot(template_path)
            static_dir = os.path.join(theme_root_path, C.TEMPLATE_STATIC_DIR)
            if os.path.exists(static_dir):
                import shutil

                shutil.copytree(
                    static_dir, os.path.join(tmp_dir, theme, C.TEMPLATE_STATIC_DIR)
                )
            webbrowser.open(tmp_file)
        else:
            self.host.disp(rendered)
