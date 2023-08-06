#
# Copyright 2015, Martin Owens <doctormo@gmail.com>
#
# cmsplugin-diff is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# cmsplugin-diff is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with cmsplugin-diff.  If not, see <http://www.gnu.org/licenses/>.
#
"""
Show the diff pages for changes to the django-cms pages.
"""

from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView, DetailView, TemplateView
from django.core.urlresolvers import reverse
from django.db.models import Count
from cms.models import Page

from .models import EditHistory, PublishHistory

class AdminBase(object):
    def get_context_data(self, **kw):
        data = super(AdminBase, self).get_context_data(**kw)
        data['opts'] = self.model._meta
        data['title'] = getattr(self, 'title', None)
        data['parents'] = self._get_parents(data['object'])
        return data

    def _get_parents(self, obj):
        return [PublishHistory.objects] + self.get_parents(obj)

    def get_parents(self, obj):
        return []

    @property
    def title(self):
        return str(self.get_object())


class HistoryList(AdminBase, ListView):
    title = PublishHistory.objects.page_title
    model = PublishHistory
    template_name = 'cmsplugin_diff/site_history_list.html'

    def get_queryset(self):
        qs = super(HistoryList, self).get_queryset()
        return qs.order_by('page_id', '-date')

    def _get_parents(self, obj):
        return [] # No parent, this is the root

    def get_context_data(self, **kw):
        data = super(HistoryList, self).get_context_data(**kw)
        data['edits_list'] = UnpublishedList.get_queryset()
        return data


class UnpublishedList(AdminBase, ListView):
    title = EditHistory.objects.page_title
    model = Page
    template_name = 'cmsplugin_diff/site_unpublished_list.html'

    @staticmethod
    def get_queryset():
        qs = Page.objects.all()
        return qs.filter(edit_history__published_in__isnull=True)\
                .annotate(edits=Count('edit_history')).filter(edits__gt=0)\
                .order_by('-edit_history__date')


class PageHistoryList(AdminBase, DetailView):
    model = Page
    pk_url_kwarg = 'page_id'
    template_name = 'cmsplugin_diff/page_history_list.html'


class PageUnpublishedList(AdminBase, ListView):
    model = EditHistory
    template_name = 'cmsplugin_diff/page_unpublished_list.html'

    def get_queryset(self):
        return self.get_object().edit_history.filter(published_in__isnull=True)

    def get_object(self):
        return Page.objects.get(pk=self.kwargs['page_id'])

    def get_parents(self, obj):
        return [EditHistory.objects]

    @property
    def title(self):
        return _("Unpublished Edits for %s") % str(self.get_object())


class HistoryDetail(AdminBase, DetailView):
    model = PublishHistory
    template_name = 'cmsplugin_diff/published_history.html'

    def get_queryset(self):
        qs = super(HistoryDetail, self).get_queryset()
        return qs.filter(page_id=self.kwargs['page_id'])

    def get_parents(self, obj):
        return [obj.page.publish_history]


class EditingDetail(AdminBase, DetailView):
    model = EditHistory
    template_name = 'cmsplugin_diff/editing_history.html'

    def get_queryset(self):
        qs = super(EditingDetail, self).get_queryset()
        return qs.filter(page_id=self.kwargs['page_id'])

    def get_parents(self, obj):
        if obj.published_in:
            return [
                obj.published_in.page.publish_history,
                obj.published_in,
            ]
        return []
