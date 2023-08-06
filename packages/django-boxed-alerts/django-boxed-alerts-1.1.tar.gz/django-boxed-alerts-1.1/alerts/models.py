#
# Copyright 2014-2017, Martin Owens <doctormo@gmail.com>
#
# django-boxed-alerts is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# django-boxed-alerts is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with django-boxed-alerts.  If not, see <http://www.gnu.org/licenses/>.
#
"""Record alerts in the database"""

from collections import defaultdict

from django.contrib.auth import get_user_model
from django.conf import settings

from django.db.models import (
    Model, Manager, QuerySet, Q, TextField, CharField,
    ForeignKey, BooleanField, DateTimeField, PositiveIntegerField,
)

from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now

from django.contrib.auth.models import Group
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django.core.urlresolvers import reverse
from django.core.validators import MaxLengthValidator
from django.core.mail.message import EmailMultiAlternatives
from django.utils import translation

from alerts.template_tools import render_template

BATCH_MODES = (
    (None, _("Instant")),
    ("D", _("Daily")),
    ("W", _("Weekly")),
    ("M", _("Monthly")),
)


class AlertTypeManager(Manager):
    """Manage alert types, ensuring only one type per base is created in the db"""
    def get_by_natural_key(self, slug):
        """Returns the natural key for AlertTypes"""
        return self.get(slug=slug)

    def get_or_create(self, values=None, **kwargs):
        """Allow the AlertType to be updated with code values
           (should only be run on new code load or server restart)"""
        if values and 'defaults' not in kwargs:
            kwargs['defaults'] = values
        (obj, created) = super(AlertTypeManager, self).get_or_create(**kwargs)
        if not created and values:
            self.filter(pk=obj.pk).update(**values)
        return (obj, created)

    def get_queryset(self):
        """ALWAYS limit alert types to those available"""
        from alerts.base import BaseAlert
        qset = super(AlertTypeManager, self).get_queryset()
        return qset.filter(slug__in=list(BaseAlert.instances))


class AlertType(Model):
    """All Possible messages that users can receive, acts as a template"""
    slug = CharField(_("URL Slug"), max_length=128, unique=True)
    group = ForeignKey(Group, verbose_name=_("Limit to Group"), blank=True, null=True)

    created = DateTimeField(_("Created Date"), auto_now_add=now)
    enabled = BooleanField(default=False)

    # These get copied into UserAlertSettings for this alert
    default_email = BooleanField(default=False)
    default_batch = CharField(max_length=1, choices=BATCH_MODES, blank=True, null=True)
    default_irc = BooleanField(default=False)

    objects = AlertTypeManager()

    breadcrumb_parent = staticmethod(lambda self: (reverse('alerts'), _('Inbox')))

    @property
    def _alerter(self):
        # Late import to stop loop import
        from alerts.base import BaseAlert
        return BaseAlert.instances[self.slug].connect_signals()

    def __getattr__(self, name):
        if hasattr(self._alerter, name):
            return getattr(self._alerter, name)
        return getattr(super(AlertType, self), name)

    def send_to(self, user, auth=None, **kwargs):
        """Creates a new alert for a certain user of this type.

         user   - The user this alert should be addressed to. (required)
                  can also be a group, where upon each member of the group
                  will be messaged (be careful with this).
         auth   - Super user to authorise the sending of an alert to everyone
         kwargs - Dictionary of objects used in the rendering of the subject
                  and body templates.

         Returns new UserAlert object or None if user isn't allowed this alert.

        """
        if not self.enabled:
            return []
        if isinstance(user, Group):
            users = user.users
        elif isinstance(user, get_user_model()):
            users = [user]
        elif user == 'all':
            if not isinstance(auth, get_user_model()) or not auth.is_superuser:
                raise ValueError("You are not authorized to send an alert to everyone.")
            users = get_user_model().objects.all()
        else:
            raise ValueError("You must specify a user or group to send an alert to.")

        return [self._send_to(real_user, **kwargs) for real_user in users]

    def _send_to(self, user, **kwargs):
        if self.enabled and (not self.group or self.group in user.groups):
            if 'instance' in kwargs and 'once' in kwargs:
                # Check if the instance has already been issued to this user's alerts.
                i = kwargs['instance']
                existing = UserAlert.objects.filter(
                    user=user, alert=self,
                    objs__o_id=i.pk, objs__name='instance',
                    deleted__isnull=True, viewed__isnull=True)
                if existing.count():
                    return None
            alert = UserAlert(user=user, alert=self)
            alert.save()
            for (key, value) in kwargs.items():
                alert.add_value(key, value)
            # Do this after saving objects and values so email can use them.
            if alert.config.batch is None:
                alert.send_email(context_data=kwargs)
            alert.send_irc_msg()
            return alert
        return None

    def subscribe_url(self, obj=None):
        """Return the url to subscribe to the given object"""
        return self.alert_url('subscribe', pk=(obj and obj.pk), slug=self.slug)

    def unsubscribe_url(self, obj=None):
        """Return the url to unsubscribe to the given object"""
        return self.alert_url('unsubscribe', pk=(obj and obj.pk), slug=self.slug)

    def get_absolute_url(self):
        """Return the url to see alert type details"""
        return self.alert_url('category', slug=self.slug)

    @staticmethod
    def alert_url(view, **kwargs):
        """Returns a standard url for alerts"""
        kwargs = dict((a, b) for (a, b) in kwargs.items() if b is not None)
        return reverse('alert.' + view, kwargs=kwargs)

    def __str__(self):
        try:
            return str(self.name)
        except AttributeError:
            return "Orphan (%s)" % self.slug


