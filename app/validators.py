"""
    Customized user types for Pydentic Validation
"""


import re


password_regex_pattern = re.compile('[A-Za-z0-9@#$%^&+=]{8,24}')
names_regex_pattern = re.compile('[A-Za-z]{2,15}')


class Password(str):
    """
        Password type for Pydentic validation
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        """
        validating method
        """

        validated = password_regex_pattern.fullmatch(value)

        if not validated:
            raise ValueError('invalid password format')

        return cls(f'{value}')

    def __repr__(self):
        return f'Password({super().__repr__()})'


class Names(str):
    """
        User Names type for Pydentic validation
    """

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        """
        validating method
        """

        validated = names_regex_pattern.fullmatch(value)

        if not validated:
            raise ValueError('invalid name format')

        return cls(f'{value}')

    def __repr__(self):
        return f'Names({super().__repr__()})'
