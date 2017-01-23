from django.conf import settings


def graphite_base_processor(request):
    return {
        'GRAPHITE_BASE': settings.GRAPHITE_BASE,
    }


def dashboard_graph_timespan(request):
    return {
        'DASHBOARD_GRAPH_TIMESPAN': settings.DASHBOARD_GRAPH_TIMESPAN,
    }
