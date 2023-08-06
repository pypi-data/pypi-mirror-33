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
"""
Record each page publish change.

This is a log of what happened and is NOT an undo and redo functionality.

"""
import json

from django.db.models import Model, Manager, SET, SET_NULL,\
    ForeignKey, DateTimeField, CharField, TextField, IntegerField

from django.utils.translation import ugettext_lazy as _, get_language
from django.core.urlresolvers import reverse
from django.contrib.auth import get_user_model
from django.conf import settings

from cms.models import Page
from .utils import get_diff

def get_deleted_user():
    """Replace user when needed"""
    return get_user_model().objects.get_or_create(username='deleted')[0]

REMOVABLE_USER = dict(on_delete=SET(get_deleted_user))
REMOVABLE_PAGE = dict(on_delete=SET_NULL, null=True)

class RedirectUrl(object):
    """
    Generic redirect url mixin that takes the queryset and returns
    the best url match, sometimes this might be the whole list, sometimes
    it's a per-page result.
    """
    def get_absolute_url(self):
        qs = self.get_queryset()
        if qs.count() == 1:
            return qs.get().get_absolute_url()
        if self.page:
            kw = dict(page_id=self.page.pk)
            return reverse('cmsplugin_diff:%s' % self.page_url, kwargs=kw)
        return reverse('cmsplugin_diff:%s' % self.site_url)

    @property
    def page(self):
        obj = self.get_queryset()._hints.get('instance', None)
        if isinstance(obj, Page):
            return obj

    @property
    def title(self):
        if self.page is not None:
            return str(self.page)
        return self.page_title

class EditManager(RedirectUrl, Manager):
    """Manage edit records"""
    page_title = _('Unpublished Edits')
    page_url = 'page_unpublished'
    site_url = 'site_unpublished'

    def unpublished_details(self):
        """Collate some figures together for display"""
        qset = self.filter(published_in__isnull=True)
        langs, users, comments, dates = zip(*qset.values_list(
            'language', 'user_id', 'comment', 'date'))
        return {
            'languages': langs,
            'comments': comments,
            'users': [get_user_model().objects.get(pk=pk) for pk in users],
            'dates': dates,
        }

    def record(self, plugin, user_id, comment, content, publish=None):
        """Standard history creation"""
        return self.create(user_id=user_id, plugin_id=plugin.pk, comment=comment,
                           content=content, page=plugin.placeholder.page,
                           language=get_language(), published_in=publish)


class SiblingMixin(object):
    """A generic mixin returning next and previous objects in the chain"""
    @property
    def siblings(self):
        """Returns a list of all plugin edits for this plugin"""
        qset = type(self).objects.filter(language=self.language)
        return qset.filter(**{self.unique_col: getattr(self, self.unique_col)})

    @property
    def previous(self):
        """Returns the previous History or a blank object"""
        return self._get_sibling('lt', '-date')

    @property
    def next(self):
        """Returns the next History or a blank object"""
        return self._get_sibling('gt', 'date')

    def _get_sibling(self, direction, order):
        """Returns either next or previous sibling in the chain of edits"""
        #raise NotImplementedError("_get_sibling must be created in model")
        qset = self.siblings.filter(**{'date__' + direction: self.date})
        if qset.count() > 0:
            return qset.order_by(order)[0]
        return type(self)()


class PublishManager(RedirectUrl, Manager):
    """Manage published histories"""
    page_title = _('Histories')
    page_url = 'page_history'
    site_url = 'site_history'

class EditHistory(Model, SiblingMixin):
    """Each time a page is edited (but not published) record the changes"""
    user = ForeignKey(settings.AUTH_USER_MODEL, **REMOVABLE_USER)
    page = ForeignKey(Page, related_name='edit_history', **REMOVABLE_PAGE)
    date = DateTimeField(auto_now_add=True, db_index=True)

    # We're not linking the plugin with a foreign key, we don't
    # want history to disappear when plugins are deleted.
    unique_col = 'plugin_id'
    plugin_id = IntegerField(db_index=True)
    comment = CharField(_("User Comment"), max_length=255, null=True)
    content = TextField(_("Current Plugin Content"), default='{}')
    language = CharField(_("Plugin Language"), max_length=8,
                         null=True, choices=settings.LANGUAGES)

    published_in = ForeignKey('PublishHistory',
                              related_name='editings', null=True, blank=True)

    objects = EditManager()

    class Meta:
        ordering = ('-date',)
        get_latest_by = 'date'
        verbose_name = 'Plugin History'
        verbose_name_plural = 'Plugin Histories'

    def __str__(self):
        if self.published_in:
            return _("Editing event #%d") % self.pk
        return _("Unpublished change #%d") % self.pk

    def get_absolute_url(self):
        """Return a link to this editing history"""
        kwargs = dict(page_id=self.page_id, pk=self.pk)
        return reverse('cmsplugin_diff:editing_history', kwargs=kwargs)

    @property
    def diff(self):
        """Return the get_diff between the previous and this content"""
        return get_diff(self.previous.content, self.content)

    @property
    def uuid(self):
        """
        Attempt to secure a uuid on the plugin's edit to prevent duplicate
        entries. We use the changed_date and remove it's precision to the
        nearest minute to discount any other odd effects.
        """
        return json.loads(self.content)['fields']['changed_date']\
                .split('.')[0].rsplit(':', 1)[0]


class PublishHistory(Model, SiblingMixin):
    """History of the publishing of pages"""
    user = ForeignKey(settings.AUTH_USER_MODEL, **REMOVABLE_USER)
    page = ForeignKey(Page, related_name='publish_history', **REMOVABLE_PAGE)
    date = DateTimeField(auto_now_add=True, db_index=True)
    unique_col = 'page_id'

    language = CharField(_("Page Language"), max_length=8,
                         null=True, choices=settings.LANGUAGES)

    objects = PublishManager()

    def __str__(self):
        return _("Publishing event #%d") % self.pk

    class Meta:
        ordering = ('-date',)
        get_latest_by = 'date'
        verbose_name = 'Page History'
        verbose_name_plural = 'Page Histories'

    def get_absolute_url(self):
        """Return a link to this history's content"""
        kwargs = dict(page_id=self.page_id, pk=self.pk)
        return reverse('cmsplugin_diff:publish_history', kwargs=kwargs)

    @property
    def users(self):
        """Returns a list of users involved in this publishing"""
        ret = set([])
        for edit in self.editings.all():
            ret.add(edit.user)
        return ret

    @property
    def languages(self):
        """Returns a set of unqiue languages involved"""
        return set([edt.get_language_display() for edt in self.editings.all()])

    @property
    def comments(self):
        """Concatinates all comments into one"""
        return "\n".join([edit.comment for edit in self.editings.all()])
