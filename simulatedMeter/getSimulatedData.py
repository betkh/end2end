import xml.etree.ElementTree as ET
import json
import requests
import os

def getInstantaneousMeterReading(meterReadingId=1):
    """Get meter reading from simulator endpoint and return value and touTier"""
    host_ip = os.getenv('HOST_IP', 'localhost')
    url = f'http://{host_ip}:8082/upt/0/mr/{meterReadingId}/r'
    
    response = requests.get(url, timeout=5)
    xml_data = response.text
    
    # Parse XML
    root = ET.fromstring(xml_data)
    ns = {'ns': 'urn:ieee:std:2030.5:ns'}
    
    # Helper function to extract text from XML element with fallback to default value
    def extractValue(element_name, default='0'):
        elem = root.find(f'ns:{element_name}', ns)
        return elem.text if elem is not None and elem.text is not None else default
    
    # Return both value and touTier
    return float(extractValue('value')), int(extractValue('touTier'))


def getDeviceID():
    """Get device ID from simulator endpoint and return sFDI"""
    host_ip = os.getenv('HOST_IP', 'localhost')
    url = f'http://{host_ip}:8082/sdev'
    
    response = requests.get(url, timeout=5)
    xml_data = response.text
    
    # Parse XML
    root = ET.fromstring(xml_data)
    ns = {'ns': 'urn:ieee:std:2030.5:ns'}
    
    # Helper function to extract text from XML element with fallback to default value
    def extract_sFDI(element_name, default=''):
        elem = root.find(f'ns:{element_name}', ns)
        return elem.text if elem is not None and elem.text is not None else default
    
    # Return just the sFDI value
    return extract_sFDI('sFDI')