from re import compile

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


@deconstructible
class UserFieldsValidator:
    regex = '[^а-яёА-ЯЁ]+|[^a-zA-Z]+'
    field = 'Переданное значение'
    message = '<%s> на разных языках либо содержит не только буквы.'

    def __init__(
        self,
        regex: str | None = None,
        field: str | None = None,
    ) -> None:
        if regex is not None:
            self.regex = regex
        if field is not None:
            self.field = field
        self.message = f'\n{self.field} {self.message}\n'

        self.regex = compile(self.regex)

    def __call__(self, value: str) -> None:
        if not self.regex.search(value):
            raise ValidationError(self.message % value)
