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

""" template generation """

from sat.core.constants import Const as C
from sat.core.i18n import _
from sat.core import exceptions
from sat.tools.common import date_utils
from sat.core.log import getLogger

log = getLogger(__name__)
import os.path
from xml.sax.saxutils import quoteattr
import time
import re
from babel import support
from babel import Locale
from babel.core import UnknownLocaleError
import pygments
from pygments import lexers
from pygments import formatters

try:
    import sat_templates
except ImportError:
    raise exceptions.MissingModule(
        u"sat_templates module is not available, please install it or check your path to use template engine"
    )
else:
    sat_templates  # to avoid pyflakes warning

try:
    import jinja2
except:
    raise exceptions.MissingModule(
        u"Missing module jinja2, please install it from http://jinja.pocoo.org or with pip install jinja2"
    )

from jinja2 import Markup as safe
from jinja2 import is_undefined
from lxml import etree

HTML_EXT = ("html", "xhtml")
RE_ATTR_ESCAPE = re.compile(r"[^a-z_-]")
#  TODO: handle external path (an additional search path for templates should be settable by user
# TODO: handle absolute URL (should be used for trusted use cases) only (e.g. jp) for security reason


class TemplateLoader(jinja2.FileSystemLoader):
    def __init__(self):
        searchpath = os.path.dirname(sat_templates.__file__)
        super(TemplateLoader, self).__init__(searchpath, followlinks=True)

    def parse_template(self, template):
        """parse template path and return theme and relative URL

        @param template_path(unicode): path to template with parenthesis syntax
        @return (tuple[(unicode,None),unicode]): theme and template_path
            theme can be None if relative path is used
            relative path is the path from search path with theme specified
            e.g. default/blog/articles.html
        """
        if template.startswith(u"("):
            try:
                theme_end = template.index(u")")
            except IndexError:
                raise ValueError(u"incorrect theme in template")
            theme = template[1:theme_end]
            template = template[theme_end + 1 :]
            if not template or template.startswith(u"/"):
                raise ValueError(u"incorrect path after template name")
            template = os.path.join(theme, template)
        elif template.startswith(u"/"):
            # absolute path means no template
            theme = None
            raise NotImplementedError(u"absolute path is not implemented yet")
        else:
            theme = C.TEMPLATE_THEME_DEFAULT
            template = os.path.join(theme, template)
        return theme, template

    def get_default_template(self, theme, template_path):
        """return default template path

        @param theme(unicode): theme used
        @param template_path(unicode): path to the not found template
        @return (unicode, None): default path or None if there is not
        """
        ext = os.path.splitext(template_path)[1][1:]
        path_elems = template_path.split(u"/")
        if ext in HTML_EXT:
            if path_elems[1] == u"error":
                # if an inexisting error page is requested, we return base page
                default_path = os.path.join(theme, u"error/base.html")
                return default_path
        if theme != C.TEMPLATE_THEME_DEFAULT:
            # if template doesn't exists for this theme, we try with default
            return os.path.join(C.TEMPLATE_THEME_DEFAULT, path_elems[1:])

    def get_source(self, environment, template):
        """relative path to template dir, with special theme handling

        if the path is just relative, "default" theme is used.
        The theme can be specified in parenthesis just before the path
        e.g.: (some_theme)path/to/template.html
        """
        theme, template_path = self.parse_template(template)
        try:
            return super(TemplateLoader, self).get_source(environment, template_path)
        except jinja2.exceptions.TemplateNotFound as e:
            # in some special cases, a defaut template is returned if nothing is found
            if theme is not None:
                default_path = self.get_default_template(theme, template_path)
                if default_path is not None:
                    return super(TemplateLoader, self).get_source(
                        environment, default_path
                    )
            # if no default template is found, we re-raise the error
            raise e


class Indexer(object):
    """Index global to a page"""

    def __init__(self):
        self._indexes = {}

    def next(self, value):
        if value not in self._indexes:
            self._indexes[value] = 0
            return 0
        self._indexes[value] += 1
        return self._indexes[value]

    def current(self, value):
        return self._indexes.get(value)


