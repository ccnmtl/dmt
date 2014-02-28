from annoying.decorators import render_to
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django_statsd.clients import statsd
from .models import Claim, PMTUser, all_unclaimed_pmt_users


@login_required
@render_to('claim/index.html')
def index(request):
    """ TODO: convert this to View"""
    if request.method == "POST":
        username = request.POST['user']
        pmt_user = get_object_or_404(PMTUser, username=username)
        Claim.objects.create(
            django_user=request.user,
            pmt_user=pmt_user)
        statsd.incr('claim.user_claimed')
        return HttpResponseRedirect("/claim/")
    else:
        r = Claim.objects.filter(django_user=request.user)
        data = dict()
        data['found'] = r.count() > 0
        if r.count() > 0:
            data['pmt_user'] = r[0].pmt_user
        else:
            data['available_users'] = all_unclaimed_pmt_users()
            likely = (
                PMTUser.objects.filter(username=request.user.username) |
                PMTUser.objects.filter(
                    fullname__iexact=request.user.get_full_name()))
            if likely.count() == 1:
                data['likely'] = likely[0].username
            else:
                data['likely'] = None
        return data
