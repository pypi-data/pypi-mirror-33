#
# Copyright 2013, Martin Owens <doctormo@gmail.com>
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
"""Alerts urls"""

from django.conf.urls import url, include
from .views import (
    SettingsList, MarkAllViewed, MarkAllDeleted, MarkViewed,
    MarkDeleted, AlertList, AlertsJson, SentMessages, Subscribe, Unsubscribe
)

def url_tree(regex, *urls):
    """Provide a way to extend patterns easily"""
    class UrlTwig(object): # pylint: disable=too-few-public-methods, missing-docstring
        urlpatterns = urls
    return url(regex, include(UrlTwig))

urlpatterns = [ # pylint: disable=invalid-name
    url(r'^$', AlertList.as_view(), name="alerts"),
    url(r'^json/$', AlertsJson.as_view(), name="alerts.json"),
    url(r'^view/$', MarkAllViewed.as_view(), name="alert.view"),
    url(r'^outbox/$', SentMessages.as_view(), name="message.outbox"),
    url(r'^delete/$', MarkAllDeleted.as_view(), name='alert.delete'),
    url(r'^settings/$', SettingsList.as_view(), name='alert.settings'),

    url_tree(
        r'^(?P<pk>\d+)/',
        url(r'^delete/', MarkDeleted.as_view(), name='alert.delete'),
        url(r'^view/', MarkViewed.as_view(), name="alert.view"),
    ),
    url_tree(
        r'^(?P<slug>[^\/]+)/',
        url(r'^$', AlertList.as_view(), name="alert.category"),
        url_tree(
            r'^subscribe/',
            url(r'^$', Subscribe.as_view(), name='alert.subscribe'),
            url(r'^(?P<pk>\d+)/$', Subscribe.as_view(), name='alert.subscribe'),
        ),
        url_tree(
            r'^unsubscribe/',
            url(r'^$', Unsubscribe.as_view(), name='alert.unsubscribe'),
            url(r'^(?P<pk>\d+)/$', Unsubscribe.as_view(), name='alert.unsubscribe'),
        ),
    ),
]
