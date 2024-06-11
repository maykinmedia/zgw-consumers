from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class PrefixValidator:
    code = "invalid"

    def __init__(
        self,
        prefix: str,
        message: str = None,
        code: str = None,
        starts_with: bool = True,
    ):
        self.prefix = prefix
        self.starts_with = starts_with

        if code is not None:
            self.code = code

        if message is not None:
            self.message = message
        else:
            self.message = _(
                "The given value {must_or_cannot} start with '{prefix}'"
            ).format(
                must_or_cannot="must" if self.starts_with else "cannot",
                prefix=self.prefix,
            )

    def __call__(self, value: str) -> bool:
        if value.startswith(self.prefix) != self.starts_with:
            raise ValidationError(self.message, code=self.code, params={"value": value})

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.prefix == other.prefix
            and (self.message == other.message)
            and (self.code == other.code)
            and (self.starts_with == other.starts_with)
        )


@deconstructible
class NonUrlValidator(URLValidator):
    message = _("Value cannot be a URL")

    def __call__(self, value):
        try:
            super().__call__(value)
        except ValidationError:
            return

        raise ValidationError(self.message, code=self.code, params={"value": value})
