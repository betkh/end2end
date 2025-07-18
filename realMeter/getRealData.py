import xml.etree.ElementTree as ET
import json
import requests
import os
import ssl
from urllib3.util.ssl_ import create_urllib3_context
from requests.adapters import HTTPAdapter
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Constants from legacy code
IEEE_PREFIX = '{urn:ieee:std:2030.5:ns}'
CIPHERS = ('ECDHE')

class CCM8Adapter(HTTPAdapter):
    """
    A TransportAdapter that re-enables ECDHE support in Requests.
    Required for communicating with smart meters using specific cipher suites.
    """
    def init_poolmanager(self, *args, **kwargs):
        kwargs['ssl_context'] = self.create_ssl_context()
        return super(CCM8Adapter, self).init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        kwargs['ssl_context'] = self.create_ssl_context()
        return super(CCM8Adapter, self).proxy_manager_for(*args, **kwargs)

    def create_ssl_context(self):
        ssl_version = ssl.PROTOCOL_TLSv1_2
        context = create_urllib3_context(ssl_version=ssl_version)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_REQUIRED
        context.set_ciphers(CIPHERS)
        return context

def setup_session(cert_path, key_path, meter_ip):
    """
    Creates a new requests session with TLS certificates for secure communication.
    
    Args:
        cert_path (str): Path to the certificate file
        key_path (str): Path to the private key file
        meter_ip (str): IP address of the smart meter
    
    Returns:
        requests.Session: Configured session for TLS communication
    """
    session = requests.Session()
    session.cert = (cert_path, key_path)
    # Mount our adapter to the domain
    session.mount(f'https://{meter_ip}', CCM8Adapter())
    return session

def getInstantaneousMeterReading(meter_ip, meter_port=443, meter_reading_id=1, cert_path=None, key_path=None):
    """
    Get meter reading from real smart meter endpoint and return value and touTier.
    
    Args:
        meter_ip (str): IP address of the smart meter
        meter_port (int): Port number (default 443 for HTTPS)
        meter_reading_id (int): Meter reading ID to query
        cert_path (str): Path to certificate file (default: realMeter/certs/.cert.pem)
        key_path (str): Path to private key file (default: realMeter/certs/.key.pem)
    
    Returns:
        tuple: (value, touTier) - meter reading value and time-of-use tier
    """
    # Set default certificate paths if not provided
    if cert_path is None:
        cert_path = os.path.join('realMeter', 'certs', '.cert.pem')
    if key_path is None:
        key_path = os.path.join('realMeter', 'certs', '.key.pem')
    
    # Verify certificate files exist
    if not os.path.exists(cert_path):
        raise FileNotFoundError(f"Certificate file not found: {cert_path}")
    if not os.path.exists(key_path):
        raise FileNotFoundError(f"Private key file not found: {key_path}")
    
    # Setup secure session
    session = setup_session(cert_path, key_path, meter_ip)
    
    # Construct URL for meter reading endpoint
    url = f'https://{meter_ip}:{meter_port}/upt/0/mr/{meter_reading_id}/r'
    
    try:
        response = session.get(url, verify=False, timeout=15.0)
        response.raise_for_status()
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
        
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to meter at {meter_ip}: {e}")
        return None, None
    except ET.ParseError as e:
        print(f"Error parsing XML response: {e}")
        return None, None

def getDeviceID(meter_ip, meter_port=443, cert_path=None, key_path=None):
    """
    Get device ID from real smart meter endpoint and return sFDI.
    
    Args:
        meter_ip (str): IP address of the smart meter
        meter_port (int): Port number (default 443 for HTTPS)
        cert_path (str): Path to certificate file (default: realMeter/certs/.cert.pem)
        key_path (str): Path to private key file (default: realMeter/certs/.key.pem)
    
    Returns:
        str: Device sFDI value
    """
    # Set default certificate paths if not provided
    if cert_path is None:
        cert_path = os.path.join('realMeter', 'certs', '.cert.pem')
    if key_path is None:
        key_path = os.path.join('realMeter', 'certs', '.key.pem')
    
    # Verify certificate files exist
    if not os.path.exists(cert_path):
        raise FileNotFoundError(f"Certificate file not found: {cert_path}")
    if not os.path.exists(key_path):
        raise FileNotFoundError(f"Private key file not found: {key_path}")
    
    # Setup secure session
    session = setup_session(cert_path, key_path, meter_ip)
    
    # Construct URL for device info endpoint
    url = f'https://{meter_ip}:{meter_port}/sdev'
    
    try:
        response = session.get(url, verify=False, timeout=15.0)
        response.raise_for_status()
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
        
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to meter at {meter_ip}: {e}")
        return None
    except ET.ParseError as e:
        print(f"Error parsing XML response: {e}")
        return None

