from django.core.checks import CheckMessage, Tags, Warning, register
from django.db import DatabaseError


@register(Tags.database)
def check_zgw_auth_secret(databases=None, **kwargs) -> list[CheckMessage]:
    """
    Warn about services using ZGW auth with an empty secret.

    An empty secret can't be used as HMAC key to sign the JWT, so building a client for
    such a service crashes.
    """
    if not databases:
        return []

    from .constants import AuthTypes
    from .models import Service

    errors: list[CheckMessage] = []
    for alias in databases:
        try:
            slugs = list(
                Service.objects.using(alias)
                .filter(auth_type=AuthTypes.zgw, secret="")
                .values_list("slug", flat=True)
            )
        except DatabaseError:  # table doesn't exist (yet)
            continue

        errors += [
            Warning(
                f"Service '{slug}' uses ZGW authorization with an empty secret.",
                hint="Configure a secret, or select another authorization type.",
                obj=f"{Service._meta.label}(slug='{slug}')",
                id="zgw_consumers.W001",
            )
            for slug in slugs
        ]
    return errors
