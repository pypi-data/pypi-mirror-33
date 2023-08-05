from fixation import models


def is_message(target):
    return isinstance(target, models.Message)


def is_field(target):
    return isinstance(target, models.Field)


def is_component(target):
    if isinstance(target, models.Component):
        return True
    elif hasattr(target, 'TagText') and not target.TagText.isdigit():
        return True
    return False


class Filter:
    def __init__(self, blacklist=[], whitelist=[]):
        self.blacklist = blacklist
        self.whitelist = whitelist
        from collections import defaultdict
        self.ctx_blacklist = defaultdict(list)
        self.ctx_whitelist = defaultdict(list)

    def is_blacklisted(self, target, context=None):
        id = models.get_id(target)
        if context:
            if id in self.ctx_blacklist[models.get_id(context)]:
                return True
        return id in self.blacklist

    def is_whitelisted(self, target, context=None):
        id = models.get_id(target)
        if context:
            if id in self.ctx_whitelist[models.get_id(context)]:
                return True
        return id in self.whitelist
