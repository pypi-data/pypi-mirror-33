#
# Copyright 2017, Martin Owens <doctormo@gmail.com>
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
from django.contrib.admin import ModelAdmin, TabularInline, site

from .models import *

def page_label(obj):
    if obj.page.publisher_is_draft:
        return str(obj.page) + " (draft)"
    return str(obj.page) + " (live)"


class EditAdmin(ModelAdmin):
    readonly_fields = ('user', 'page', 'plugin_id', 'published_in', 'date')
    list_display = ('plugin_id', '_page', 'comment', 'user', 'date', 'is_published')

    def is_published(self, obj):
        return bool(obj.published_in)
    is_published.boolean = True
    _page = staticmethod(page_label)

site.register(EditHistory, EditAdmin)

class EditsInline(TabularInline):
    fields = ['user', 'plugin_id', 'comment',]
    readonly_fields = ['user',]
    model = EditHistory
    extra = 0

class PublishAdmin(ModelAdmin):
    readonly_fields = ('user', 'page', 'language')
    list_display = ('_page', 'user', 'date', 'language')
    list_filter = ('language',)
    inlines = [EditsInline]

    _page = staticmethod(page_label)

site.register(PublishHistory, PublishAdmin)

