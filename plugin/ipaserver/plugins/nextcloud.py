################################################################################
# nextcloud.py - FreeIPA plugin to enable / set a quota for nextcloud users
################################################################################
#
# Copyright (C) $( 2020 ) Radio Bern RaBe
#                    Switzerland
#                    http://www.rabe.ch
#
# This program is free software: you can redistribute it and/or
# modify it under the terms of the GNU Affero General Public
# License as published  by the Free Software Foundation, version
# 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License  along with this program.
# If not, see <http://www.gnu.org/licenses/>.
#
# Please submit enhancements, bugfixes or comments via:
# https://github.com/radiorabe/kanboard-tasks-from-email
#
# Authors:
#  Simon Nussbaum <smirta@gmx.net>
#
# --------------------------------------------------------------------------
# Adjustments 2021 Jasper Roloff <jasperroloff@gmail.com>
# - merge both plugins into one single plugin
# - restructure file
# - add FreeIPA permissions
# - add support for groups
# --------------------------------------------------------------------------
#
# Description:
# With this plugin a switch will be added to the ipa cli to allow users/groups to
# connect to nextcloud. It will set the Attribute nextcloudEnabled either to
# TRUE or FALSE.
#
# Also, a switch will be added to the ipa cli to set a quota for
# users connecting to nextcloud. It will set the Attribute nextcloudQuota.
# Allowed values are 'default' or an integer with 'MB', 'GB' etc.
#
#
# For this to work, extending the LDAP schema is required.
#
# Usage:
# ipa group-mod --nextcloudenabled=TRUE <groupname>
# ipa user-mod --nextcloudenabled=TRUE <username>
# ipa user-mod --nextcloudquota="100 MB" <username>
#

from ipaserver.plugins import user, group
from ipalib.parameters import Str, Bool
from ipalib.text import _


# for groups

def groupadd_precallback(self, ldap, dn, entry, attrs_list, *keys, **options):
    entry['objectclass'].append('nextcloudgroup')
    return dn


def groupmod_precallback(self, ldap, dn, entry, attrs_list, *keys, **options):
    if 'objectclass' not in entry.keys():
        old_entry = ldap.get_entry(dn, ['objectclass'])
        entry['objectclass'] = old_entry['objectclass']
    entry['objectclass'].append('nextcloudgroup')
    return dn


group.group.takes_params = group.group.takes_params + (
    Bool('nextcloudenabled?',
         cli_name='nextcloudenabled',
         label=_('Nextcloud enabled?'),
         doc=_('Whether or not a nextcloud is enabled for this group (default is false).'),
         default=False,
         autofill=True,
         ),
)
group.group_add.register_pre_callback(groupadd_precallback)
group.group_mod.register_pre_callback(groupmod_precallback)
group.group.default_attributes = group.group.default_attributes + ['nextcloudenabled']
group.group.managed_permissions = {**group.group.managed_permissions, **{
    'System: Read Group Nextcloud Attributes': {
        'ipapermbindruletype': 'anonymous',
        'ipapermright': {'read', 'search', 'compare'},
        'ipapermdefaultattr': {
            'nextcloudenabled'
        },
    },

    'System: Modify Group Nextcloud Attributes': {
        'ipapermbindruletype': 'permission',
        'ipapermright': {'write', 'add', 'delete'},
        'ipapermdefaultattr': {
            'nextcloudenabled'
        },
    },
}}


# for users

def useradd_precallback(self, ldap, dn, entry, attrs_list, *keys, **options):
    entry['objectclass'].append('nextclouduser')
    return dn


def usermod_precallback(self, ldap, dn, entry, attrs_list, *keys, **options):
    if 'objectclass' not in entry.keys():
        old_entry = ldap.get_entry(dn, ['objectclass'])
        entry['objectclass'] = old_entry['objectclass']
    entry['objectclass'].append('nextclouduser')
    return dn


user.user.takes_params = user.user.takes_params + (
    Bool('nextcloudenabled?',
         cli_name='nextcloudenabled',
         label=_('Nextcloud enabled?'),
         doc=_('Whether or not a nextcloud is enabled for this user (default is false).'),
         default=False,
         autofill=True,
         ),
    Str('nextcloudquota?',
        cli_name='nextcloudquota',
        label=_('Nextcloud Quota'),
        doc=_(
            'Defines Nextcloud quota in Bytes. Allowed values are "none", "default", e.g. "1024 MB" (default is "default").'),
        default=u'default',
        autofill=True,
        pattern='^(default|none|[0-9]+ [MGT]B)$',
        pattern_errmsg='may only be "none", "default" or a number of mega-, giga- or terabytes (e.g. 1024 MB)',
        ),
)

user.user.default_attributes = user.user.default_attributes + ['nextcloudquota', 'nextcloudenabled']
user.user_add.register_pre_callback(useradd_precallback)
user.user_mod.register_pre_callback(usermod_precallback)
user.user.managed_permissions = {**user.user.managed_permissions, **{
    'System: Read User Nextcloud Attributes': {
        'ipapermbindruletype': 'anonymous',
        'ipapermright': {'read', 'search', 'compare'},
        'ipapermdefaultattr': {
            'nextcloudenabled', 'nextcloudquota'
        },
    },

    'System: Modify User Nextcloud Attributes': {
        'ipapermbindruletype': 'permission',
        'ipapermright': {'write', 'add', 'delete'},
        'ipapermdefaultattr': {
            'nextcloudenabled', 'nextcloudquota'
        },
    },
}}
