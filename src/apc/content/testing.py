# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import apc.content


class ApcContentLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=apc.content)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'apc.content:default')


APC_CONTENT_FIXTURE = ApcContentLayer()


APC_CONTENT_INTEGRATION_TESTING = IntegrationTesting(
    bases=(APC_CONTENT_FIXTURE,),
    name='ApcContentLayer:IntegrationTesting',
)


APC_CONTENT_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(APC_CONTENT_FIXTURE,),
    name='ApcContentLayer:FunctionalTesting',
)


APC_CONTENT_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        APC_CONTENT_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='ApcContentLayer:AcceptanceTesting',
)