class SettingsQuerySet(QuerySet):
    """Provide easy ways of accessing lists of user's alert settings"""
    def get(self, *args, **kwargs):
        """Get the specific setting, creating one if it doesn't exist"""
        hint = self._hints.get('instance', None)
        user = kwargs.get('user', hint)
        alert = kwargs.get('alert', hint)

        try:
            return super().get(*args, **kwargs)
        except self.model.DoesNotExist:
            if not isinstance(user, get_user_model()) \
              or not isinstance(alert, AlertType):
                raise

        # Create a blank, not-saved model containing the default settings.
        return self.model(
            user_id=user.pk,
            alert_id=alert.pk,
            owner=alert.subscribe_own,
            email=alert.default_email,
            irc=alert.default_irc,
            batch=alert.default_batch,
        )

    def for_user(self, user):
        """Return the settings for a specific user"""
        alert = self._hints.get('instance', None)
        return self.get(user=user, alert=alert)



class UserAlertSetting(Model):
    """Allow users to configure how they access alerts on the website"""
    user = ForeignKey(settings.AUTH_USER_MODEL, related_name='alert_settings')
    alert = ForeignKey(AlertType, related_name='settings')
    owner = BooleanField(_("Subscribe to Self"), default=True, \
        help_text=_("Send the alert if it relates directly to me or my group."))

    email = BooleanField(_("Send Email Alert"), default=False, \
        help_text=_("Send the alert to the account email address."))
    irc = BooleanField(_("Send IRC Alert"), default=False, \
        help_text=_("If online, this alert will be sent to my irc nickname."))
    batch = CharField(_("Batch Alerts"), max_length=1, \
        choices=BATCH_MODES, blank=True, null=True, \
        help_text=_("Save all alerts and send as one email, only affects email alerts."))
    filter_value = CharField(max_length=255, blank=True, null=True, \
        help_text=_("An extra filter variable which can be different for each alert."))

    objects = SettingsQuerySet.as_manager()

    slug = property(lambda self: self.alert.slug)

    def __str__(self):
        return str(self.alert)

    @property
    def subscriptions(self):
        """Returns related subscriptions based on the user and alert"""
        return self.alert.subscriptions.filter(user=self.user)

    def is_default(self):
        """Return true if the settings are just the default settings"""
        return self.owner != self.alert.subscribe_own \
            or self.email != self.alert.default_email \
            or self.batch != self.alert.default_batch \
            or self.irc != self.alert.default_irc \
            or self.filter_value not in [None, '']

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        """Do not save default settings if never saved before"""
        if self.pk and not self.is_default():
            super().save(force_insert=False, force_update=False, using=None, update_fields=None)