def getHardwareDetails(meter_ip, meter_port=443, cert_path=None, key_path=None):
    """
    Get hardware details from real smart meter endpoint.
    
    Args:
        meter_ip (str): IP address of the smart meter
        meter_port (int): Port number (default 443 for HTTPS)
        cert_path (str): Path to certificate file (default: realMeter/certs/.cert.pem)
        key_path (str): Path to private key file (default: realMeter/certs/.key.pem)
    
    Returns:
        dict: Hardware details including lFDI, swVer, mfID
    """
    # Set default certificate paths if not provided
    if cert_path is None:
        cert_path = os.path.join('realMeter', 'certs', '.cert.pem')
    if key_path is None:
        key_path = os.path.join('realMeter', 'certs', '.key.pem')
    
    # Verify certificate files exist
    if not os.path.exists(cert_path):
        raise FileNotFoundError(f"Certificate file not found: {cert_path}")
    if not os.path.exists(key_path):
        raise FileNotFoundError(f"Private key file not found: {key_path}")
    
    # Setup secure session
    session = setup_session(cert_path, key_path, meter_ip)
    
    # Construct URL for hardware details endpoint
    url = f'https://{meter_ip}:{meter_port}/sdev/sdi'
    
    try:
        response = session.get(url, verify=False, timeout=15.0)
        response.raise_for_status()
        xml_data = response.text
        
        # Parse XML
        root = ET.fromstring(xml_data)
        ns = {'ns': 'urn:ieee:std:2030.5:ns'}
        
        # Extract hardware details
        hw_info_names = ['lFDI', 'swVer', 'mfID']
        hw_info_dict = {}
        
        for name in hw_info_names:
            elem = root.find(f'.//{IEEE_PREFIX}{name}')
            hw_info_dict[name] = elem.text if elem is not None else ''
        
        return hw_info_dict
        
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to meter at {meter_ip}: {e}")
        return {}
    except ET.ParseError as e:
        print(f"Error parsing XML response: {e}")
        return {}

# Example usage and testing
if __name__ == "__main__":
    import sys
    
    # Get meter IP from environment variable (loaded from .env file) or command line
    meter_ip = os.getenv('METER_IP')
    meter_port = int(os.getenv('METER_PORT', '443'))
    
    if not meter_ip:
        if len(sys.argv) > 1:
            meter_ip = sys.argv[1]
        else:
            print("Usage: python getRealData.py <meter_ip>")
            print("Or set METER_IP in .env file or environment variable")
            sys.exit(1)
    
    print(f"Connecting to meter at {meter_ip}:{meter_port}...")
    
    # Test hardware details
    print("\n=== Hardware Details ===")
    hw_details = getHardwareDetails(meter_ip, meter_port)
    if hw_details:
        for key, value in hw_details.items():
            print(f"{key}: {value}")
    else:
        print("Failed to get hardware details")
    
    # Test device ID
    print("\n=== Device ID ===")
    device_id = getDeviceID(meter_ip, meter_port)
    if device_id:
        print(f"Device sFDI: {device_id}")
    else:
        print("Failed to get device ID")
    
    # Test meter reading
    print("\n=== Meter Reading ===")
    value, tou_tier = getInstantaneousMeterReading(meter_ip, meter_port)
    if value is not None:
        print(f"Meter Value: {value}")
        print(f"Time-of-Use Tier: {tou_tier}")
    else:
        print("Failed to get meter reading") 