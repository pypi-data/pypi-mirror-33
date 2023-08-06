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
"""
Inherit from these classes if you want to create your own alert connections.
"""
__all__ = ['BaseAlert', 'EditedAlert', 'CreatedAlert', 'AddedAlert', 'RemovedAlert']

import os
import logging
from signal import SIGUSR1
from collections import defaultdict

from django.conf import settings
from django.db.models import signals as django_signals
from django.core.mail.message import EmailMultiAlternatives
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from alerts.template_tools import has_template, render_template, render_directly

class Lookup(object): # pylint: disable=too-few-public-methods
    """This descriptor is a class and object property, this is so
       we can do things like:

       Message.subscriptions.all()
       msgobj.subscriptions.all()
    """
    def __init__(self, base, model):
        self.base = base
        self.model = model

    def __get__(self, obj, klass=None):
        """Get a normal manager, but add in an extra attributes"""
        manager = type(self.model.objects)()
        manager.target = obj
        manager.model = self.model
        manager.alert_type = self.base.alert_type
        return manager

class BaseAlert(object): # pylint: disable=too-many-public-methods
    """None model parent class for your alert signals"""
    # Control how subscriptions will work.
    subscribe_all = True
    subscribe_any = True
    subscribe_own = True # Related users and groups

    # These defaults control how messages should be displayed or
    # Send via email to the user's email address.
    default_email = True
    default_batch = None  # Instant
    default_irc = False

    signal = django_signals.post_save
    sender = None

    # What lookup should be attached to the sender model;
    # much like ForeignKey related_name it creates reverse lookups.
    related_name = 'alerts'
    related_sub = 'subscriptions'

    subject = "{{ instance }}"
    email_subject = "{% trans 'Website Alert:' %} {{ instance }}"
    email_footer = 'alerts/alert/email_footer.txt'
    object_name = "{{ instance }}"

    # User specifies which user attribute on the instance alerts are sent
    alert_user = '.'
    alert_group = '.'

    # Should we load only on test suite run.
    test_only = False

    # Should settings be disabled and the defaults for all
    show_settings = True

    # Target is the attribute on the instance which subscriptions are bound
    target_field = None

    # Optional filter data that can be populated by the settings (e.g. language).
    filter_field = None
    filter_subscriber = None

    # A record of all the instances, and their dictionaries
    _singletons = defaultdict(dict)
    instances = {}
    slug = None

    def __init__(self, slug=None, is_test=False, is_migrate=False, **kwargs):
        # Borg singleton pattern
        self.__dict__ = self._singletons[slug]
        self.instances[slug] = self

        if type(self).slug is not None:
            # Already initialised previously
            return

        type(self).slug = slug
        self.is_test = is_test
        self.is_migrate = is_migrate
        # If signal is set to none, then we don't need to connect
        self.connected = not self.signal

        # Check the setup of this alert class
        if not self.sender:
            raise AttributeError("%s required 'sender' attribute" %
                                 type(self).__name__)
        if hasattr(self.sender, self.related_name):
            raise AttributeError("%s already has '%s' reverse lookup" % (
                self.sender.__name__, self.related_name))

        super(BaseAlert, self).__init__(**kwargs)

        from alerts.models import AlertType
        if not self.is_migrate:
            # Create an AlertType object which mirrors this class
            (self._alert_type, _) = AlertType.objects.get_or_create(
                slug=self.slug,
                values={
                    'enabled': True,
                    'default_email' : self.default_email,
                    'default_irc': self.default_irc,
                    'default_batch': self.default_batch,
                }
            )
        self.connect_signals()

        from alerts.models import UserAlert, AlertSubscription
        setattr(self.sender, self.related_name, Lookup(self, UserAlert))
        setattr(self.sender, self.related_sub, Lookup(self, AlertSubscription))

    def show_settings_now(self, user):
        """Shows the settings for these alert types"""
        return user and self.show_settings

    def connect_signals(self):
        """Attempts to start the signals late"""
        if not self.connected:
            self.signal.connect(self.call, sender=self.sender, dispatch_uid=self.slug)
            self.connected = True
        return self

    def disconnect_signals(self):
        """Disconnects the alert signal, useful for tests"""
        if self.connected:
            self.signal.disconnect(self.call, sender=self.sender, dispatch_uid=self.slug)
            self.connected = False
        return self

    @property
    def alert_type(self):
        """For tests we have to load alert_type object's late."""
        if not hasattr(self, '_alert_type'):
            # This will fail is the test doesn't include a fixture with all the right
            # alert types available. It depends on the test to populate the database.
            from alerts.models import AlertType
            self._alert_type = AlertType.objects.get(slug=self.slug)
        return self._alert_type

    @classmethod
    def get_alert_type(cls):
        """Return alert_type when we only have the alert class"""
        return cls(cls.slug).alert_type

    def get_alert_users(self, instance):
        """Returns a user of a list of users to send emails to"""
        return getattr(instance, self.alert_user, None)

    def get_alert_groups(self, instance):
        """Returns a group or a list of groups to send emails to"""
        return getattr(instance, self.alert_group, None)

    @classmethod
    def bellow(cls, **kwargs):
        """
        Manually calls this notification and sends out emails even if no
        django signal was actually triggered.
        """
        return cls(cls.slug).call(**kwargs)

    def call(self, instance, **kwargs):
        """Connect this method to the post_save signal and it will
           create an alert when the sender edits any object."""
        def send_to(recipient, kind=None):
            """Look through recipient and send to each"""
            if kind is None or isinstance(recipient, kind):
                ret = self.alert_type.send_to(recipient, **kwargs)
                if ret and isinstance(ret, list):
                    return ret
            elif isinstance(recipient, list):
                ret = []
                for item in recipient:
                    ret += send_to(item, kind=kind)
            return []

        users = []

        if self.subscribe_own:
            users += send_to(self.get_alert_users(instance), get_user_model())
            users += send_to(self.get_alert_groups(instance), Group)

        if self.subscribe_all:
            for sub in self.alert_type.subscriptions.filter(target__isnull=True):
                if self._filter_subscriber(sub.user, kwargs):
                    users += send_to(sub.user)

        if self.subscribe_any:
            target = instance
            if self.target_field:
                target = getattr(instance, self.target_field)

            for sub in self.alert_type.subscriptions.filter(target=target.pk):
                if self._filter_subscriber(sub.user, kwargs):
                    users += send_to(sub.user)

        return self.post_send(*users, **kwargs)

    def get_filter_field(self, user, kwargs): # pylint: disable=unused-argument
        """Returns the field that filters these objects for this user."""
        return self.filter_field

    def _filter_subscriber(self, user, kwargs):
        field = self.get_filter_field(user, kwargs)
        if field:
            from alerts.models import UserAlertSetting
            try:
                setting = user.alert_settings.get(alert__slug=self.slug)
            except UserAlertSetting.DoesNotExist:
                setting = None
            return self.get_filter_subscriber(user, setting, kwargs)
        return True

    def get_filter_subscriber(self, user, setting, kwargs): # pylint: disable=unused-argument
        """Do actual filtering of the user for this object"""
        return self.filter_subscriber

    @staticmethod
    def post_send(*users, **_):
        """Complete the call and tidy up if needed"""
        return bool(users)

    @property
    def instance_type(self):
        """Returns the type of the instance, either by sender or the target"""
        if self.target_field:
            return self.sender._meta.get_field(self.target_field).rel.to # pylint: disable=protected-access
        return self.sender

    @property
    def template(self):
        """Returns the html template for website visible alerts"""
        template = "%s/alert/%s.html" % tuple(self.slug.split('.', 1))
        if has_template(template):
            return template
        return "alerts/type_default.html"

    @property
    def email_template(self):
        """Returns the template for the email"""
        template = "%s/alert/email_%s.txt" % tuple(self.slug.split('.', 1))
        if has_template(template):
            return template
        else:
            logging.warning("Template: '%s' doesn't exist.", template)
        return "alerts/email_default.txt"

    @property
    def name(self):
        """The name is a human visible name used to show users"""
        raise NotImplementedError("Name is a required property for alerts.")

    @property
    def desc(self):
        """Describe the alert, what it does, and how it's triggered to users"""
        raise NotImplementedError("Desc is a required property for alerts.")

    @property
    def info(self):
        """Info is like description but provides detailed information"""
        raise NotImplementedError("Info is a required property for alerts.")

    def get_object(self, **fields):
        """Returns object matching field using Alert's target object type"""
        model = self.sender
        if self.target_field:
            # Get FoeignKey's mdel linking this alert instead
            model = getattr(model, self.target_field).field.rel.to
        return model.objects.get(**fields)

    def get_object_name(self, obj):
        """Return's a label for this kind of subscription for an object"""
        if obj:
            return render_directly(self.object_name, {'object': obj})
        return None

    @staticmethod
    def format_data(data):
        """Overridable function to format data for the template"""
        return data

    def get_subject(self, context_data):
        """Return's the subject text given the object"""
        return render_directly(self.subject, self.format_data(context_data))

    def get_body(self, context_data):
        """Returns the rendered body using the context_data dictionary"""
        return render_template(self.template, context_data)

    def get_email_body(self, context_data):
        """Returns the email body text rendered from the context_data"""
        return render_template(self.email_template, context_data)

    @staticmethod
    def send_irc_msg(user):
        """
        Send the running IRC bot a kick up the bum about a new alert.
        """
        try:
            with open(settings.IRCBOT_PID, 'r') as pid:
                pid = int(pid.read().strip())
            with open('/proc/%d/cmdline' % pid, 'r') as proc:
                assert('ircbot' in proc.read())
            os.kill(pid, SIGUSR1)
            return bool(user)
        except: # pylint: disable=bare-except
            # Any errors may mean:
            # * IRCBOT not configured, not running
            # * IRCBOT pid file exists but process isn't ircbot
            # * We don't have permission to signal process
            return False

    def send_email(self, recipient, context_data, **kwargs):
        """Sends the email to the recipient using the context_data"""
        if not recipient:
            return False

        context_data = self.format_data(context_data)
        subject = render_directly(self.email_subject, context_data)

        kwargs.update({
            'subject': subject.strip().replace('\n', ' ').replace('\r', ' '),
            'body': self.get_email_body(context_data),
            'to': [recipient],
        })

        if self.email_footer is not None:
            kwargs['body'] += render_template(self.email_footer, context_data)

        #if self.alert_type.CATEGORY_USER_TO_USER:
        #    this doesn't work yet because we don't know how to get the sender
        #    kwargs['reply_to'] = self.get_sender(context_data)

        # This will fail silently if not configured right
        return EmailMultiAlternatives(**kwargs).send(True)