class UserAlertQuerySet(QuerySet):
    """Provide ways to listing a user's alerts"""
    def serialise(self):
        """Turn the list of alerts into a list of dictionaries"""
        # It's not possible to use qs.values(...) because we need
        # to return the subject and body lines too which are template
        # rendered and not just values in the database.
        return [{
            'id': item.pk,
            'subject': item.subject,
            'body': item.body,
            'created': item.created,
            'viewed': item.viewed,
            'deleted': item.deleted,
            'alert': item.alert.pk,
        } for item in self]

    @property
    def new(self):
        """Return all new (unread) alerts"""
        return self.filter(viewed__isnull=True, deleted__isnull=True)

    @property
    def visible(self):
        """Return a list of visible alerts"""
        return self.filter(deleted__isnull=True)

    def view_all(self):
        """Mark all new alerts as visible"""
        return self.new.update(viewed=now())

    def delete_all(self):
        """Delete all visible alerts"""
        return self.visible.update(deleted=now())

    def send_batch_email(self, batch_mode, user_id, alert_ids):
        """Sends all the selected messages out as a batched email"""
        qset = self.filter(user_id=user_id, alert_id__in=alert_ids)
        if qset.count() == 0:
            return False
        if qset.count() == 1:
            return self[0].send_email()

        user = qset[0].user
        context_data = {
            'mode': batch_mode,
            'types': len(alert_ids),
            'count': qset.count(),
            'alerts': qset,
            'user': user
        }

        with translation.override(user.language):
            subject = {
                'D': _("Inkscape Daily Notifications (%d)"),
                'W': _("Inkscape Weekly Notifications (%d)"),
                'M': _("Inkscape Monthly Notifications (%d)"),
            }[batch_mode] % qset.count()

            template = "alerts/alert/batch_email.txt"

            kwargs = {
                'subject': subject,
                'body': render_template(template, context_data),
                'to': [user.email],
            }
            if EmailMultiAlternatives(**kwargs).send(True):
                qset.view_all()
        return True

class UserAlertManager(Manager):
    """Provide easy access to alert lists for users"""
    _queryset_class = UserAlertQuerySet

    def get_queryset(self):
        """Returns alerts for a user, butonly currently live ones"""
        queryset = super(UserAlertManager, self).get_queryset()

        from alerts.base import BaseAlert
        # Limit query to currently live/available alerts
        queryset = queryset.filter(alert__slug__in=list(BaseAlert.instances))

        if getattr(self, 'target', None) is not None:
            ctype = UserAlertObject.target.get_content_type(obj=self.target)
            queryset = queryset.filter(objs__table=ctype, objs__o_id=self.target.pk)

        if getattr(self, 'alert_type', None) is not None:
            queryset = queryset.filter(alert=self.alert_type)

        return queryset.order_by('-created')

    @property
    def parent(self):
        """Returns what object is the parent, ususally the user object"""
        if 'user__exact' in self.core_filters:
            return self.core_filters['user__exact']
        return None


class UserAlert(Model):
    """A single alert for a specific user"""
    user = ForeignKey(settings.AUTH_USER_MODEL, related_name='alerts')
    alert = ForeignKey(AlertType, related_name='sent')

    created = DateTimeField(auto_now_add=True)
    viewed = DateTimeField(blank=True, null=True)
    deleted = DateTimeField(blank=True, null=True)

    objects = UserAlertManager()

    subject = property(lambda self: self.alert.get_subject(self.data))
    body = property(lambda self: self.alert.get_body(self.data))
    email_body = property(lambda self: self.alert.get_email_body(self.data))

    def view(self):
        """Set the alert as viewed"""
        if not self.viewed:
            self.viewed = now()
            self.save()

    def delete(self):
        """Set the alert as deleted"""
        if not self.deleted:
            self.deleted = now()
            self.save()

    def is_hidden(self):
        """Return true if the alert is viewed or deleted"""
        return self.viewed or self.deleted

    @property
    def config(self):
        """Return the settings for this alert's type and this user"""
        # This should auto-create but not save.
        return UserAlertSetting.objects.get(user=self.user, alert=self.alert)

    def __str__(self):
        return "<UserAlert %s>" % str(self.created)

    @staticmethod
    def get_absolute_url():
        """Return a link to all alerts for this user"""
        return reverse('alerts')

    @property
    def data(self):
        """Return a dictionary of fields for this alert"""
        ret = defaultdict(list, alert=self, site=settings.SITE_ROOT)
        for item in list(self.objs.all()) + list(self.values.all()):
            try:
                target = item.target
            except AttributeError:
                target = None

            if item.name[0] == '@':
                ret[item.name[1:]+'_list'].append(target)
            else:
                ret[item.name] = target
        return ret

    def add_value(self, name, value):
        """Add the named value to this alert's value list"""
        if isinstance(value, (tuple, list)) and name[0] != '@':
            for x in value:
                self.add_value('@' + name, x)
        elif isinstance(value, Model):
            UserAlertObject(alert=self, name=name, target=value).save()
        else:
            UserAlertValue(alert=self, name=name, target=str(value)).save()

    def send_irc_msg(self):
        """Send this alert message over IRC if it's available"""
        if not self.config.irc:
            return False
        return self.alert.send_irc_msg(self)

    def send_email(self, **kwargs):
        """Send alert email is user's own language"""
        if not self.config.email:
            return False
        with translation.override(self.user.language or 'en'):
            data = self.data.copy()
            data.update(kwargs.pop('context_data', {}))
            if self.alert.send_email(self.user.email, data, **kwargs):
                self.view()
        return True


