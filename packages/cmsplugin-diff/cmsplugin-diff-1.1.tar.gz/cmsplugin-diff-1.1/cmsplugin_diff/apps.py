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
Connect app signals for history recording.
"""
import sys

from django.apps import AppConfig as BaseConfig
from django.utils.translation import get_language
from django.contrib.auth import get_user_model
from django.core.cache import cache

from django.db.models import signals

from .utils import generate_content

class AppConfig(BaseConfig):
    name = 'cmsplugin_diff'
    verbose_name = "CMS Diff"

    def ready(self):
        if 'loaddata' in sys.argv:
            return
        from cms.models import CMSPlugin, Page
        from cms.signals import post_publish
        from .cms_toolbar import DiffToolbar
        signals.pre_save.connect(self.ensure_initial)
        signals.post_save.connect(self.record_plugin_history)
        post_publish.connect(self.record_history, sender=Page)

    def ensure_initial(self, sender, instance, **kwargs):
        """Ensure there is a previous history object"""
        from cms.models import CMSPlugin, Page
        from .models import EditHistory, PublishHistory
        if not (isinstance(instance, CMSPlugin) and instance.id):
            # Idn't a plugin or is being created
            return

        # We're looking at an initalisation request.
        history = EditHistory.objects.filter(plugin_id=instance.id)
        if history.count() > 0:
            return

        # We don't want to modified version, but the original one
        try:
            instance = type(instance).objects.get(pk=instance.id)
        except type(instance).DoesNotExist:
            return
        content = generate_content(instance)
        if content is None:
            return

        # So what's happened here, is that there is an existing plugin
        # that existed BEFORE this plugin was being used. So we're going
        # to track the initial state of the plugin, before it's changed.
        User = get_user_model()
        # We would use changed_by, but django-cms converts user id to First
        # and Last name, not even username. Making that field useless.
        (user, _) = User.objects.get_or_create(username='cms-user')

        public = instance.page.publisher_public
        kwargs = dict(page=public, language=get_language())
        publishings = PublishHistory.objects.filter(**kwargs)
        if publishings.count() == 0:
            kwargs['defaults'] = dict(user=user, date=public.changed_date)
            (pub, _) = PublishHistory.objects.get_or_create(**kwargs)
        else:
            # Get the first one created which should be the initial version.
            pub = publishings.latest('date')

        # Note: Do not make 'Inital' comment translatable.
        return EditHistory.objects.record(instance, user.id, 'Initial', content, pub)

    def record_plugin_history(self, sender, instance, **kwargs):
        """When a plugin is created or edited"""
        from cms.models import CMSPlugin, Page
        from .models import EditHistory
        if not isinstance(instance, CMSPlugin):
            return

        user_id = cache.get('cms-user-id')
        comment = cache.get('cms-comment')
        content = generate_content(instance)
        if content is None:
            return

        # Don't record a history of change if nothing changed.
        history = EditHistory.objects.filter(plugin_id=instance.id)
        if history.count() > 0:
            # Temporary history object for uuid
            this = EditHistory(content=content)
            latest = history.latest()
            if latest.content == content or this.uuid == latest.uuid:
                return

        EditHistory.objects.record(instance, user_id, comment, content)

    def record_history(self, sender, instance, **kwargs):
        """When a page is published, make a new PublishHistory object"""
        from .models import EditHistory, PublishHistory

        # Make sure we have the draft version.
        if not instance.publisher_is_draft:
            instance = publisher_draft

        editings = EditHistory.objects.filter(
            page_id=instance.id,
            published_in__isnull=True,
        )

        if editings.count() == 0:
            # No changes happened, skip!
            return

        public = instance.publisher_public
        user_id = cache.get('cms-user-id')

        history = PublishHistory.objects.create(
            page=public, user_id=user_id, language=get_language())
        history.editings = editings
        history.save()

