# UNICEF Notification

Notification is a library that provides handles sending of notifications.


## Installation

    pip install unicef-notification


## Setup

Add ``unicef_notification`` to ``INSTALLED_APPS`` in ``settings.py``

    INSTALLED_APPS = [
        ...
        'unicef_notification',
    ]

Define the notification template directory to be used;

    UNICEF_NOTIFICATION_TEMPLATE_DIR = 'notifications'

This is the directory where notifcation templates are to be placed in your applications.

## Usage

Create notification template in defined `UNICEF_NOTIFICATION_TEMPLATE_DIR` from setup.

    name = "<unique name for notification">
    defaults = {
        "description": "Sample notification",
        "subject": "Subject of notification",
        "content": "Content of notification",
        "html_content": "Notificaton content in HTML format",
    }

Update the notifications;

    python manage.py update_notifications

Send notification with template;

    from unicef_notification.utils import send_notification_with_template

    context = {}
    send_notification_with_template(
        ["to@example.com"],
        "<name-of-template>",
        context,
    )

Send notification without a template;

    from unicef_notification.utils import send_notification

    send_notification(
        ["to@example.com"],
        subject="Subject of notification",
        content="Content of notification",
        html_content="Notification content in HTML format",
    )


## Contributing

### Environment Setup

To install the necessary libraries

    $ make install


### Coding Standards

See `PEP 8 Style Guide for Python Code <https://www.python.org/dev/peps/pep-0008/>`_ for complete details on the coding standards.

To run checks on the code to ensure code is in compliance

    $ make lint


### Testing

Testing is important and tests are located in `tests/` directory and can be run with;

    $ make test

Coverage report is viewable in `build/coverage` directory, and can be generated with;


### Project Links

 - Continuos Integration - https://circleci.com/gh/unicef/unicef-notification/tree/develop
 - Source Code - https://github.com/unicef/unicef-notification
