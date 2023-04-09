from re import compile

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible


@deconstructible
class UserFieldsValidator:
    first_regex = '[^а-яёА-ЯЁ]+'
    second_regex = '[^a-zA-Z]+'
    field = 'Переданное значение'
    message = '<%s> на разных языках либо содержит не только буквы.'

    def __init__(
        self,
        first_regex: str | None = None,
        second_regex: str | None = None,
        field: str | None = None,
    ) -> None:
        if first_regex is not None:
            self.first_regex = first_regex
        if second_regex is not None:
            self.second_regex = second_regex
        if field is not None:
            self.field = field
        self.message = f'\n{self.field} {self.message}\n'

        self.first_regex = compile(self.first_regex)
        self.second_regex = compile(self.second_regex)

    def __call__(self, value: str) -> None:
        if self.first_regex.search(value) and self.second_regex.search(value):
            raise ValidationError(self.message % value)
