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
"""
Convert plugin data into storable json content and convert that content
into a structured diff list of changes.
"""

import json

from codecs import lookup_error, register_error
from html.entities import codepoint2name
from diff_match_patch import diff_match_patch
differ = diff_match_patch()

from django.utils.safestring import mark_safe
from django.utils.encoding import force_text
from django.utils.html import strip_tags, strip_spaces_between_tags, linebreaks
from django.utils.translation import ugettext_lazy as _

#
# ACTION_DELETE - Exited in A, but was deleted in B
# ACTION_NONE   - Exists in both, but is the same (no change)
# ACTION_CHANGE - Exists in both and is different (changes)
# ACTION_CREATE - Doesn't exist in A, and so was created in B
#
(ACTION_DELETE, ACTION_NONE, ACTION_CHANGE, ACTION_CREATE) = range(-1, 3)

# A list of cms plugin fields which will be ignored in the diff output.
IGNORE_ALWAYS = ('id', 'changed_date', 'cmsplugin_ptr', 'numchild', 'alias_reference')
# Like ignore always, but shows if the value has changed
IGNORE_SAME = ('language', 'creation_date', 'depth', 'position', 'path', 'plugin_type')

def is_str(var):
    return isinstance(var, str)

def clean_text(text):
    return strip_tags(force_text(text)).replace("\n\n\n", "\n\n").strip()

def generate_content(plugin):
    """
    Generates the raw content structure for this plugin. It's a json
    encoded text string which contains a record of each of the plugin's
    fields.
    """
    if not plugin.placeholder_id:
        # If it's not a part of a page
        return

    if not plugin.page or not plugin.page.publisher_is_draft:
        # If it's a live page, we don't want to know.
        return

    # Resolve the actual plugin object
    (obj, plugin) = plugin.get_plugin_instance()
    if obj is None:
        return

    fields = {}
    bodies = {}

    for field in type(obj)._meta.get_fields():
        name = field.name
        if not hasattr(obj, name):
            continue
        value = getattr(obj, name, None)
        if value is not None:
            if not isinstance(value, (int, float)):
                value = clean_text(value).encode('ascii', 'htmlnamerefreplace')
            if isinstance(value, str) and '\n' in value:
                fields[name] = value.replace('\r\n', '\n')
            else:
                fields[name] = value

    if not fields and not bodies:
        return None

    return json.dumps({
        'fields': fields,
    }, sort_keys=True, indent=2)


def get_diff(content_a, content_b):
    """
    Decontructs the json created in generate_content and produces an structured
    output showing the difference between the two. This can be either field
    to field comparisons or a body diff for multi-line fields.

    Bodies are pre-compiled into a diff html if the action is 'changed' and
    will show the existing content for other actions.

    {
      'fields': [
        {
          'key': 'name-of field',
          'changed': True,
          'action': 'changed',
          'content': {
            'before': 'ABC',
            'after': '123',
          },
        },
        ...
      ],
      'bodies': [
        {
          'key': 'name-of-body',
          'changed': True,
          'action': 'changed',
          'content': '<ins>123</ins><del>ABC</del>'
        },
        ...
      ],
    """
    fields = []
    bodies = []

    try:
        fields_a =  json.loads(content_a)['fields']
    except ValueError:
        return diff_error(_('Old record is broken, diff unavailable.'))
    except KeyError:
        if content_a != '{}':
            return diff_error(_('Old record is missing, diff unavailable. %s'))
        # When histories are first created, all fields are created.
        fields_a = {}

    try:
        fields_b =  json.loads(content_b)['fields']
    except KeyError:
        return diff_error(_('New record is missing, diff unavailable.'))
    except ValueError:
        return diff_error(_('New record is broken, diff unavailable.'))

    for key, a, b, action in field_diff(fields_a, fields_b):
        if key in IGNORE_ALWAYS:
            continue # We don't want to see this field.

        ac_name = ['unchanged', 'changed', 'created', 'deleted'][action]
        packet = {
            'key': key,
            ac_name: True,
            'action': ac_name,
            'content': [a, 'to_be_filled', b, a][action],
        }

        if (is_str(a) and '\n' in a) or (is_str(b) and '\n' in b):
            if action == ACTION_CHANGE:
                diff = differ.diff_main(a, b)
                differ.diff_cleanupSemantic(diff)
                html = differ.diff_prettyHtml(diff)
                packet['content'] = html.replace('&para;','')
            bodies.append(packet)

        else:
            if action == ACTION_CHANGE:
                packet['content'] = {'before': a, 'after': b}

            if action != ACTION_NONE or key not in IGNORE_SAME:
                fields.append(packet)

    return {'fields': fields, 'bodies': bodies}


