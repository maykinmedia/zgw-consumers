import os
from datetime import datetime

from django.test import TestCase

from zgw_consumers.constants import CertificateTypes
from zgw_consumers.forms import CertificateAdminForm
from zgw_consumers.models import Certificate

TEST_FILES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


class CertificateTests(TestCase):
    def test_calculated_properties(self):
        certificate_f = open(os.path.join(TEST_FILES, "test.certificate"), "r")
        key_f = open(os.path.join(TEST_FILES, "test.key"), "r")

        # TODO make factory
        certificate = Certificate.objects.create(
            label="Test certificate",
            type=CertificateTypes.key_pair,
            public_certificate=certificate_f.read(),
            private_key=key_f.read(),
        )

        certificate_f.close()
        key_f.close()

        self.assertEqual(datetime(2023, 2, 21, 14, 26, 51), certificate.expiry_date)
        self.assertEqual(
            "C: NL, ST: Some-State, O: Internet Widgits Pty Ltd", certificate.issuer
        )
        self.assertEqual(
            "C: NL, ST: Some-State, O: Internet Widgits Pty Ltd", certificate.subject
        )

    def test_admin_validation_invalid_certificate(self):
        form = CertificateAdminForm(
            data={
                "label": "Test invalid certificate",
                "type": CertificateTypes.cert_only,
                "public_certificate": "Some invalid certificate text",
            }
        )

        self.assertFalse(form.is_valid())

    def test_admin_validation_valid_certificate(self):
        with open(os.path.join(TEST_FILES, "test.certificate"), "r") as certificate_f:
            form = CertificateAdminForm(
                data={
                    "label": "Test invalid certificate",
                    "type": CertificateTypes.cert_only,
                    "public_certificate": certificate_f.read(),
                }
            )

        self.assertTrue(form.is_valid())

    def test_invalid_key_pair(self):
        certificate_f = open(os.path.join(TEST_FILES, "test.certificate"), "r")
        # Valid key that belongs to another certificate
        key_f = open(os.path.join(TEST_FILES, "test2.key"), "r")

        # TODO make factory
        certificate = Certificate.objects.create(
            label="Test certificate",
            type=CertificateTypes.key_pair,
            public_certificate=certificate_f.read(),
            private_key=key_f.read(),
        )

        certificate_f.close()
        key_f.close()

        self.assertFalse(certificate.is_valid_key_pair())

    def test_valid_key_pair(self):
        certificate_f = open(os.path.join(TEST_FILES, "test.certificate"), "r")
        key_f = open(os.path.join(TEST_FILES, "test1.key"), "r")

        # TODO make factory
        certificate = Certificate.objects.create(
            label="Test certificate",
            type=CertificateTypes.key_pair,
            public_certificate=certificate_f.read(),
            private_key=key_f.read(),
        )

        certificate_f.close()
        key_f.close()

        self.assertTrue(certificate.is_valid_key_pair())

    def test_valid_key_pair_missing_key(self):
        certificate_f = open(os.path.join(TEST_FILES, "test.certificate"), "r")

        # TODO make factory
        certificate = Certificate.objects.create(
            label="Test certificate",
            type=CertificateTypes.key_pair,
            public_certificate=certificate_f.read(),
        )

        certificate_f.close()

        self.assertIsNone(certificate.is_valid_key_pair())
