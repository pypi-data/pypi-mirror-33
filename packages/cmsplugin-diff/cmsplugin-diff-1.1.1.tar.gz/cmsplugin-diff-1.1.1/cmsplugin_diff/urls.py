#
# Copyright 2015-2017, Martin Owens <doctormo@gmail.com>
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
app_name = 'cmsplugin_diff'


from django.conf.urls import url, include
try:
    from django.conf.urls import patterns
except ImportError:
    # Django>=1.10
    patterns = None
   
from .views import *

urlpatterns = [
    url(r'^$',             HistoryList.as_view(), name='site_history'),
    url(r'^unpublished/$', UnpublishedList.as_view(), name='site_unpublished'),

    url(r'^p(?P<page_id>\d+)/$',             PageHistoryList.as_view(), name='page_history'),
    url(r'^p(?P<page_id>\d+)/unpublished/$', PageUnpublishedList.as_view(), name='page_unpublished'),

    url(r'^p(?P<page_id>\d+)/p(?P<pk>\d+)/$', HistoryDetail.as_view(), name='publish_history'),
    url(r'^p(?P<page_id>\d+)/e(?P<pk>\d+)/$', EditingDetail.as_view(), name='editing_history'),
]

if patterns:
    urlpatterns = patterns('', *urlpatterns)
