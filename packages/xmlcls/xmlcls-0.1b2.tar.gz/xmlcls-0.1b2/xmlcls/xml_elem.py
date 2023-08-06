# -*- coding: utf-8 -*-
"""
Base class for wrappers over XML elements

If class name ends with 'List' then:
    - class must contains '_list_item_class' attribute with class name
    - class constructor returns list of objects with type of '_list_item_class' attribute's value

If 'xpath' attribute is None - the root element will be wrapped else element(s) from xpath value.
"""


class XMLElement:
    """
    Base class for custom XML elements objects

    TODO: explicit element attributes definition and validation
    TODO: use __slots__?
    """

    xpath = None
    _element = None
    _list_item_class = None

    def __new__(cls, xml_element):
        """
        Find XML element in root xml_element and instantiate class

        Args:
            cls: class. If class name ends with 'List' - wil be return list: [cls._list_item_class(), ...]
            xml_element: root xml element to find by passed class xpath

        Returns: list of instances or instance
        """
        is_list = cls.__name__.endswith('List')
        if is_list and cls._list_item_class is None:
            raise Exception('{}._list_item_class is None! Must be child class of XMLElement!'.format(cls))

        element = None
        if cls.xpath is None:
            element = xml_element.get_root()
        elif not is_list:
            element = xml_element.find(cls.xpath)
        elif is_list:
            elements = xml_element.findall(cls.xpath)
            return [cls.instantiate(cls._list_item_class, elm) for elm in elements] if elements is not None else []
        return cls.instantiate(cls, element) if element is not None else cls.instantiate(cls)

    @staticmethod
    def instantiate(cls, element=None) -> object:
        """
        Create instance of class

        Args:
            cls: class
            element: etree.Element
        Returns:
            instance
        """
        obj = super(XMLElement, cls).__new__(cls)

        if element is not None:
            obj._element = element
            obj.__dict__.update(element.attrib)

        return obj

    @property
    def tag(self):
        return self.element.tag if self.element is not None else None

    @property
    def text(self):
        return "{}".format(self.element.text).strip() if self.element is not None else None

    @staticmethod
    def as_text(f) -> callable:
        """
        Decorator
        """
        def wrap(_self):
            xml_elem = f(_self)

            if xml_elem is None:
                return xml_elem

            if isinstance(xml_elem, list):
                return [elem.text for elem in xml_elem]

            return xml_elem.text

        return wrap

    @property
    def element(self):
        return self._element if hasattr(self, '_element') else None

    def get_root(self):
        """ get root etree.Element """
        return self._element.get_root() if self._element is not None else None

    def find(self, xpath: str):
        """ make xpath query for one etree.Element """
        return self._element.find(xpath) if self._element is not None else None

    def findall(self, xpath: str) -> list:
        """ make xpath query for multiple elements """
        return self._element.findall(xpath) if self._element is not None else None

    @property
    def dict(self) -> dict:
        """ get element's attributes as dict """
        dict_ = self.__dict__.copy()
        if '_element' in dict_:
            del dict_['_element']
        return dict_

    def __repr__(self) -> str:
        return '{}: {}'.format(self.tag, self.dict)

    def __bool__(self) -> bool:
        return bool(self.tag)

    def __getitem__(self, key):
        return self.__dict__[key] if key in self.__dict__ else None

    def __setitem__(self, key, val):
        self.__dict__[key] = val

    def __delitem__(self, key):
        if key in self.__dict__:
            del self.__dict__[key]

    def __contains__(self, key):
        return key in self.__dict__

    def __iter__(self):
        return iter(self.__dict__.keys())
