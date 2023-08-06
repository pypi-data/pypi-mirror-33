#
# Copyright 2016-2017, Martin Owens <doctormo@gmail.com>
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
When editing and creating cmsplugins, we want to record the comment.
"""

import logging
from django.core.cache import cache

try:
    # From django 1.10 upwards, we have a new style middleware
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    class MiddlewareMixin(object):
        pass


class EditCommentMiddleware(MiddlewareMixin):
    """
    Save any comment submitted with an editing.
    """
    def process_request(self, request):
        if request.method == 'POST' and '/admin/cms/' in request.path_info:
            if 'comment' in request.POST:
                cache.set('cms-comment', request.POST['comment'])
            else:
                cache.set('cms-comment', "")
            cache.set('cms-user-id', request.user.id)

