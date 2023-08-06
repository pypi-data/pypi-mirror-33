# -*- coding: utf-8 -*-

from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContainer
from plone.supermodel import model
from zope.component import adapter
from zope.interface import implementer
from zope.interface import provider


@provider(IFormFieldProvider)
class IFolderishGallery(model.Schema):
    """
    """
    pass


@implementer(IFolderishGallery)
@adapter(IDexterityContainer)
class FolderishGallery(object):
    def __init__(self, context):
        self.context = context
