# -*- coding: utf-8 -*-

class Parameter:
    def __init__(
        self, id=None, name=None, cType=None, hasLimits=False
    ):
        self.id = id
        self.name = name
        self.cType = cType
        self.hasLimits = hasLimits
