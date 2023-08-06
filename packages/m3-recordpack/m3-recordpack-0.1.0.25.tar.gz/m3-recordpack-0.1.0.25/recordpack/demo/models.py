# coding: utf-8
u"""
Модели приложения
"""
#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

# Stdlib
from __future__ import absolute_import
import json

# 3rdparty
from django.db import models
import six

#------------------------------------------------------------------------------
# Models
#------------------------------------------------------------------------------

class Person(models.Model):
    u"""
    Физическое лицо (человек)
    """

    GENDERS = {
        0: u'муж.',
        1: u'жен',
    }
    GENDERS_LIST = list(GENDERS.items())

    fname = models.CharField(
        u'Имя', max_length=255)
    sname = models.CharField(
        u'Фамилия', max_length=255)
    mname = models.CharField(
        u'Отчество', max_length=255)
    birthday = models.DateField(
        u'День рождения', null=True)
    gender = models.SmallIntegerField(
        u'Пол',
        choices=six.iteritems(GENDERS),
        default=0)
    

    # Properties
    # -----------------------------------------------------------------
    
    @property
    def fullname(self):
        return u'{.fname} {.sname} {.mname}'.format(self).rstrip()

    @property
    def shortname(self):
        return u'{fname} .{sname} .{mname}'.format(
            fname=self.fname,
            sname=(self.sname or ' ')[0],
            mname=(self.mname or ' ')[0]
        ).rstrip(' .')


    # Meta
    # -----------------------------------------------------------------

    class Meta:
        verbose_name = u'Физическое лицо'
        verbose_name_plural = u'Физические лица'
