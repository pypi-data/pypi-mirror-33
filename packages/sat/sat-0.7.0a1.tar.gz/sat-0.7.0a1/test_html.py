#!/usr/bin/env python2
#-*- encoding: utf-8 -*-


html = u"<p>ceci est un <strong>test</strong> </p>"


from xml.etree import ElementTree as ET

e = ET.fromstring(html)


for elem in e.iter():
    print elem.tag
