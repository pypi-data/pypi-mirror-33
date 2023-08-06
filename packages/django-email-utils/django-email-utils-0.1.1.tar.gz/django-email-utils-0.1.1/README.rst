##################
django-email-utils
##################

Utility functions to ease Django's email sending process.


************
Installation
************

Install from PyPI::

    pip install django-email-utils


*****
Usage
*****

Send emails using the ``send_email`` utility function::

    from email_utils import send_email


    send_email(
        context={'foo': 'bar'},
        from_email='no-reply@myproject.com',
        recipient_list=['test@example.com'],
        subject='My Templated Email',
        template_name='myapp/template',
    )


*******
License
*******

This project is licensed under the MIT License.


*******
Authors
*******

Chathan Driehuys (chathan@driehuys.com)
