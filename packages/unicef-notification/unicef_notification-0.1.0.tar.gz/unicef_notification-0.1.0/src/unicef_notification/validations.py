from django.core.exceptions import ValidationError
from post_office.models import EmailTemplate


def validate_template_name(template_name):
    try:
        EmailTemplate.objects.get(name=template_name)
    except EmailTemplate.DoesNotExist:
        raise ValidationError("No such EmailTemplate: %s" % template_name)


def validate_method_type(method_type):
    from unicef_notification.models import Notification

    if method_type not in (Notification.TYPE_CHOICES):
        raise ValidationError("Notification type must be 'Email'")
