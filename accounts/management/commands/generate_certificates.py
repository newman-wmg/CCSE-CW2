from django.core.management.base import BaseCommand
from django.conf import settings
import os
from OpenSSL import crypto

class Command(BaseCommand):
    help = 'Generate self-signed SSL certificates for development'

    def handle(self, *args, **options):
        # Generate key
        k = crypto.PKey()
        k.generate_key(crypto.TYPE_RSA, 2048)

        # Generate certificate
        cert = crypto.X509()
        cert.get_subject().C = "UK"
        cert.get_subject().ST = "London"
        cert.get_subject().L = "London"
        cert.get_subject().O = "SecureCart"
        cert.get_subject().OU = "Development"
        cert.get_subject().CN = "localhost"
        cert.set_serial_number(1000)
        cert.gmtime_adj_notBefore(0)
        cert.gmtime_adj_notAfter(365*24*60*60)  # Valid for one year
        cert.set_issuer(cert.get_subject())
        cert.set_pubkey(k)
        cert.sign(k, 'sha256')

        # Write certificate
        cert_path = os.path.join(settings.BASE_DIR, 'certificates')
        if not os.path.exists(cert_path):
            os.makedirs(cert_path)

        with open(os.path.join(cert_path, "cert.pem"), "wb") as f:
            f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))

        with open(os.path.join(cert_path, "key.pem"), "wb") as f:
            f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))

        self.stdout.write(self.style.SUCCESS('Successfully generated SSL certificates'))