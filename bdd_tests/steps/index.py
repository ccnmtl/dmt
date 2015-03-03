from behave import given, when, then
from django.contrib.auth import BACKEND_SESSION_KEY, SESSION_KEY
from django.conf import settings
from django.utils.module_loading import import_module
from dmt.main.tests.factories import UserFactory


def create_pre_authenticated_session():
    user = UserFactory(userprofile__status="active")
    engine = import_module(settings.SESSION_ENGINE)
    session = engine.SessionStore()
    session[SESSION_KEY] = user.pk
    session[BACKEND_SESSION_KEY] = settings.AUTHENTICATION_BACKENDS[0]
    session.save()
    return user, session.session_key


@given(u'I am not logged in')
def not_logged_in(context):
    context.browser.delete_all_cookies()
    context.user = None


@given(u'I am logged in')
def logged_in(context):
    if hasattr(context, 'user') and context.user is not None:
        # already logged in
        return
    b = context.browser
    # can only set a cookie for the domain we are on
    # so, in case this is the very first step to run,
    # we have to visit some page on the site first.
    # a 404 loads quickly and shouldn't involve the databases,
    # so we reduce the chances of a race on the sqlite driver.
    b.get(context.browser_url("/some_404_page/"))
    b.find_element_by_xpath("//body")
    user, s = create_pre_authenticated_session()
    b.add_cookie({'name': settings.SESSION_COOKIE_NAME, 'value': s})
    context.user = user


@when(u'I access the url "{url}"')
def i_access_the_url(context, url):
    context.browser.get(context.browser_url(url))


@then(u'I see logged out message')
def i_see_logged_out_message(context):
    assert "not logged in" in context.browser.find_element_by_tag_name(
        'body').text


@then(u"I don't see the logged out message")
def i_dont_see_the_logged_out_message(context):
    assert "not logged in " not in context.browser.find_element_by_tag_name(
        'body').text


@then(u'I see the navbar')
def i_see_the_navbar(context):
    assert context.browser.find_element_by_css_selector('nav.navbar')


@then(u'I see my usernav')
def i_see_my_usernav(context):
    assert context.browser.find_element_by_css_selector('a.username')
