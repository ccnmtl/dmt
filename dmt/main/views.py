from annoying.decorators import render_to
from .models import Project


@render_to('main/index.html')
def index(request):
    return dict(projects=Project.objects.all())
