import zipfile

from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _

from zgw_consumers.models import Certificate


class Command(BaseCommand):
    help = "Dump all certificates to a .zip archive"

    def add_arguments(self, parser):
        parser.add_argument(
            "--filename",
            help=_("Name of the archive to write data to"),
            type=str,
            default="certificates.zip",
        )

    def handle(self, *args, **options):
        filename = options["filename"]
        certs = Certificate.objects.all()
        with zipfile.ZipFile(filename, "w") as zf:
            for cert in certs:
                if cert.public_certificate:
                    zf.write(
                        cert.public_certificate.path,
                        arcname=cert.public_certificate.name,
                    )

                if cert.private_key:
                    zf.write(cert.private_key.path, arcname=cert.private_key.name)
