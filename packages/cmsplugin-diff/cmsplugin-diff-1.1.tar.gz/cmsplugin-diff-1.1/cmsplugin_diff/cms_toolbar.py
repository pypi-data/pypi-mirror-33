#
# Copyright 2017, Martin Owens <doctormo@gmail.com>
#
# This file is part of the software inkscape-web, consisting of custom 
# code for the Inkscape project's django-based website.
#
# inkscape-web is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# inkscape-web is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with inkscape-web.  If not, see <http://www.gnu.org/licenses/>.
#
"""
Provide links to see a page's history from the cms toolbar.
"""

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from cms.toolbar_pool import toolbar_pool
from cms.toolbar_base import CMSToolbar
from cms.cms_toolbars import PAGE_MENU_IDENTIFIER

@toolbar_pool.register
class DiffToolbar(CMSToolbar):
    def populate(self):
        menu = self.toolbar.get_menu(PAGE_MENU_IDENTIFIER)
        if menu is None:
            return

        if hasattr(self.request.current_page, '_wrapped'):
            page = self.request.current_page._wrapped
        else:
            page = self.request.current_page

        if page.publisher_is_draft:
            draft = page
            public = page.publisher_public
        else:
            draft = page.publisher_draft
            public = page

        menu.add_break('DIFF_MENU_BREAK')
        if public is not None and public.publish_history.count() > 0:
            menu.add_modal_item(_('Published History'), url=public.publish_history.get_absolute_url())
        else:
            menu.add_modal_item(_('Published History'), disabled=True, url=None)

        if draft is not None and draft.edit_history.filter(published_in__isnull=True).count() > 0:
            menu.add_modal_item(_('Unpublished Edits'), url=draft.edit_history.get_absolute_url())
        else:
            menu.add_modal_item(_('Unpublished Edits'), disabled=True, url=None)

