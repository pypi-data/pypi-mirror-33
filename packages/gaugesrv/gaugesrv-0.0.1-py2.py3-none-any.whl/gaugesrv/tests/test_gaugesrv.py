# -*- coding: utf-8 -*-
import unittest

import gaugesrv.app


class MainTestCase(unittest.TestCase):

    def test_main(self):
        request, response = gaugesrv.app.app.test_client.get('/')
        self.assertEqual(response.status, 200)

    def test_assets_built(self):
        # requires the setup.py build step to have ran
        request, response = gaugesrv.app.app.test_client.get('/gaugesrv.js')
        self.assertEqual(response.status, 200)
