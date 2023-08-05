Telethon
========
.. epigraph::

  ⭐️ Thanks **everyone** who has starred the project, it means a lot!

|logo| This is the threaded version of the **Telethon** library for Python.
You can its documentation `here <https://telethon.readthedocs.io/en/sync/>`_.

The threaded version is easier to get started with and simpler for quick
REPL sessions. However, you're encouraged to try out the `asyncio version
<https://github.com/LonamiWebs/Telethon>`_.


What is this?
-------------

Telegram is a popular messaging application. This library is meant
to make it easy for you to write Python programs that can interact
with Telegram. Think of it as a wrapper that has already done the
heavy job for you, so you can focus on developing an application.


Installing
----------

.. code:: sh

  pip3 install telethon


Creating a client
-----------------

.. code:: python

    from telethon import TelegramClient

    # These example values won't work. You must get your own api_id and
    # api_hash from https://my.telegram.org, under API Development.
    api_id = 12345
    api_hash = '0123456789abcdef0123456789abcdef'

    client = TelegramClient('session_name', api_id, api_hash)
    client.start()


Doing stuff
-----------

.. code:: python

    me = client.get_me()
    print(me.stringify())

    client.send_message('username', 'Hello! Talking to you from Telethon')
    client.send_file('username', '/home/myself/Pictures/holidays.jpg')

    client.download_profile_photo('me')
    messages = client.get_messages('username')
    messages[0].download_media()


Next steps
----------

Do you like how Telethon looks? Check out `Read The Docs
<https://telethon.readthedocs.io/en/sync/>`_ for a more in-depth explanation,
with examples, troubleshooting issues, and more useful information.


.. |logo| image:: logo.svg
    :width: 24pt
    :height: 24pt
