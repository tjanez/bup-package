Notes on Fedora bup-web Package
===============================

The bup-web package provides the `bup web` command which runs a web server for
browsing through bup repositories.
For convenience, it also provides a systemd unit file for running `bup web`
as a service with the systemd user instance (i.e. `systemd --user`).


Usage
-----

### Managing systemd user service

*NOTE: All commands should be executed as an ordinary (non-root) user.*

To enable the bup-web user service, execute:

    systemctl --user enable bup-web.service

To start the bup-web user service, execute:

    systemctl --user start bup-web.service

To see the status of the bup-web user service, execute:

    systemctl --user status bup-web.service

To stop the bup-web user service, execute:

    systemctl --user stop bup-web.service

To disable the bup-web user service, execute:

    systemctl --user disable bup-web.service

### Browsing bup repositories

Open your web browser and go to:

    127.0.0.1:8080

*NOTE: By default, bup-web only accepts requests from local clients.
To expose it to whole network, add `0.0.0.0:<port-number>` to its command line.
For more details on editing bup-web's configuration, see the next section.*


Configuration
-------------

Currently, bup-web user service can only be configured by manually editing its
systemd unit file.

If you've previously enabled bup-web user service, disable it with:

    systemctl --user disable bup-web.service

Then copy the package-provided unit file to your systemd user instance
configuration directory:

    cp /usr/lib/systemd/user/bup-web.service ~/.config/systemd/user/

Edit the unit file to suit your needs.

Finally, enable the bup-web user service with:

    systemctl --user enable bup-web.service


Troubleshooting
---------------

If the bup-web user service fails to start, examine its journal records by
executing:

    journalctl --user-unit bup-web.service


Authors
-------

Tadej Janež
