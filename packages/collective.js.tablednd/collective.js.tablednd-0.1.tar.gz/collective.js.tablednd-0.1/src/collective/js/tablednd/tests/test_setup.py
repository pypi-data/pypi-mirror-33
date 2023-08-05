# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from collective.js.tablednd.testing import COLLECTIVE_JS_TABLEDND_INTEGRATION_TESTING  # noqa
from plone import api

import unittest2 as unittest


class TestSetup(unittest.TestCase):
    """Test that collective.js.tablednd is properly installed."""

    layer = COLLECTIVE_JS_TABLEDND_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if collective.js.tablednd is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.isProductInstalled('collective.js.tablednd'))

    def test_uninstall(self):
        """Test if collective.js.tablednd is cleanly uninstalled."""
        self.installer.uninstallProducts(['collective.js.tablednd'])
        self.assertFalse(self.installer.isProductInstalled('collective.js.tablednd'))

    def test_browserlayer(self):
        """Test that ICollectiveJsTableDNDLayer is registered."""
        from collective.js.tablednd.interfaces import ICollectiveJsTableDNDLayer
        from plone.browserlayer import utils
        self.assertIn(ICollectiveJsTableDNDLayer, utils.registered_layers())
