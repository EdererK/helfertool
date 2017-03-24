from django.db.models import Count
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from collections import OrderedDict

from registration.views.utils import nopermission

from registration.decorators import archived_not_available
from registration.models import Event, Helper


class JobShirts:
    def __init__(self, shirt_choices):
        self.shifts = OrderedDict()
        self.total = OrderedDict()
        self.coordinators = OrderedDict()

        for size, name in shirt_choices:
            self.total.update({name: 0})
            self.coordinators.update({name: 0})


@login_required
@archived_not_available
def shirts(request, event_url_name):
    event = get_object_or_404(Event, url_name=event_url_name)
    shirt_choices = event.get_shirt_choices()

    # permission
    if not event.is_involved(request.user):
        return nopermission(request)

    # check if shirt sizes are collected for this event
    if not event.ask_shirt:
        context = {'event': event}
        return render(request, 'statistic/shirts_not_active.html', context)

    # size names
    size_names = [name for size, name in shirt_choices]

    # shirt sizes
    helper_shirts = event.helper_set.values('shirt').annotate(
        num=Count('shirt'))

    # total numbers (iterate over all sizes in correct order)
    total_shirts = OrderedDict()
    for size, name in shirt_choices:
        num = 0

        # get size for helpers
        try:
            num = helper_shirts.get(shirt=size)['num']
        except Helper.DoesNotExist:
            pass

        total_shirts.update({name: num})

    # for each job
    job_shirts = OrderedDict()
    for job in event.job_set.all():
        sizes_for_job = JobShirts(shirt_choices)
        # for each shift
        for shift in job.shift_set.all():
            sizes_for_shift = shift.shirt_sizes
            sizes_for_job.shifts.update({shift: sizes_for_shift})

            # update total number
            for size, name in shirt_choices:
                num = sizes_for_job.total[name]
                sizes_for_job.total.update({name: num+sizes_for_shift[name]})
        job_shirts.update({job: sizes_for_job})

    # render
    context = {'event': event,
               'size_names': size_names,
               'total_shirts': total_shirts,
               'job_shirts': job_shirts}
    return render(request, 'statistic/shirts.html', context)