# -*- coding: utf-8 -*-
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneWithPackageLayer
from plone.testing import z2

import collective.js.tablednd


COLLECTIVE_JS_TABLEDND_FIXTURE = PloneWithPackageLayer(
    zcml_package=collective.js.tablednd,
    zcml_filename='testing.zcml',
    gs_profile_id='collective.js.tablednd:testing',
    name='CollectiveJsTableDNDLayer',
    additional_z2_products=()
)


COLLECTIVE_JS_TABLEDND_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_JS_TABLEDND_FIXTURE,),
    name='CollectiveJsTableDNDLayer:IntegrationTesting'
)


COLLECTIVE_JS_TABLEDND_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_JS_TABLEDND_FIXTURE,),
    name='CollectiveJsTableDNDLayer:FunctionalTesting'
)


COLLECTIVE_JS_TABLEDND_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        COLLECTIVE_JS_TABLEDND_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE
    ),
    name='CollectiveJsTableDNDLayer:AcceptanceTesting'
)
