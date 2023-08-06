# -*- coding: utf-8 -*-
from collective.behavior.gallery.behaviors.folderish_gallery import IFolderishGallery # noqa
from collective.behavior.gallery.testing import COLLECTIVE_BEHAVIOR_GALLERY_INTEGRATION_TESTING  # noqa
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.behavior.interfaces import IBehavior
from zope.component import getUtility

import unittest


class FolderishGalleryIntegrationTest(unittest.TestCase):

    layer = COLLECTIVE_BEHAVIOR_GALLERY_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_behavior_folderish_gallery(self):
        behavior = getUtility(
            IBehavior,
            'collective.behavior.gallery.folderish_gallery'
        )
        self.assertEqual(
            behavior.marker,
            IFolderishGallery,
        )
        behavior_name = 'collective.behavior.gallery.behaviors.folderish_gallery.IFolderishGallery' # noqa
        behavior = getUtility(IBehavior, behavior_name)
        self.assertEqual(
            behavior.marker,
            IFolderishGallery,
        )