class ScriptsHandler(object):
    def __init__(self, renderer, template_path, template_root_dir, root_path):
        self.renderer = renderer
        self.template_root_dir = template_root_dir
        self.root_path = root_path
        self.scripts = []  #  we don't use a set because order may be important
        dummy, self.theme, self.is_default_theme = renderer.getThemeData(template_path)

    def include(self, library_name, attribute="defer"):
        """Mark that a script need to be imported.

        Must be used before base.html is extended, as <script> are generated there.
        If called several time with the same library, it will be imported once.
        @param library_name(unicode): name of the library to import
        @param loading:
        """
        if attribute not in ("defer", "async", ""):
            raise exceptions.DataError(
                _(u'Invalid attribute, please use one of "defer", "async" or ""')
            )
        if library_name.endswith(".js"):
            library_name = library_name[:-3]
        if library_name not in self.scripts:
            self.scripts.append((library_name, attribute))
        return u""

    def generate_scripts(self):
        """Generate the <script> elements

        @return (unicode): <scripts> HTML tags
        """
        scripts = []
        tpl = u"<script src={src} {attribute}></script>"
        for library, attribute in self.scripts:
            path = self.renderer.getStaticPath(
                library, self.template_root_dir, self.theme, self.is_default_theme, ".js"
            )
            if path is None:
                log.warning(_(u"Can't find {}.js javascript library").format(library))
                continue
            path = os.path.join(self.root_path, path)
            scripts.append(tpl.format(src=quoteattr(path), attribute=attribute))
        return safe(u"\n".join(scripts))


