#!/usr/bin/env python

'''
This script retrieves the Shibboleth authentication cookie for HDTools for use
with `password_reset.py` and `last_password_change.py`.
It depends on `pywebview>=5.1` for opening HDTools; `pywebview` uses the system
web browser engine (Linux: QTWebEngine/WebKitGTK, Windows: WebView2, MacOS:
WKWebView).

For Linux, install `pywebview[gtk]` or `pywebview[qt]` specifically if you
receive errors about `gi` or `qtpy` not being installed. See the `pywebview`
documentation (https://pywebview.flowrl.com/guide/installation.html#linux) for
more information about the necessary dependencies.

For the GTK version, you may also need to install `libcairo2-dev` and
`libgirepository-2.0-dev` (on Debian-based systems) in addition to the other
dependencies listed on the site.


Usage:

```
export HDTOOLS_COOKIE="$(./get_hdtools_cookie.py)"
./password_reset.py --users userA
./last_password_change.py --users userA output.json
```
'''

import webview


def get_cookie(window: webview.Window):
    for cookie in window.get_cookies():
        for morsel in cookie.values():
            if morsel.key.startswith('_shibsession_'):
                print(f'{morsel.key}={morsel.value}')
                window.destroy()
                return


if __name__ == '__main__':
    w = webview.create_window('HDTools', 'https://hdtools.app.clemson.edu')
    w.events.loaded += get_cookie
    webview.start()