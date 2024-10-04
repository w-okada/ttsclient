import os
from OpenSSL import crypto
from datetime import datetime

from ttsclient.const import SSL_KEY_DIR


def generate_self_signed_cert():
    SSL_KEY_DIR.mkdir(exist_ok=True)
    key_base_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    keyfile = f"{key_base_name}.key"
    certfile = f"{key_base_name}.cert"
    certargs = {
        "Country": "JP",
        "State": "Tokyo",
        "City": "Chuo-ku",
        "Organization": "F",
        "Org. Unit": "F",
    }
    cert_dir = SSL_KEY_DIR

    c_f = cert_dir / certfile
    k_f = cert_dir / keyfile
    if not os.path.exists(c_f) or not os.path.exists(k_f):
        k = crypto.PKey()
        k.generate_key(crypto.TYPE_RSA, 2048)
        cert = crypto.X509()
        cert.get_subject().C = certargs["Country"]
        cert.get_subject().ST = certargs["State"]
        cert.get_subject().L = certargs["City"]
        cert.get_subject().O = certargs["Organization"]  # noqa
        cert.get_subject().OU = certargs["Org. Unit"]
        cert.get_subject().CN = "Example"
        cert.set_serial_number(1000)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(315360000)
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(k)
        cert.sign(k, "sha1")
        open(c_f, "wb").write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
        open(k_f, "wb").write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
    return c_f, k_f
