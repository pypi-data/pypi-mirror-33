# coding: utf-8
u""" Module description. 
"""

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

# 3rdparty
from __future__ import absolute_import
from django.db import models

# Recordpack
from m3_django_compat import get_model

from recordpack.provider import BaseProxy

#------------------------------------------------------------------------------
# Proxies
#------------------------------------------------------------------------------

class PersonListProxy(BaseProxy):
    def load(self, root):
        person_model = get_model('demo', 'Person')
        self.from_root()
        self.gender = person_model.GENDERS[self.gender]
