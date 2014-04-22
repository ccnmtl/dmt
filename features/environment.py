import os
# This is necessary for all installed apps to be recognized, for some reason.
os.environ['DJANGO_SETTINGS_MODULE'] = 'dmt.settings_integration'
import urlparse
from dmt import settings_lettuce as settings
import wsgi_intercept
from django.core.handlers.wsgi import WSGIHandler
from south.management.commands import patch_for_test_db_setup
from BeautifulSoup import BeautifulSoup
from lxml import html


def before_all(context):
    from django.test.simple import DjangoTestSuiteRunner
    # We'll use thise later to frog-march Django through the motions
    # of setting up and tearing down the test environment, including
    # test databases.
    context.runner = DjangoTestSuiteRunner()

    patch_for_test_db_setup()

    host = context.host = 'localhost'
    port = context.port = getattr(settings,
                                  'TESTING_MECHANIZE_INTERCEPT_PORT', 17681)
    # NOTE: Nothing is actually listening on this port. wsgi_intercept
    # monkeypatches the networking internals to use a fake socket when
    # connecting to this port.
    wsgi_intercept.add_wsgi_intercept(host, port, WSGIHandler)

    def browser_url(url):
        """Create a URL for the virtual WSGI server.
        e.g context.browser_url('/'), context.browser_url(reverse('my_view'))
        """
        return urlparse.urljoin('http://%s:%d/' % (host, port), url)

    context.browser_url = browser_url

    def parse_soup():
        r = context.browser.response()
        h = r.read()
        r.seek(0)
        return BeautifulSoup(h)
    context.parse_soup = parse_soup

    def parse_lxml():
        r = context.browser.response()
        data = r.read()
        r.seek(0)
        return html.fromstring(data)
    context.parse_lxml = parse_lxml


def before_scenario(context, scenario):
    context.runner.setup_test_environment()
    context.old_db_config = context.runner.setup_databases()
    from wsgi_intercept import mechanize_intercept
    browser = context.browser = mechanize_intercept.Browser()
    browser.set_handle_robots(False)


def after_scenario(context, scenario):
    context.runner.teardown_databases(context.old_db_config)
    context.runner.teardown_test_environment()
