#!/usr/bin/env python

import token_api

rc = token_api.connect()
if rc == 0:
    token_api.clear_token()
    token_api.disconnect()
