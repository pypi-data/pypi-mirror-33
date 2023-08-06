# -*- coding: utf-8 -*-
"""
XML file wrapper class on xml.etree
"""


from defusedxml import lxml as etree
from lxml.etree import XMLSchema


class XMLFile:
    """
    XML file wrapper class on xml.etree

    without xsd in constructor:
        XMLFile(your_xml_string)
    with xsd in constructor:
        XMLFile(your_xml_string, your_xsd_string)
    pass xsd to method:
        elm = XMLFile(your_xml_string).is_valid(your_xsd_string) # check elm.error_log if False

    try:
        elm.assert_valid()
    except etree.DocumentInvalid as e:
        print('Invalid xml:', e)
    """
    def __init__(self, xml_str: bytes, xsd_str: bytes=None):
        self.xml_str = xml_str
        self.xsd_str = xsd_str

        self.xml = etree.fromstring(self.xml_str)  # fromstring() returns Element instead parse()'s ElementTree
        self.xsd = None
        if xsd_str:
            self.init_xsd(xsd_str)

    def init_xsd(self, xsd_str):
        """
        Init xsd as XMLSchema

        Raises:
            XMLSchemaParseError
        """
        self.xsd = XMLSchema(
            etree.fromstring(xsd_str)
        )

    def get_root(self):
        """ get root element """
        return self.xml

    def find(self, xpath: str):
        """ make xpath query for one element """
        return self.xml.find(xpath)

    def findall(self, xpath: str) -> list:
        """ make xpath query for multiple elements """
        return self.xml.findall(xpath)

    def is_valid(self, xsd_str: bytes = None) -> bool:
        """ check is valid xml (by xsd_str if passed) """
        return self.check_xsd(xsd_str).validate(self.xml)

    def assert_valid(self, xsd_str: bytes = None) -> None:
        """ check is valid xml (by xsd_str if passed) and raise etree.DocumentInvalid if not """
        self.check_xsd(xsd_str).assertValid(self.xml)

    def check_xsd(self, xsd_str: bytes = None) -> XMLSchema:
        """ check self.xsd isset or try to create with xsd_str """
        if xsd_str:
            self.init_xsd(xsd_str)
        if not self.xsd:
            raise Exception('XMLSchema not found! Pass it by constructor\'s or this method\'s argument - "xsd_str".')

        return self.xsd

    @property
    def error_log(self) -> str:
        """ the log of validation errors and warnings """
        return self.xsd.error_log if self.xsd else ''
