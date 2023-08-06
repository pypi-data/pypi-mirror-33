Confiky
=======

Description
-----------

Confiky read one or more ``.ini`` file and create a ``Confiky`` object with ``ini`` sections as sub class
and file settings as attributes.

Files can be passed to constructor in three ways (evaluated in this order):
    
1) ``env_arg``: check for environment variable with provided name

2) ``cli_arg``: pass ``--cli_arg`` (``cli_arg`` as you define) to the main script or who start Confiky

3) ``files``: list or string of file path

Installation
------------

Install package as usual running:

    pip install confiky

Usage
-----

Library must be imported as:

    from confiky import Confiky

Then you can tell where to find settings:

    config = Confiky(env_arg='MYAPPCONFIGPATH', cli_arg='settings', files='settings.ini')

or simpler:

    config = Confiky(files=['foo/settings.ini', '/etc/bar.ini'])
    
If no valid config source is found ``ValueError`` will be raised.

You can limit sections by doing:

    config = Confiky(files=['foo/settings.ini', '/etc/bar.ini'], required_sections=['server', 'email'])

To see all sections readed:

    config.sections

To access one specific setting:

    # config.section_name.attribute_name
    mail_server = config.email.host

You can validate your config file by doing:

    >>> config.validate(sections=['foo'], fields=['test1', 'test2', 'test3'])
    >>> {'fields_found': 3, 'sections_found'=1, all_found=True}

A shortcut is also present:

    >>> config.is_valid(sections=['foo'], fields=['test1', 'test2', 'test3'])
    >>> True

If you want to see all your settings:

    config.explain()


TODO
----

- Verify configurations order policy
- Add more informations to ``explain()`` such as setting origin
- Override default ``__getattr__`` to handle missing setting


