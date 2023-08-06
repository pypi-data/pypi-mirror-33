import os
import xmlschema
import validators
from robot.api import logger
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET


class XsdKeywords(object):
    """
    XsdLibrary is a XSD keyword library that uses to validate XML
    """
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        pass

    @staticmethod
    def xml_should_match_xsd(xml, xsd):
        """ Xml Should Match Xsd: validate xml to xsd
        ``xml`` xml file path, URL path or a string containing the XML data.
        ``xsd`` xsd file path, URL path or a string containing the XML Schemas Definition.
        """
        if validators.url(xsd) is True or os.path.exists(xsd):
            _schema = xmlschema.XMLSchema(xsd)
        else:
            try:
                ET.fromstring(xml)
                _schema = xmlschema.XMLSchema("""{0}""".format(xsd,))
            except:
                logger.error("the xml parameter is invalid")
                raise
        if validators.url(xml) is True or os.path.exists(xml):
            _schema.validate(xml)
        else:
            _schema.validate("""{0}""".format(xml,))
