
import logging
log = logging.getLogger(__name__)

import lxml.builder
from bl.dict import Dict

from .element_maker import ElementMaker

class Builder(Dict):
    """create a set of ElementMaker methods all bound to the same object."""
    def __init__(self, default=None, **namespaces):
        Dict.__init__(self)
        if default is not None:
            nsmap = {None:default}
            nsmap.update(**{k:namespaces[k] for k in namespaces.keys() if namespaces[k] != default})
        else:
            nsmap = namespaces
        self.__dict__['nsmap'] = nsmap
        for key in namespaces:        # each namespace gets its own method. named for its key
            self[key] = ElementMaker(namespace=namespaces[key], nsmap=nsmap)
        self._ = ElementMaker(namespace=default, nsmap=nsmap)

    def __call__(self, tag, *args, **kwargs):
        from .xml import XML
        ns = XML.tag_namespace(tag)
        keys = list(self.__dict__['nsmap'].keys())
        values = [self.__dict__['nsmap'][k] for k in keys]
        if ns is not None and ns in values:
            key = keys[values.index(ns)]
            if key is None: key = '_'
        else:
            key = '_'
        name = XML.tag_name(tag)
        e = self[key](name, *args, **kwargs)
        return e

    @classmethod
    def single(C, namespace=None):
        """An element maker with a single namespace that uses that namespace as the default"""
        if namespace is None:
            B = C()._
        else:
            B = C(default=namespace, _=namespace)._
        return B