class UserAlertObject(Model):
    """User alert value, linked to another database object"""
    alert = ForeignKey(UserAlert, related_name='objs')
    name = CharField(max_length=128)

    table = ForeignKey(ContentType, blank=True, null=True)
    o_id = PositiveIntegerField()
    target = GenericForeignKey('table', 'o_id')

    def __str__(self):
        return "AlertObject %s=%s" % (self.name, str(self.o_id))


class UserAlertValue(Model):
    """User alert value, scalar value stored as a string"""
    alert = ForeignKey(UserAlert, related_name='values')
    name = CharField(max_length=128)
    target = CharField(max_length=255)

    def __str__(self):
        return "AlertValue %s=%s" % (self.name, self.target)


class SubscriptionQuerySet(QuerySet):
    """Access a list of subscriptions for a user"""
    def get_or_create(self, target=None, **kwargs):
        """Handle the match between a null target and non-null targets"""
        deleted = 0
        if target:
            # if subscription with no target exists, return that.
            try:
                obj = self.get(target__isnull=True, **kwargs)
            except AlertSubscription.DoesNotExist:
                return super().get_or_create(target=target, **kwargs) + (0,)
            else:
                return (obj, False, deleted)

        (obj, created) = super().get_or_create(target=target, **kwargs)
        if created:
            # replace all other existing subscriptions with this one.
            to_delete = self.filter(target__isnull=False, **kwargs)
            deleted = to_delete.count()
            to_delete.delete()
        return (obj, created, deleted)

    def is_subscribed(self, target=None, directly=False):
        """Returns true if the user is already subscribed to this"""
        if target is None:
            return bool(self.filter(target__isnull=True).count())
        if directly:
            return bool(self.filter(target=target.pk).count())
        return bool(self.filter(Q(target=target.pk) | Q(target__isnull=True)).count())


class AlertSubscriptionManager(Manager.from_queryset(SubscriptionQuerySet)):
    """Manage lists of user subscriptions"""
    def get_queryset(self):
        """Return alert subscriptions with the right targeting"""
        queryset = super(AlertSubscriptionManager, self).get_queryset()

        if getattr(self, 'alert_type', None) is not None:
            queryset = queryset.filter(alert=self.alert_type)
        if hasattr(self, 'target'):
            if self.target is not None:
                queryset = queryset.filter(target=self.target.pk)
            else:
                queryset = queryset.filter(target__isnull=True)
        return queryset


class AlertSubscription(Model):
    """A subscription to a object or list of object's alerts"""
    alert = ForeignKey(AlertType, related_name='subscriptions')
    user = ForeignKey(settings.AUTH_USER_MODEL, related_name='alert_subscriptions')
    target = PositiveIntegerField(_("Object ID"), blank=True, null=True)

    objects = AlertSubscriptionManager()

    def object(self):
        """Return the associated object (alert target)"""
        return self.alert.get_object(pk=self.target)

    def __str__(self):
        return "%s Subscription to %s" % (str(self.user), str(self.alert))


# -------- Start Example App -------- #

class MessageQuerySet(QuerySet):
    """Provide links to the user interface for lists of messages"""
    breadcrumb_name = staticmethod(lambda: _("Messages"))
    get_absolute_url = staticmethod(lambda: reverse("alerts"))

class Message(Model):
    """
    User messages are a simple alert example system allowing
    users to send messages between each other.
    """
    sender = ForeignKey(settings.AUTH_USER_MODEL, related_name="sent_messages")
    recipient = ForeignKey(settings.AUTH_USER_MODEL, related_name="messages")
    reply_to = ForeignKey('self', related_name="replies", null=True, blank=True)
    subject = CharField(max_length=128)
    body = TextField(_("Message Body"),\
        validators=[MaxLengthValidator(8192)], null=True, blank=True)
    created = DateTimeField(default=now)

    objects = MessageQuerySet.as_manager()

    def get_root(self, children=None):
        """Returns the root message for the thread"""
        children = children or tuple()
        if self.reply_to:
            # Break infinate root-to-branch loop in tree
            if id(self) in children:
                return self
            return Message.get_root(self.reply_to, children+(id(self),))
        return self

    def __str__(self):
        return "Message from %s" % str(self.sender)
