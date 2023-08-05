# encoding: utf-8

import os
import plistlib
from uuid import uuid4
from cryptography import x509
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from networkutil.ssl import (generate_config_ca,
                             get_config_file_path,
                             SSLConstant,
                             NameOID,
                             register_ssl_config,
                             SSL_CONFIG)
from .._constants import SSL_CERT_CA, SSL_PROFILE_NAME
from ..exceptions import SSLError


def check_ca_exists():

    cfg = register_ssl_config()

    ca_key = get_config_file_path(fn=SSL_CERT_CA,
                                  ext=SSLConstant.private_key)

    ca_pem = get_config_file_path(fn=SSL_CERT_CA,
                                  ext=SSLConstant.pem)

    ca_der = get_config_file_path(fn=SSL_CERT_CA,
                                  ext=SSLConstant.der)

    return (True
            if os.path.exists(ca_key)
            and os.path.exists(ca_pem)
            and os.path.exists(ca_der)
            and SSL_CERT_CA in cfg[SSL_CONFIG]
            else False)


def create_ca():
    generate_config_ca(name=SSL_CERT_CA,
                       subject_keys={
                           NameOID.COMMON_NAME: SSL_CERT_CA,
                           NameOID.COUNTRY_NAME: u'GB'
                       },
                       digest=hashes.SHA1(),
                       passphrase=None,
                       version1=True)


def get_ca():

    if not check_ca_exists():
        raise SSLError(u'Root CA must be generated before starting HTTPS servers!')

    ca_key = u'{k}.{c}'.format(k=SSL_CONFIG,
                               c=SSL_CERT_CA)
    cfg = register_ssl_config()

    ca_filepaths = cfg[ca_key]

    backend = default_backend()

    with open(ca_filepaths[SSLConstant.private_key], 'rb') as key_f:
        key = load_pem_private_key(key_f.read(), password=None, backend=backend)

    with open(ca_filepaths[SSLConstant.pem], 'rb') as pem_f:
        pem = x509.load_pem_x509_certificate(pem_f.read(), backend=backend)

    return pem, key, ca_filepaths


def create_apple_configurator_profile(filepath):
    # Read certificate file (DER)
    certificate_file = get_config_file_path(fn=SSL_CERT_CA,
                                            ext=SSLConstant.der)
    _, certificate_fn = os.path.split(certificate_file)

    with open(certificate_file, 'rb') as f:
        certificate = f.read()

    # Generate UUIDs
    profile_uuid = str(uuid4()).upper()
    cert_payload_uuid = str(uuid4()).upper()

    # Create the plist structure
    profile_plist = {
        u'PayloadDisplayName': SSL_PROFILE_NAME,
        u'PayloadIdentifier': u'{name}.{uuid}'.format(name=SSL_PROFILE_NAME,
                                                      uuid=profile_uuid),  # Change to machine name?
        u'PayloadRemovalDisallowed': False,
        u'PayloadType': u'Configuration',
        u'PayloadUUID': profile_uuid,
        u'PayloadVersion': 1,
        u'PayloadContent': [
            {
                u'PayloadCertificateFileName': certificate_fn,
                u'PayloadContent': plistlib.Data(certificate),
                u'PayloadDescription': u'Adds a CA root certificate',
                u'PayloadDisplayName': SSL_CERT_CA,
                u'PayloadIdentifier': u'com.apple.security.root.{uuid}'.format(uuid=cert_payload_uuid),
                u'PayloadType': u'com.apple.security.root',
                u'PayloadUUID': cert_payload_uuid,
                u'PayloadVersion': 1
            }
        ]
    }

    # Save the profile
    plistlib.writePlist(profile_plist, filepath)
