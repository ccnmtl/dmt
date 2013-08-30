from django.conf.urls.defaults import patterns

urlpatterns = patterns(
    'dmt.claim.views',
    (r'^$', 'index'),
)
