# coding: utf-8

#------------------------------------------------------------------------------
# Imports
#------------------------------------------------------------------------------

# 3rdparty
from __future__ import absolute_import
from django.conf import urls
from django.conf.urls import url

from m3_ext.ui import app_ui
from m3.actions import ControllerCache

# Demo
from . import actions
from . import controller

#------------------------------------------------------------------------------
# Action packs registration
#------------------------------------------------------------------------------

def register_urlpatterns():
    return (
        url('^', controller.action_controller.process_request),
    )


def register_actions():
    controller.action_controller.extend_packs([
        actions.PersonPack(),
    ])


def register_desktop_menu():
    metarole = app_ui.GENERIC_USER
    persons_shortcut = app_ui.DesktopShortcut(
        name=u'Физические лица',
        pack=ControllerCache.find_pack(actions.PersonPack),
        index=10)
    app_ui.DesktopLoader.add(
        metarole, app_ui.DesktopLoader.TOPTOOLBAR, persons_shortcut)
    app_ui.DesktopLoader.add(
        metarole, app_ui.DesktopLoader.START_MENU, persons_shortcut)