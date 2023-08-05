from fixation.models import get_id, Message, MsgContent, Component, Field, Enum

import os


class Configuration:
    @staticmethod
    def fiximate(base_dir):
        return Configuration(base_dir)

    def __init__(self, base_dir, messages='messages', fields='fields', components='components'):
        self.base_dir = base_dir
        self.message_dir = messages
        self.fields_dir = fields
        self.components_dir = components

    def get_http_path(self, target):
        if isinstance(target, Message):
            return "{}/{}".format(self.message_dir, get_id(target))
        elif isinstance(target, Field):
            return "{}/{}".format(self.fields_dir, get_id(target))
        elif isinstance(target, Component):
            return "{}/{}".format(self.components_dir, get_id(target))
        else:
            if target.pretty_type().isdigit():
                return "{}/{}".format(self.fields_dir, target.pretty_name())
            else:
                return "{}/{}".format(getattr(self, target.pretty_type().lower()+"s_dir"), target.pretty_name())

    def get_paths(self, target):
        if target == 'messages':
            return os.path.join(self.base_dir, self.message_dir)
        elif target == 'fields':
            return os.path.join(self.base_dir, self.fields_dir)
        elif target == 'components':
            return os.path.join(self.base_dir, self.components_dir)

    @staticmethod
    def get_filename(target):
        return get_id(target)

