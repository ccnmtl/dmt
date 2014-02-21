from django import template
from dmt.claim.models import Claim

register = template.Library()


class DummyPMTUser(object):
    """ all we need to do is direct them to the page
    to claim their account """
    def get_absolute_url(self):
        return "/claim/"


class PMTUserNode(template.Node):
    def __init__(self, var_name):
        self.var_name = var_name

    def render(self, context):
        if 'request' not in context:
            return ''
        u = context['request'].user
        r = Claim.objects.filter(django_user=u)
        if r.count() > 0:
            context[self.var_name] = r[0].pmt_user
        else:
            context[self.var_name] = DummyPMTUser()
        return ''


@register.tag('pmtuser')
def pmtuser(parser, token):
    var_name = token.split_contents()[1:][1]
    return PMTUserNode(var_name)