class EditedAlert(BaseAlert): # pylint: disable=abstract-method
    """Special alert type, when any item is edited"""
    def call(self, instance=None, **kwargs):
        if not kwargs.get('created', False):
            return super(EditedAlert, self).call(instance=instance, **kwargs)
        return False


class CreatedAlert(BaseAlert): # pylint: disable=abstract-method
    """Special alert type, when any item is created"""
    def call(self, instance=None, **kwargs):
        if kwargs.get('created', False):
            return super(CreatedAlert, self).call(instance=instance, **kwargs)
        return False

class AddedAlert(BaseAlert):
    """Special alert type, when an item is added to a many to many relationship"""
    signal = django_signals.m2m_changed
    m2m_action = 'post_add'
    m2m_reverse = False
    sender = property(lambda self: self.m2m_sender.through)

    @property
    def m2m_sender(self):
        """Returns the sender field that the many to many is attached to"""
        raise NotImplementedError("Many to Many sender must be specified")

    def call(self, pk_set=None, instance=None, action=None, reverse=False, **kwargs): # pylint: disable=arguments-differ
        if action == self.m2m_action and reverse == self.m2m_reverse:
            att = self.m2m_sender.field.attname
            kwargs['items'] = getattr(instance, att).filter(pk__in=pk_set)
            return super(AddedAlert, self).call(instance=instance, **kwargs)
        return False


class RemovedAlert(AddedAlert): # pylint: disable=abstract-method
    """Special alert type, when an item is removed from a many to many relationship"""
    m2m_action = 'pre_remove'


class CustomAlert(BaseAlert): # pylint: disable=abstract-method
    """Will not bind a singal and instead cls.call(obj) should be called manually"""
    signal = None

    @classmethod
    def call(cls, instance, **kw):
        alert = cls(cls.slug)
        return super(CustomAlert, alert).call(instance=instance, **kw)
