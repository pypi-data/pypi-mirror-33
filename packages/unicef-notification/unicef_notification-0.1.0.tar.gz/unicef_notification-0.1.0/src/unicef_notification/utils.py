import json

from django.conf import settings
from django.core import serializers
from django.db import models
from django.template import Context
from django.template.loader import get_template


def model_to_dictionary(obj):
    """
    Given a model instance `obj`, return a dictionary that represents it.
    E.g. something like
    {
        'pk': 15,
        'model':
        'audit.auditorstaffmember',
        'auditor_firm': 15,
        'user': 934
    }
    For _simple_ use from templates, this'll work as well as the model
    instance itself.
    And it's trivially serializable by the default json encoder.
    That's all we really need here.
    """
    # We cannot just use model_to_dict, because it excludes non-editable fields
    # unconditionally, and we want them all.

    # Note that Django's serializers only work on iterables of model instances

    json_string = serializers.serialize('json', [obj])
    # The string will deserialize to a list with one simple dictionary, like
    # {
    #     'pk': 15,
    #     'model':
    #     'audit.auditorstaffmember',
    #     'fields': {
    #         'auditor_firm': 15,
    #         'user': 934
    #     }
    # }
    d = json.loads(json_string)[0]
    # Promote the fields into the main dictionary
    d.update(**d.pop('fields'))
    return d


def serialize_dict(data):
    """
    Return a new dictionary, which is a copy of data, but
    if data is a dictionary with some model instances as values,
    the model instances are replaced with dictionaries so that
    the whole thing should be serializable.
    """
    return {
        k: model_to_dictionary(v) if isinstance(v, models.Model) else v
        for k, v in data.items()
    }


def strip_text(text):
    return '\r\n'.join([line.lstrip() for line in text.splitlines()])


def get_template_content(content, filename, context={}):
    # If content given, use that; if filename given, fetch the template
    # from that file and return its content; else, return an empty string.
    if content:
        return content
    if filename:
        ctx = Context(context)
        template = get_template(filename)
        return template.template.render(ctx)
    return ''


def send_notification(
        recipients,
        sender=None,
        from_address='',
        cc=None,
        context=None,
        subject=None,
        subject_filename=None,
        content=None,
        content_filename=None,
        html_content=None,
        html_content_filename=None,
):
    """
    Send a notification, building the content from templates and
    a rendering context.

    Always uses 'Email' type (no other notification type implemented yet).

    * recipients: list of email strings to address the notification to

    * cc: list of email strings to copy the notification to, or None

    * sender: any object. if present, stored as the ``.sender`` in the notification.
      If it's a User object, its ``.email`` is used as the notification
      "From" address.

    * from_address: If `sender` doesn't provide a From address, this can
      provide an email string to use for it. If this is None and the
      sender doesn't provide an address, then settings.DEFAULT_FROM_EMAIL
      is used.

    * context: dictionary used to render the templates, or None.

    Then, for each of subject, plain text message content, and html text message
    content, you can provide either the raw content, or the name of a template file.
    (If you provide both, the content will be used, not the template file).
    """
    from unicef_notification.models import Notification

    if not (sender or from_address):
        from_address = settings.DEFAULT_FROM_EMAIL

    # Let the model handle parameter validation by creating the instance
    # and 'cleaning' it before saving.
    subject = get_template_content(subject, subject_filename, context)
    text_message = get_template_content(content, content_filename, context)
    html_message = get_template_content(
        html_content,
        html_content_filename,
        context
    )

    notification = Notification(
        method_type=Notification.TYPE_EMAIL,
        sender=sender,
        from_address=from_address,
        recipients=recipients,
        cc=cc or [],
        template_data=context,
        subject=subject,
        text_message=text_message,
        html_message=html_message,
    )
    notification.full_clean()
    notification.save()
    notification.send_notification()


def send_notification_with_template(
    recipients,
    template_name,
    context,
    sender=None,
    from_address='',
    cc=None,
):
    """
    Send an email notification using an EmailTemplate object as the source of
    the templates.

    Always uses 'Email' type (no other notification type implemented yet).

    * recipients: list of email strings to address the notification to

    * cc: list of email strings to copy the notification to, or None

    * sender: any object. if present, stored as the ``.sender`` in the notification.
      If it's a User object, its ``.email`` is used as the notification
      "From" address.

    * from_address: If `sender` doesn't provide a From address, this can
      provide an email string to use for it. If this is None and the
      sender doesn't provide an address, then settings.DEFAULT_FROM_EMAIL
      is used.

    * context: dictionary used to render the templates, or None.

    * template_name: name of email template to use (there must be a EmailTemplate
      record with that name)
    """
    from unicef_notification.models import Notification

    if not (sender or from_address):
        from_address = settings.DEFAULT_FROM_EMAIL

    assert template_name

    # Let the model handle parameter validation by creating the instance
    # and 'cleaning' it before saving.
    notification = Notification(
        method_type=Notification.TYPE_EMAIL,
        sender=sender,
        from_address=from_address,
        recipients=recipients,
        cc=cc or [],
        template_name=template_name,
        template_data=context,
    )
    notification.full_clean()
    notification.save()
    notification.send_notification()