def diff_error(msg):
    return {'fields': [
      {
        'key': 'Error Loading Diff',
        'content': msg,
        'error': True,
        'action': 'error',
      },
    ]}

def field_diff(a, b):
    """
    Loop through a collection of fields and return an generator which
    contains the key, A and B values as well as the 'action', this can be:

      See ACTION enumeration above.

    """
    set_a = set(a)
    set_b = set(b)
    not_both = set_a ^ set_b

    # Key is in both sets
    for key in set_a & set_b:
        if a[key] == b[key]:
            yield key, a[key], b[key], ACTION_NONE
        else:
            yield key, a[key], b[key], ACTION_CHANGE

    # Only in A (deletes)
    for key in not_both & set_a:
        yield key, a[key], None, ACTION_DELETE

    # Only in B (creates)
    for key in not_both & set_b:
        yield key, None, b[key], ACTION_CREATE


def stub_text(stub):
    """Returns a html of the stub text""" 
    return mark_safe(stub.replace('<span>', '\n\n').replace('</span>', '')\
                  .replace('<del style="background:#ffe6e6;">', '<--').replace('</del>', '-->')\
                  .replace('<ins style="background:#e6ffe6;">', '<++').replace('</ins>', '++>'))

def stub(diffs):
    diffs = [o for d in diffs for o in d]
    return differ.diff_prettyHtml(get_segment(diffs)).replace('&para;','')


def get_segment(diffs):
    """Returns the first section of the diff as a stub"""
    size = 1024
    cleaned = stem_diff(diffs)
    tot = 0
    for (op, text) in cleaned:
        tot += len(text)
        if tot > size:
            break
        yield (op, text)

def stem_diff(diffs):
    left_size = 10
    right_size = 10
    # First step is to stem non-changed parts with elipsis
    for x, (op, text) in enumerate(diffs):
        if op == 0:
            lines = text.splitlines()
            if len(lines) == 0:
                continue

            if len(lines) == 1 and len(text) <= left_size + right_size \
              and x > 0 and x < len(diffs):
                yield (op, text)
                continue

            if x > 0:
                if len(lines[0]) > left_size:
                    yield (op, lines[0][:left_size] + "...")
                else:
                    yield (op, lines[0])

            if x < len(diffs):
                if len(lines[-1]) > right_size:
                    yield (op, "..." + lines[-1][-right_size:])
                else:
                    yield (op, lines[-1])
        else:
            yield (op, text)

#
# This section probably exists elswhere, but I couldn't find it.
# so what this does it take a unicode and replaces the numerical
# html encoding from xmlcharrefreplace and replaces them with
# named varients from codepoint2name where available. 
#
# This turns &#160; into &nbsp; for example.
#
names = dict([(u'&#%d;' % a, u'&%s;' % b) for a, b in codepoint2name.items()])
xcrr = lookup_error('xmlcharrefreplace')

def htmlnamerefreplace(exc):
    ret = xcrr(exc)
    return (names.get(ret[0], ret[0]), ret[1])

register_error('htmlnamerefreplace', htmlnamerefreplace)

