import os
from datetime import datetime

from django.contrib.admin import AdminSite
from django.contrib.auth.models import User
from django.core.files import File
from django.db.models.deletion import ProtectedError
from django.test import RequestFactory, TestCase, TransactionTestCase

import requests_mock
from privates.test import temp_private_root

from zgw_consumers.admin import CertificateAdmin
from zgw_consumers.constants import APITypes, CertificateTypes
from zgw_consumers.forms import CertificateAdminForm
from zgw_consumers.models import Certificate, Service

TEST_FILES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


@temp_private_root()
class CertificateTests(TestCase):
    def test_calculated_properties(self):
        client_certificate_f = open(os.path.join(TEST_FILES, "test.certificate"), "r")
        key_f = open(os.path.join(TEST_FILES, "test.key"), "r")

        certificate = Certificate.objects.create(
            label="Test certificate",
            type=CertificateTypes.key_pair,
            public_certificate=File(client_certificate_f, name="test.certificate"),
            private_key=File(key_f, name="test.key"),
        )

        client_certificate_f.close()
        key_f.close()

        self.assertEqual(datetime(2023, 2, 21, 14, 26, 51), certificate.expiry_date)
        self.assertEqual(
            "C: NL, ST: Some-State, O: Internet Widgits Pty Ltd", certificate.issuer
        )
        self.assertEqual(
            "C: NL, ST: Some-State, O: Internet Widgits Pty Ltd", certificate.subject
        )

    def test_admin_validation_invalid_certificate(self):
        with open(
            os.path.join(TEST_FILES, "invalid.certificate"), "r"
        ) as client_certificate_f:
            form = CertificateAdminForm(
                {
                    "label": "Test invalid certificate",
                    "type": CertificateTypes.cert_only,
                },
                {"public_certificate": File(client_certificate_f)},
            )

        self.assertFalse(form.is_valid())

    def test_admin_validation_valid_certificate(self):
        with open(
            os.path.join(TEST_FILES, "test.certificate"), "r"
        ) as client_certificate_f:
            form = CertificateAdminForm(
                {
                    "label": "Test invalid certificate",
                    "type": CertificateTypes.cert_only,
                },
                {"public_certificate": File(client_certificate_f)},
            )

        self.assertTrue(form.is_valid())

    def test_invalid_key_pair(self):
        client_certificate_f = open(os.path.join(TEST_FILES, "test.certificate"), "r")
        # Valid key that belongs to another certificate
        key_f = open(os.path.join(TEST_FILES, "test2.key"), "r")

        certificate = Certificate.objects.create(
            label="Test certificate",
            type=CertificateTypes.key_pair,
            public_certificate=File(client_certificate_f, name="test.certificate"),
            private_key=File(key_f, name="test2.key"),
        )

        client_certificate_f.close()
        key_f.close()

        self.assertFalse(certificate.is_valid_key_pair())

    def test_valid_key_pair(self):
        client_certificate_f = open(os.path.join(TEST_FILES, "test.certificate"), "r")
        key_f = open(os.path.join(TEST_FILES, "test.key"), "r")

        certificate = Certificate.objects.create(
            label="Test certificate",
            type=CertificateTypes.key_pair,
            public_certificate=File(client_certificate_f, name="test.certificate"),
            private_key=File(key_f, name="test.key"),
        )

        client_certificate_f.close()
        key_f.close()

        self.assertTrue(certificate.is_valid_key_pair())

    def test_valid_key_pair_missing_key(self):
        with open(
            os.path.join(TEST_FILES, "test.certificate"), "r"
        ) as client_certificate_f:
            certificate = Certificate.objects.create(
                label="Test certificate",
                type=CertificateTypes.key_pair,
                public_certificate=File(client_certificate_f, name="test.certificate"),
            )

        self.assertIsNone(certificate.is_valid_key_pair())

    def test_admin_changelist_doesnt_crash_on_missing_files(self):
        # Github #39
        client_certificate_f = open(os.path.join(TEST_FILES, "test.certificate"), "r")
        key_f = open(os.path.join(TEST_FILES, "test.key"), "r")

        certificate = Certificate.objects.create(
            label="Test certificate",
            type=CertificateTypes.key_pair,
            public_certificate=File(client_certificate_f, name="test.certificate"),
            private_key=File(key_f, name="test.key"),
        )
        # delete the physical files from media storage
        os.unlink(certificate.public_certificate.path)
        os.unlink(certificate.private_key.path)

        certificate_admin = CertificateAdmin(model=Certificate, admin_site=AdminSite())

        # fake a superuser admin request to changelist
        request = RequestFactory().get("/dummy")
        request.user = User.objects.create_user(is_superuser=True, username="admin")
        response = certificate_admin.changelist_view(request)

        # calling .render() to force actual rendering and trigger issue
        response.render()

        self.assertEqual(response.status_code, 200)


