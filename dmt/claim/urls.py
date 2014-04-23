from django.conf.urls import patterns

urlpatterns = patterns(
    'dmt.claim.views',
    (r'^$', 'index'),
)
