from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, URLValidator
from django.utils.translation import gettext_lazy as _

validate_leading_slashes = RegexValidator(
    regex=r"^[^/#][^\s]*",
    message="The value must be a relative path.",
    code="invalid",
)


class NonUrlValidator(URLValidator):
    message = _("Value cannot be a URL")

    def __call__(self, value):
        try:
            super().__call__(value)
        except ValidationError:
            return

        raise ValidationError(self.message, code=self.code, params={"value": value})
