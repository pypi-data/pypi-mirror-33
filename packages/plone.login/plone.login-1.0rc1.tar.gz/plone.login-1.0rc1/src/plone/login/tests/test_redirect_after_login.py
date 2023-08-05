# -*- coding: utf-8 -*-
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.login.browser.login import LoginForm
from plone.login.interfaces import IInitialLogin
from plone.login.interfaces import IRedirectAfterLogin
from plone.login.testing import PLONE_LOGIN_FUNCTIONAL_TESTING
from plone.login.testing import PLONE_LOGIN_INTEGRATION_TESTING
from plone.testing.z2 import Browser
from zope.interface import implementer
from zope.interface import Interface
from zope.publisher.interfaces import IRequest

import unittest


@implementer(IRedirectAfterLogin)
class AfterLoginAdapter(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, came_from=None, is_first_login=False):
        return 'http://nohost/plone/sitemap'


@implementer(IInitialLogin)
class InitialLoginAdapter(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        self.context.foo = 'foo'


class TestCameFromFiltering(unittest.TestCase):
    layer = PLONE_LOGIN_INTEGRATION_TESTING

    def setUp(self):
        self.request = self.layer['request']
        self.portal = self.layer['portal']
        self.form = LoginForm(self.portal, self.request)

    def test_get_came_from_via_request(self):
        self.assertEqual(self.form.get_came_from(), None)
        url = 'https://nohost/plone/foo-bar'
        self.request['came_from'] = url
        self.assertEqual(self.form.get_came_from(), url)

    def test_external_urls_are_ignored(self):
        url = 'https://example.com/maliciousness'
        self.request['came_from'] = url
        self.assertEqual(self.form.get_came_from(), None)

    def test_login_templates_are_filtered(self):
        url = 'https://nohost/plone/logout'
        self.request['came_from'] = url
        self.assertEqual(self.form.get_came_from(), None)

    def test_referer_is_fallback(self):
        url = 'https://nohost/plone/test'
        self.request['came_from'] = None
        self.request['HTTP_REFERER'] = url
        self.assertEqual(self.form.get_came_from(), url)


class TestRedirectAfterLogin(unittest.TestCase):

    layer = PLONE_LOGIN_FUNCTIONAL_TESTING

    def setUp(self):
        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False
        self.portal = self.layer['portal']

    def test_redirect_to_portal_if_no_adapter_nor_came_from(self):
        self.browser.open('http://nohost/plone/login')
        self.browser.getLink('Log in').click()
        self.assertEqual(self.browser.url, 'http://nohost/plone/login')

        self.browser.getControl('Login Name').value = TEST_USER_NAME
        self.browser.getControl('Password').value = TEST_USER_PASSWORD
        self.browser.getControl('Log in').click()

        self.assertIn('You are now logged in.', self.browser.contents)
        self.assertEqual(self.browser.url,
                         'http://nohost/plone',
                         'Successful login did not redirect to the homepage '
                         'when came_from was not defined.')

        # Now log out.
        self.browser.getLink('Log out').click()

        self.assertIn('You have been logged out.',
                      self.browser.contents,
                      'Logout status message not displayed.')

    def test_redirect_to_came_from_if_no_adapter_found(self):
        self.browser.open('http://nohost/plone/login')
        self.browser.getLink('Log in').click()
        self.assertEqual(self.browser.url, 'http://nohost/plone/login')

        self.browser.getControl('Login Name').value = TEST_USER_NAME
        self.browser.getControl('Password').value = TEST_USER_PASSWORD
        self.browser.getControl(name='came_from').value = \
            'http://nohost/plone/contact-info'

        self.browser.getControl('Log in').click()

        self.assertIn('You are now logged in.', self.browser.contents)
        self.assertEqual(self.browser.url,
                         'http://nohost/plone/contact-info',
                         'Successful login did not redirect to the came_from.')

        # Now log out.
        self.browser.getLink('Log out').click()

        self.assertIn('You have been logged out.',
                      self.browser.contents,
                      'Logout status message not displayed.')

    def test_redirect_to_adapter_result(self):
        # Register our redirect adapter
        from zope.component import getGlobalSiteManager
        gsm = getGlobalSiteManager()
        gsm.registerAdapter(AfterLoginAdapter,
                            (Interface, IRequest))

        self.browser.open('http://nohost/plone/login')
        self.browser.getLink('Log in').click()
        self.assertEqual(self.browser.url, 'http://nohost/plone/login')

        self.browser.getControl('Login Name').value = TEST_USER_NAME
        self.browser.getControl('Password').value = TEST_USER_PASSWORD
        self.browser.getControl(name='came_from').value = \
            'http://nohost/plone/contact-info'

        self.browser.getControl('Log in').click()

        gsm.unregisterAdapter(AfterLoginAdapter,
                              (Interface, IRequest))

        self.assertIn('You are now logged in.', self.browser.contents)
        self.assertEqual(self.browser.url,
                         'http://nohost/plone/sitemap',
                         'Successful login did not use the adapter for '
                         'redirect.')

        # Now log out.
        self.browser.getLink('Log out').click()

        self.assertIn('You have been logged out.',
                      self.browser.contents,
                      'Logout status message not displayed.')

    def test_initiallogin_adapter(self):
        # Register our redirect adapter
        from zope.component import getGlobalSiteManager
        gsm = getGlobalSiteManager()
        gsm.registerAdapter(InitialLoginAdapter,
                            (Interface, IRequest))

        self.browser.open('http://nohost/plone/login')
        self.browser.getLink('Log in').click()
        self.assertEqual(self.browser.url, 'http://nohost/plone/login')

        self.browser.getControl('Login Name').value = TEST_USER_NAME
        self.browser.getControl('Password').value = TEST_USER_PASSWORD
        self.browser.getControl(name='came_from').value = \
            'http://nohost/plone/contact-info'

        self.browser.getControl('Log in').click()

        gsm.unregisterAdapter(InitialLoginAdapter,
                              (Interface, IRequest))

        self.assertIn('You are now logged in.', self.browser.contents)
        self.assertEqual(self.browser.url, 'http://nohost/plone/contact-info')
        self.assertEqual(self.portal.foo, 'foo')

        # Now log out.
        self.browser.getLink('Log out').click()

        self.assertIn('You have been logged out.',
                      self.browser.contents,
                      'Logout status message not displayed.')
