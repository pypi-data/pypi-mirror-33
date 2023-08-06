# -*- coding: utf-8 -*-

import simplejson as json
import lxml
import logging
from lxml import objectify

logger = logging.getLogger(__name__)


class objectJSONEncoder(json.JSONEncoder):
    """A specialized JSON encoder that can handle simple lxml objectify types
    """

    def default(self, o):
        if isinstance(o, lxml.objectify.IntElement):
            return int(o)
        if isinstance(o, lxml.objectify.NumberElement) or \
           isinstance(o, lxml.objectify.FloatElement):
            return float(o)
        if isinstance(o, lxml.objectify.ObjectifiedDataElement):
            return str(o)
        if hasattr(o, '__dict__'):
            return o.__dict__
        return json.JSONEncoder.default(self, o)


def decode_xml(xml_str):
    response = xml_str.replace('encoding="UTF-8"', '')
    try:
        obj = objectify.fromstring(response)
        encoded_obj = objectJSONEncoder().encode(obj)
        return {"type": "json", "data": json.loads(encoded_obj)}
    except Exception as e:
        logger.error(e.args)
        return {"type": "xml", "data": xml_str}
