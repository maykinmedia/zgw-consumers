from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class StartWithValidator:
    code = "invalid"

    def __init__(
        self,
        prefix: str,
        message: str = None,
        code: str = None,
        return_value: bool = True,
    ):
        self.prefix = prefix
        self.return_value = return_value

        if code is not None:
            self.code = code

        if message is not None:
            self.message = message
        else:
            self.message = _(
                "The given value {must_or_cannot} start with '{prefix}'"
            ).format(
                must_or_cannot="must" if self.return_value else "cannot",
                prefix=self.prefix,
            )

    def __call__(self, value: str) -> bool:
        if not value.startswith(self.prefix) == self.return_value:
            raise ValidationError(self.message, code=self.code, params={"value": value})

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.prefix == other.prefix
            and (self.message == other.message)
            and (self.code == other.code)
            and (self.return_value == other.return_value)
        )


@deconstructible
class IsNotUrlValidator(URLValidator):
    message = _("String cannot be a URL")

    def __call__(self, value):
        try:
            super().__call__(value)
        except ValidationError:
            return

        raise ValidationError(self.message, code=self.code, params={"value": value})
