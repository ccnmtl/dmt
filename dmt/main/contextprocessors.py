from django.conf import settings


def graphite_base_processor(request):
    return {
        'GRAPHITE_BASE': settings.GRAPHITE_BASE,
    }
