.. _developerguide:

Developer guide
===============

Using latest ``reana-client`` version
-------------------------------------

If you want to use the latest bleeding-edge version of ``reana-client``, without
cloning it from GitHub, you can use:

 .. code-block:: console

    $ mkvirtualenv reana-client-latest -p /usr/bin/python2.7
    $ pip install \
        'git+https://github.com/reanahub/reana-client.git@master#egg=reana-client'
