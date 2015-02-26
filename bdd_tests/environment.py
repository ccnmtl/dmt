import urlparse
from splinter import Browser


def before_all(context):
    host = context.host = 'localhost'
    port = context.port = 8081
    context.browser = Browser(context.config.browser or 'firefox')

    def browser_url(url):
        return urlparse.urljoin('http://%s:%d/' % (host, port), url)

    context.browser_url = browser_url


def after_all(context):
    context.browser.quit()


def before_scenario(context, scenario):
    pass


def after_scenario(context, scenario):
    pass
