from behave import given, when, then


@given(u'I am not logged in')
def not_logged_in(context):
    pass


@when(u'I access the url "{url}"')
def i_access_the_url(context, url):
    br = context.browser
    br.open(context.browser_url(url))
    context.response = br.response()
    assert context.response.code == 200


@then(u'I see the navbar')
def i_see_the_navbar(context):
    dom = context.parse_lxml()
    navbar = dom.cssselect('nav.navbar')[0]
    assert navbar
