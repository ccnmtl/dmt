from behave import given, when, then
from django.contrib.auth import BACKEND_SESSION_KEY, SESSION_KEY
from django.conf import settings
from django.utils.module_loading import import_module
from dmt.main.tests.factories import UserFactory


def create_pre_authenticated_session():
    user = UserFactory()
    engine = import_module(settings.SESSION_ENGINE)
    session = engine.SessionStore()
    session[SESSION_KEY] = user.pk
    session[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
    session.save()
    return session.session_key


@given(u'I am not logged in')
def not_logged_in(context):
    context.browser.cookies.delete(settings.SESSION_COOKIE_NAME)


@given(u'I am logged in')
def logged_in(context):
    s = create_pre_authenticated_session()
    context.browser.cookies.add({settings.SESSION_COOKIE_NAME: s})


@when(u'I access the url "{url}"')
def i_access_the_url(context, url):
    context.browser.visit(context.browser_url(url))


@then(u'I see logged out message')
def i_see_logged_out_message(context):
    assert context.browser.is_text_present("re not logged in")


@then(u"I don't see the logged out message")
def i_dont_see_the_logged_out_message(context):
    assert not context.browser.is_text_present("re not logged in")


@then(u'I see the navbar')
def i_see_the_navbar(context):
    assert context.browser.is_element_present_by_css('nav.navbar')


@then(u'I see my usernav')
def i_see_my_usernav(context):
    assert context.browser.is_element_present_by_css('a.username')
