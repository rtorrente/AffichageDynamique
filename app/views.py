from django.shortcuts import render
from django.views.generic import ListView
from .models import Feed, FeedGroup, Content
from django.contrib.auth.models import Group
from django.http import HttpResponseForbidden


class Home(ListView):
    model=Feed
    def get_queryset(self):
        if self.request.user.is_superuser:
            return Feed.objects.order_by("feed_group")
        else:
            return Feed.objects.filter(submitter_group__in=self.request.user.groups.all()).order_by("feed_group")

def content_list(request, pk):
    feed = Feed.objects.get(pk=pk)
    if feed.submitter_group not in request.user.groups.all() and not request.user.is_superuser:
        return HttpResponseForbidden()
    content = Content.objects.filter(feed=feed)
    return render(request, 'app/content_list.html', {"content": content})