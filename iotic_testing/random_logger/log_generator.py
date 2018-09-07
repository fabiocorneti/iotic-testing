# -*- coding: utf-8 -*-
import faker

__all__ = ['RandomLogGenerator']


class RandomLogGenerator:
    """
    Yields random log data.
    """

    def __init__(self, feed, schema):
        """
        Create a new log generator for the given schema.
        """
        self.__schema = schema
        self.__feed = feed
        self.__template = feed.get_template()
        self.__faker = faker.Faker()

    def __next__(self):
        for field_name, field_definition in self.__schema.items():
            if field_definition.provider is None:
                continue
            if callable(field_definition.provider):
                value = field_definition.provider(self.__faker)
            else:
                value = getattr(self.__faker, field_definition.provider)()
            # TODO: is it correct to reuse the template?
            setattr(self.__template.values, field_name, value)
        return self.__template

    def __iter__(self):
        return self