@temp_private_root()
class ServiceWithCertificateTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        client_certificate_f = open(os.path.join(TEST_FILES, "test.certificate"), "r")
        server_certificate_f = open(os.path.join(TEST_FILES, "test2.certificate"), "r")
        key_f = open(os.path.join(TEST_FILES, "test.key"), "r")

        cls.client_certificate = Certificate.objects.create(
            label="Test client certificate",
            type=CertificateTypes.key_pair,
            public_certificate=File(client_certificate_f, name="test.certificate"),
            private_key=File(key_f, name="test.key"),
        )
        cls.client_certificate_only = Certificate.objects.create(
            label="Test client certificate (only cert)",
            type=CertificateTypes.cert_only,
            public_certificate=File(client_certificate_f, name="test1.certificate"),
        )
        cls.server_certificate = Certificate.objects.create(
            label="Test server certificate",
            type=CertificateTypes.cert_only,
            public_certificate=File(server_certificate_f, name="test2.certificate"),
        )

        client_certificate_f.close()
        server_certificate_f.close()
        key_f.close()

    def test_build_client_with_server_and_client_certificates(self):
        oas_path = os.path.join(os.path.dirname(__file__), "schemas/drc.yaml")

        with open(oas_path, "r") as oas_file:
            service = Service.objects.create(
                label="Test",
                api_type=APITypes.drc,
                api_root="https://foo.bar",
                oas_file=File(oas_file, name="schema.yaml"),
                client_certificate=self.client_certificate,
                server_certificate=self.server_certificate,
            )

        client = service.build_client()

        with requests_mock.Mocker() as m:
            m.get("https://foo.bar")
            client.request("https://foo.bar", "enkelvoudiginformatieobject_list")
            history = m.request_history

        request_with_tls = history[0]

        self.assertTupleEqual(
            (
                self.client_certificate.public_certificate.path,
                self.client_certificate.private_key.path,
            ),
            request_with_tls.cert,
        )
        self.assertEqual(
            self.server_certificate.public_certificate.path, request_with_tls.verify
        )

    def test_build_client_with_only_client_certificates(self):
        oas_path = os.path.join(os.path.dirname(__file__), "schemas/drc.yaml")

        with open(oas_path, "r") as oas_file:
            service = Service.objects.create(
                label="Test",
                api_type=APITypes.drc,
                api_root="https://foo.bar",
                oas_file=File(oas_file, name="schema.yaml"),
                client_certificate=self.client_certificate,
            )

        client = service.build_client()

        with requests_mock.Mocker() as m:
            m.get("https://foo.bar")
            client.request("https://foo.bar", "enkelvoudiginformatieobject_list")
            history = m.request_history

        request_with_tls = history[0]

        self.assertTupleEqual(
            (
                self.client_certificate.public_certificate.path,
                self.client_certificate.private_key.path,
            ),
            request_with_tls.cert,
        )
        self.assertTrue(request_with_tls.verify)

    def test_build_client_with_only_client_certificates_no_key(self):
        oas_path = os.path.join(os.path.dirname(__file__), "schemas/drc.yaml")

        with open(oas_path, "r") as oas_file:
            service = Service.objects.create(
                label="Test",
                api_type=APITypes.drc,
                api_root="https://foo.bar",
                oas_file=File(oas_file, name="schema.yaml"),
                client_certificate=self.client_certificate_only,
            )

        client = service.build_client()

        with requests_mock.Mocker() as m:
            m.get("https://foo.bar")
            client.request("https://foo.bar", "enkelvoudiginformatieobject_list")
            history = m.request_history

        request_with_tls = history[0]

        self.assertEqual(
            self.client_certificate_only.public_certificate.path, request_with_tls.cert
        )
        self.assertTrue(request_with_tls.verify)

    def test_build_client_with_only_server_certificates(self):
        oas_path = os.path.join(os.path.dirname(__file__), "schemas/drc.yaml")

        with open(oas_path, "r") as oas_file:
            service = Service.objects.create(
                label="Test",
                api_type=APITypes.drc,
                api_root="https://foo.bar",
                oas_file=File(oas_file, name="schema.yaml"),
                server_certificate=self.server_certificate,
            )

        client = service.build_client()

        with requests_mock.Mocker() as m:
            m.get("https://foo.bar")
            client.request("https://foo.bar", "enkelvoudiginformatieobject_list")
            history = m.request_history

        request_with_tls = history[0]

        self.assertEqual(
            self.server_certificate.public_certificate.path, request_with_tls.verify
        )

    def test_certificate_deletion_with_services(self):
        oas_path = os.path.join(os.path.dirname(__file__), "schemas/drc.yaml")

        with open(os.path.join(TEST_FILES, "test.certificate"), "r") as certificate_f:
            certificate = Certificate.objects.create(
                label="Test client certificate",
                type=CertificateTypes.cert_only,
                public_certificate=File(certificate_f, name="test.certificate"),
            )

        with open(oas_path, "r") as oas_file:
            Service.objects.create(
                label="Test",
                api_type=APITypes.drc,
                api_root="https://foo.bar",
                oas_file=File(oas_file, name="schema.yaml"),
                client_certificate=certificate,
            )

        with self.assertRaises(ProtectedError):
            certificate.delete()


@temp_private_root()
class TestCertificateFilesDeletion(TransactionTestCase):
    def test_certificate_deletion_deletes_files(self):
        with open(os.path.join(TEST_FILES, "test.certificate"), "r") as certificate_f:
            certificate = Certificate.objects.create(
                label="Test client certificate",
                type=CertificateTypes.cert_only,
                public_certificate=File(certificate_f, name="test.certificate"),
            )

        file_path = certificate.public_certificate.path
        storage = certificate.public_certificate.storage

        certificate.delete()

        self.assertFalse(storage.exists(file_path))
