# -*- coding: utf-8 -*-
from plone.app.upgrade.utils import loadMigrationProfile


def reload_gs_profile(context):
    loadMigrationProfile(
        context,
        'profile-collective.slick:default',
    )


def to_1020(context):
    loadMigrationProfile(
        context,
        'profile-collective.slick:to1020',
    )
    reload_gs_profile(context)
