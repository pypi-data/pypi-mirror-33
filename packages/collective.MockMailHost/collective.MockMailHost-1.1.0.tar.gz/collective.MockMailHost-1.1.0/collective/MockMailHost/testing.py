# -*- coding: utf-8 -*-
from plone.app.testing import applyProfile
from plone.app.testing import PloneSandboxLayer
from plone.app.testing.layers import FunctionalTesting
from plone.app.testing.layers import IntegrationTesting
import doctest


class CollectiveMockMailHostLayer(PloneSandboxLayer):

    def setUpZope(self, app, configurationContext):
        import collective.MockMailHost
        self.loadZCML(package=collective.MockMailHost)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'collective.MockMailHost:default')

COLLECTIVE_MOCKMAILHOST_FIXTURE = CollectiveMockMailHostLayer()

COLLECTIVE_MOCKMAILHOST_INTEGRATION_TESTING = IntegrationTesting(
    bases=(COLLECTIVE_MOCKMAILHOST_FIXTURE, ),
    name='CollectiveMockMailHostLayer:Integration'
)
COLLECTIVE_MOCKMAILHOST_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(COLLECTIVE_MOCKMAILHOST_FIXTURE, ),
    name='CollectiveMockMailHostLayer:Functional'
)

optionflags = (
    doctest.REPORT_ONLY_FIRST_FAILURE
    | doctest.ELLIPSIS
    | doctest.NORMALIZE_WHITESPACE
)
