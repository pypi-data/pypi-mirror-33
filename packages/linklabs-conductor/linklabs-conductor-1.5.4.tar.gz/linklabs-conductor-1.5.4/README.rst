Conductor.py
============

This is a python wrapper of Link Labs's Conductor service.

To get started, simply instantiate a ``ConductorAccount`` with your credentials::

    import conductor
    account = conductor.ConductorAccount('my_email_address')

Then, you can process messages as they are received::

    app_token = account.get_application_token('12345678901234567890')
    for msg in app_token.subscribe_iter():
        print(msg)

You can also send downlink messages to a particular module::

    module = account.get_module('$301$0-0-0-04000119D')
    msg = module.send_message(b'hello')
    msg.wait_for_success()