class Renderer(object):
    def __init__(self, host):
        self.host = host
        self.base_dir = os.path.dirname(
            sat_templates.__file__
        )  # FIXME: should be modified if we handle use extra dirs
        self.env = jinja2.Environment(
            loader=TemplateLoader(),
            autoescape=jinja2.select_autoescape(["html", "xhtml", "xml"]),
            trim_blocks=True,
            lstrip_blocks=True,
            extensions=["jinja2.ext.i18n"],
        )
        self._locale_str = C.DEFAULT_LOCALE
        self._locale = Locale.parse(self._locale_str)
        self.installTranslations()
        # we want to have access to SàT constants in templates
        self.env.globals[u"C"] = C
        # custom filters
        self.env.filters["next_gidx"] = self._next_gidx
        self.env.filters["cur_gidx"] = self._cur_gidx
        self.env.filters["date_fmt"] = self._date_fmt
        self.env.filters["xmlui_class"] = self._xmlui_class
        self.env.filters["attr_escape"] = self.attr_escape
        self.env.filters["item_filter"] = self._item_filter
        self.env.filters["adv_format"] = self._adv_format
        self.env.filters["dict_ext"] = self._dict_ext
        self.env.filters["highlight"] = self.highlight
        # custom tests
        self.env.tests["in_the_past"] = self._in_the_past
        self.icons_path = os.path.join(host.media_dir, u"fonts/fontello/svg")

    def installTranslations(self):
        i18n_dir = os.path.join(self.base_dir, "i18n")
        self.translations = {}
        for lang_dir in os.listdir(i18n_dir):
            lang_path = os.path.join(i18n_dir, lang_dir)
            if not os.path.isdir(lang_path):
                continue
            po_path = os.path.join(lang_path, "LC_MESSAGES/sat.mo")
            try:
                with open(po_path, "rb") as f:
                    self.translations[Locale.parse(lang_dir)] = support.Translations(
                        f, "sat"
                    )
            except EnvironmentError:
                log.error(
                    _(u"Can't find template translation at {path}").format(path=po_path)
                )
            except UnknownLocaleError as e:
                log.error(_(u"Invalid locale name: {msg}").format(msg=e))
            else:
                log.info(_(u"loaded {lang} templates translations").format(lang=lang_dir))
        self.env.install_null_translations(True)

    def setLocale(self, locale_str):
        """set current locale

        change current translation locale and self self._locale and self._locale_str
        """
        if locale_str == self._locale_str:
            return
        if locale_str == "en":
            # we default to GB English when it's not specified
            # one of the main reason is to avoid the nonsense U.S. short date format
            locale_str = "en_GB"
        try:
            locale = Locale.parse(locale_str)
        except ValueError as e:
            log.warning(_(u"invalid locale value: {msg}").format(msg=e))
            locale_str = self._locale_str = C.DEFAULT_LOCALE
            locale = Locale.parse(locale_str)

        locale_str = unicode(locale)
        if locale_str != C.DEFAULT_LOCALE:
            try:
                translations = self.translations[locale]
            except KeyError:
                log.warning(_(u"Can't find locale {locale}".format(locale=locale)))
                locale_str = C.DEFAULT_LOCALE
                locale = Locale.parse(self._locale_str)
            else:
                self.env.install_gettext_translations(translations, True)
                log.debug(_(u"Switched to {lang}").format(lang=locale.english_name))

        if locale_str == C.DEFAULT_LOCALE:
            self.env.install_null_translations(True)

        self._locale = locale
        self._locale_str = locale_str

    def getThemeAndRoot(self, template):
        """retrieve theme and root dir of a given tempalte

        @param template(unicode): template to parse
        @return (tuple[unicode, unicode]): theme and absolute path to theme's root dir
        """
        theme, dummy = self.env.loader.parse_template(template)
        return theme, os.path.join(self.base_dir, theme)

    def getStaticPath(self, name, template_root_dir, theme, is_default, ext=".css"):
        """retrieve path of a static file if it exists with current theme or default

        File will be looked at [theme]/static/[name][ext], and then default
        if not found.
        @param name(unicode): name of the file to look for
        @param template_root_dir(unicode): absolute path to template root used
        @param theme(unicode): name of the template theme used
        @param is_default(bool): True if theme is the default theme
        @return (unicode, None): relative path if found, else None
        """
        file_ = None
        path = os.path.join(theme, C.TEMPLATE_STATIC_DIR, name + ext)
        if os.path.exists(os.path.join(template_root_dir, path)):
            file_ = path
        elif not is_default:
            path = os.path.join(
                C.TEMPLATE_THEME_DEFAULT, C.TEMPLATE_STATIC_DIR, name + ext
            )
            if os.path.exists(os.path.join(template_root_dir, path)):
                file_.append(path)
        return file_

    def getThemeData(self, template_path):
        """return template data got from template_path

        @return tuple(unicode, unicode, bool):
            path_elems: elements of the path
            theme: theme of the page
            is_default: True if the theme is the default theme
        """
        path_elems = [os.path.splitext(p)[0] for p in template_path.split(u"/")]
        theme = path_elems.pop(0)
        is_default = theme == C.TEMPLATE_THEME_DEFAULT
        return (path_elems, theme, is_default)

    def getCSSFiles(self, template_path, template_root_dir):
        """retrieve CSS files to use according to theme and template path

        for each element of the path, a .css file is looked for in /static, and returned if it exists.
        previous element are kept by replacing '/' with '_', and styles.css is always returned.
        For instance, if template_path is some_theme/blog/articles.html:
            some_theme/static/styles.css is returned if it exists else default/static/styles.css
            some_theme/static/blog.css is returned if it exists else default/static/blog.css (if it exists too)
            some_theme/static/blog_articles.css is returned if it exists else default/static/blog_articles.css (if it exists too)
        @param template_path(unicode): relative path to template file (e.g. some_theme/blog/articles.html)
        @param template_root_dir(unicode): absolute path of the theme root dir used
        @return list[unicode]: relative path to CSS files to use
        """
        # TODO: some caching would be nice
        css_files = []
        path_elems, theme, is_default = self.getThemeData(template_path)
        for css in (u"fonts", u"styles"):
            css_path = self.getStaticPath(css, template_root_dir, theme, is_default)
            if css_path is not None:
                css_files.append(css_path)

        for idx, path in enumerate(path_elems):
            css_path = self.getStaticPath(
                u"_".join(path_elems[: idx + 1]), template_root_dir, theme, is_default
            )
            if css_path is not None:
                css_files.append(css_path)

        return css_files

    ## custom filters ##

    @jinja2.contextfilter
    def _next_gidx(self, ctx, value):
        """Use next current global index as suffix"""
        next_ = ctx["gidx"].next(value)
        return value if next_ == 0 else u"{}_{}".format(value, next_)

    @jinja2.contextfilter
    def _cur_gidx(self, ctx, value):
        """Use current current global index as suffix"""
        current = ctx["gidx"].current(value)
        return value if not current else u"{}_{}".format(value, current)

    def _date_fmt(
        self, timestamp, fmt="short", date_only=False, auto_limit=None, auto_old_fmt=None
    ):
        if is_undefined(fmt):
            fmt = u"short"

        try:
            return date_utils.date_fmt(
                timestamp, fmt, date_only, auto_limit, auto_old_fmt
            )
        except Exception as e:
            log.warning(_(u"Can't parse date: {msg}").format(msg=e))
            return timestamp

    def attr_escape(self, text):
        """escape a text to a value usable as an attribute

        remove spaces, and put in lower case
        """
        return RE_ATTR_ESCAPE.sub(u"_", text.strip().lower())[:50]

    def _xmlui_class(self, xmlui_item, fields):
        """return classes computed from XMLUI fields name

        will return a string with a series of escaped {name}_{value} separated by spaces.
        @param xmlui_item(xmlui.XMLUIPanel): XMLUI containing the widgets to use
        @param fields(iterable(unicode)): names of the widgets to use
        @return (unicode, None): computer string to use as class attribute value
            None if no field was specified
        """
        classes = []
        for name in fields:
            escaped_name = self.attr_escape(name)
            try:
                for value in xmlui_item.widgets[name].values:
                    classes.append(escaped_name + "_" + self.attr_escape(value))
            except KeyError:
                log.debug(
                    _(u'ignoring field "{name}": it doesn\'t exists').format(name=name)
                )
                continue
        return u" ".join(classes) or None

    @jinja2.contextfilter
    def _item_filter(self, ctx, item, filters):
        """return item's value, filtered if suitable

        @param item(object): item to filter
            value must have name and value attributes,
            mostly used for XMLUI items
        @param filters(dict[unicode, (callable, dict, None)]): map of name => filter
            if filter is None, return the value unchanged
            if filter is a callable, apply it
            if filter is a dict, it can have following keys:
                - filters: iterable of filters to apply
                - filters_args: kwargs of filters in the same order as filters (use empty dict if needed)
                - template: template to format where {value} is the filtered value
        """
        value = item.value
        filter_ = filters.get(item.name, None)
        if filter_ is None:
            return value
        elif isinstance(filter_, dict):
            filters_args = filter_.get(u"filters_args")
            for idx, f_name in enumerate(filter_.get(u"filters", [])):
                kwargs = filters_args[idx] if filters_args is not None else {}
                filter_func = self.env.filters[f_name]
                try:
                    eval_context_filter = filter_func.evalcontextfilter
                except AttributeError:
                    eval_context_filter = False

                if eval_context_filter:
                    value = filter_func(ctx.eval_ctx, value, **kwargs)
                else:
                    value = filter_func(value, **kwargs)
            template = filter_.get(u"template")
            if template:
                # format will return a string, so we need to check first
                # if the value is safe or not, and re-mark it after formatting
                is_safe = isinstance(value, safe)
                value = template.format(value=value)
                if is_safe:
                    value = safe(value)
            return value

    def _adv_format(self, value, template, **kwargs):
        """Advancer formatter

        like format() method, but take care or special values like None
        @param value(unicode): value to format
        @param template(None, unicode): template to use with format() method.
            It will be formatted using value=value and **kwargs
            None to return value unchanged
        @return (unicode): formatted value
        """
        if template is None:
            return value
        #  jinja use string when no special char is used, so we have to convert to unicode
        return unicode(template).format(value=value, **kwargs)

    def _dict_ext(self, source_dict, extra_dict, key=None):
        """extend source_dict with extra dict and return the result

        @param source_dict(dict): dictionary to extend
        @param extra_dict(dict, None): dictionary to use to extend first one
            None to return source_dict unmodified
        @param key(unicode, None): if specified extra_dict[key] will be used
            if it doesn't exists, a copy of unmodified source_dict is returned
        @return (dict): resulting dictionary
        """
        if extra_dict is None:
            return source_dict
        if key is not None:
            extra_dict = extra_dict.get(key, {})
        ret = source_dict.copy()
        ret.update(extra_dict)
        return ret

    def highlight(self, code, lexer_name=None, lexer_opts=None, html_fmt_opts=None):
        """Do syntax highlighting on code

        under the hood, pygments is used, check its documentation for options possible values
        @param code(unicode): code or markup to highlight
        @param lexer_name(unicode, None): name of the lexer to use
            None to autodetect it
        @param html_fmt_opts(dict, None): kword arguments to use for HtmlFormatter
        @return (unicode): HTML markup with highlight classes
        """
        if lexer_opts is None:
            lexer_opts = {}
        if html_fmt_opts is None:
            html_fmt_opts = {}
        if lexer_name is None:
            lexer = lexers.guess_lexer(code, **lexer_opts)
        else:
            lexer = lexers.get_lexer_by_name(lexer_name, **lexer_opts)
        formatter = formatters.HtmlFormatter(**html_fmt_opts)
        return safe(pygments.highlight(code, lexer, formatter))

    ## custom tests ##

    def _in_the_past(self, timestamp):
        """check if a date is in the past

        @param timestamp(unicode, int): unix time
        @return (bool): True if date is in the past
        """
        return time.time() > int(timestamp)

    ## template methods ##

    def _icon_defs(self, *names):
        """Define svg icons which will be used in the template, and use their name as id"""
        svg_elt = etree.Element(
            "svg",
            nsmap={None: "http://www.w3.org/2000/svg"},
            width="0",
            height="0",
            style="display: block",
        )
        defs_elt = etree.SubElement(svg_elt, "defs")
        for name in names:
            path = os.path.join(self.icons_path, name + u".svg")
            icon_svg_elt = etree.parse(path).getroot()
            # we use icon name as id, so we can retrieve them easily
            icon_svg_elt.set("id", name)
            if not icon_svg_elt.tag == "{http://www.w3.org/2000/svg}svg":
                raise exceptions.DataError(u"invalid SVG element")
            defs_elt.append(icon_svg_elt)
        return safe(etree.tostring(svg_elt, encoding="unicode"))

    def _icon_use(self, name, cls=""):
        return safe(
            u"""<svg class="svg-icon{cls}" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">
          <use href="#{name}"/>
        </svg>
        """.format(
                name=name, cls=(" " + cls) if cls else ""
            )
        )

    def render(
        self,
        template,
        theme=None,
        locale=C.DEFAULT_LOCALE,
        root_path=u"",
        media_path=u"",
        css_files=None,
        css_inline=False,
        **kwargs
    ):
        """render a template
.
        @param template(unicode): template to render (e.g. blog/articles.html)
        @param theme(unicode): template theme
        @param root_path(unicode): prefix of the path/URL to use for template root
            must end with a u'/'
        @param media_path(unicode): prefix of the SàT media path/URL to use for template root
            must end with a u'/'
        @param css_files(list[unicode],None): CSS files to used
            CSS files must be in static dir of the template
            use None for automatic selection of CSS files based on template category
            None is recommended. General static/style.css and theme file name will be used.
        @param css_inline(bool): if True, CSS will be embedded in the HTML page
        @param **kwargs: variable to transmit to the template
        """
        if not template:
            raise ValueError(u"template can't be empty")
        if theme is not None:
            # use want to set a theme, we add it to the template path
            if template[0] == u"(":
                raise ValueError(
                    u"you can't specify theme in template path and in argument at the same time"
                )
            elif template[0] == u"/":
                raise ValueError(u"you can't specify theme with absolute paths")
            template = u"(" + theme + u")" + template
        else:
            theme, dummy = self.env.loader.parse_template(template)

        template_source = self.env.get_template(template)
        template_root_dir = os.path.normpath(
            self.base_dir
        )  # FIXME: should be modified if we handle use extra dirs
        #  XXX: template_path may have a different theme as first element than theme if a default page is used
        template_path = template_source.filename[len(template_root_dir) + 1 :]

        if css_files is None:
            css_files = self.getCSSFiles(template_path, template_root_dir)

        kwargs["icon_defs"] = self._icon_defs
        kwargs["icon"] = self._icon_use

        if css_inline:
            css_contents = []
            for css_file in css_files:
                css_file_path = os.path.join(template_root_dir, css_file)
                with open(css_file_path) as f:
                    css_contents.append(f.read())
            if css_contents:
                kwargs["css_content"] = "\n".join(css_contents)

        scripts_handler = ScriptsHandler(
            self, template_path, template_root_dir, root_path
        )
        self.setLocale(locale)
        # XXX: theme used in template arguments is the requested theme, which may differ from actual theme
        #      if the template doesn't exist in the requested theme.
        return template_source.render(
            theme=theme,
            root_path=root_path,
            media_path=media_path,
            css_files=css_files,
            locale=self._locale,
            gidx=Indexer(),
            script=scripts_handler,
            **kwargs
        )
