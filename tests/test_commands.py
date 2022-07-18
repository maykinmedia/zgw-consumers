import os
import zipfile

from django.core.files import File
from django.core.management import call_command
from django.test import TestCase

from freezegun import freeze_time
from privates.test import temp_private_root

from zgw_consumers.constants import CertificateTypes
from zgw_consumers.models import Certificate

TEST_FILES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


@freeze_time("2022-01-01")
@temp_private_root()
class CertificateDumpTests(TestCase):
    def setUp(self) -> None:
        super().setUp()

        def remove_certs_archive():
            if os.path.exists("certificates.zip"):
                os.remove("certificates.zip")

        self.addCleanup(remove_certs_archive)

    def test_dump_certificate_files(self):
        client_certificate_f = open(os.path.join(TEST_FILES, "test.certificate"), "r")
        key_f = open(os.path.join(TEST_FILES, "test.key"), "r")
        certificate1 = Certificate.objects.create(
            label="Test certificate",
            type=CertificateTypes.key_pair,
            public_certificate=File(client_certificate_f, name="test.certificate"),
            private_key=File(key_f, name="test.key"),
        )
        client_certificate_f.close()
        key_f.close()

        client_certificate_f = open(os.path.join(TEST_FILES, "test.certificate"), "r")
        key_f = open(os.path.join(TEST_FILES, "test.key"), "r")
        certificate2 = Certificate.objects.create(
            label="Test certificate2",
            type=CertificateTypes.key_pair,
            public_certificate=File(client_certificate_f, name="test.certificate2"),
            private_key=File(key_f, name="test.key2"),
        )
        client_certificate_f.close()
        key_f.close()

        call_command("dump_certs")

        expected_files = [
            "ssl_certs_keys/2022/01/01/test.certificate",
            "ssl_certs_keys/2022/01/01/test.key",
            "ssl_certs_keys/2022/01/01/test.certificate2",
            "ssl_certs_keys/2022/01/01/test.key2",
        ]
        zf = zipfile.ZipFile("certificates.zip", "r")

        self.assertEqual(zf.namelist(), expected_files)
        self.assertEqual(
            zf.open("ssl_certs_keys/2022/01/01/test.certificate").read(),
            certificate1.public_certificate.read(),
        )
        self.assertEqual(
            zf.open("ssl_certs_keys/2022/01/01/test.key").read(),
            certificate1.private_key.read(),
        )
        self.assertEqual(
            zf.open("ssl_certs_keys/2022/01/01/test.certificate2").read(),
            certificate2.public_certificate.read(),
        )
        self.assertEqual(
            zf.open("ssl_certs_keys/2022/01/01/test.key2").read(),
            certificate2.private_key.read(),
        )
