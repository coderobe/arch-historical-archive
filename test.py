#!/usr/bin/env python

import upload_pkg_internetarchive
import DB

import mock
from unittest.mock import MagicMock, call
import unittest

class TestUploader(unittest.TestCase):

    def test_upload_pkg(self):
        mock_uploader = MagicMock()
        app = upload_pkg_internetarchive.ArchiveUploader(mock_uploader,
                DB.DB(':memory:'))
        app.chunksize = 2

        response_ok = MagicMock(status_code=200)

        mock_uploader.upload.side_effect = [
                [response_ok, response_ok],
                [response_ok, response_ok]
                ]

        self.assertFalse(app.db.exists('fb-client-2.0.4-1-any.pkg.tar.xz'))
        self.assertFalse(app.db.exists('fb-client-2.0.3-2-any.pkg.tar.xz'))
        self.assertFalse(app.db.exists('fb-client-2.0.99-1-any.pkg.tar.xz'))

        ret = app.main(['./test-data/archive/packages/f/fb-client'])
        self.assertEqual(ret, 0)

        self.assertTrue(app.db.exists('fb-client-2.0.4-1-any.pkg.tar.xz'))
        self.assertTrue(app.db.exists('fb-client-2.0.3-2-any.pkg.tar.xz'))
        self.assertFalse(app.db.exists('fb-client-2.0.99-1-any.pkg.tar.xz'))

        ret = app.main(['./test-data/archive/packages/f/fb-client'])
        self.assertEqual(ret, 0)

        mock_uploader.upload.assert_has_calls([
            call('archlinux_pkg_fb-client',
                files=['./test-data/archive/packages/f/fb-client/fb-client-2.0.3-2-any.pkg.tar.xz',
                    './test-data/archive/packages/f/fb-client/fb-client-2.0.3-2-any.pkg.tar.xz.sig',],
                metadata=mock.ANY),
            call('archlinux_pkg_fb-client',
                files=['./test-data/archive/packages/f/fb-client/fb-client-2.0.4-1-any.pkg.tar.xz',
                    './test-data/archive/packages/f/fb-client/fb-client-2.0.4-1-any.pkg.tar.xz.sig',],
                metadata=mock.ANY),
            ])

    def test_upload_pkg_error(self):
        mock_uploader = MagicMock()
        app = upload_pkg_internetarchive.ArchiveUploader(mock_uploader,
                DB.DB(':memory:'))
        app.chunksize = 2

        response_ok = MagicMock(status_code=200)
        response_error = MagicMock(status_code=500)

        mock_uploader.upload.side_effect = [
                [response_ok, response_ok],
                [response_error, response_ok]
                ]

        self.assertFalse(app.db.exists('fb-client-2.0.4-1-any.pkg.tar.xz'))
        self.assertFalse(app.db.exists('fb-client-2.0.3-2-any.pkg.tar.xz'))

        ret = app.main(['./test-data/archive/packages/f/fb-client'])
        self.assertEqual(ret, 1)

        mock_uploader.upload.assert_has_calls([
            call('archlinux_pkg_fb-client',
                files=['./test-data/archive/packages/f/fb-client/fb-client-2.0.3-2-any.pkg.tar.xz',
                    './test-data/archive/packages/f/fb-client/fb-client-2.0.3-2-any.pkg.tar.xz.sig',],
                metadata=mock.ANY),
            call('archlinux_pkg_fb-client',
                files=['./test-data/archive/packages/f/fb-client/fb-client-2.0.4-1-any.pkg.tar.xz',
                    './test-data/archive/packages/f/fb-client/fb-client-2.0.4-1-any.pkg.tar.xz.sig',],
                metadata=mock.ANY),
            ])

        self.assertFalse(app.db.exists('fb-client-2.0.4-1-any.pkg.tar.xz'))
        self.assertTrue(app.db.exists('fb-client-2.0.3-2-any.pkg.tar.xz'))

        mock_uploader.reset_mock()
        mock_uploader.upload.side_effect = [[response_ok]]

        ret = app.main(['./test-data/archive/packages/f/fb-client'])
        self.assertEqual(ret, 0)

        mock_uploader.upload.assert_called_once_with('archlinux_pkg_fb-client',
                files=['./test-data/archive/packages/f/fb-client/fb-client-2.0.4-1-any.pkg.tar.xz'],
                metadata=mock.ANY)
        self.assertTrue(app.db.exists('fb-client-2.0.4-1-any.pkg.tar.xz'))
        self.assertTrue(app.db.exists('fb-client-2.0.3-2-any.pkg.tar.xz'))

    def test_upload_pkg_multiple_case(self):
        mock_uploader = MagicMock()
        app = upload_pkg_internetarchive.ArchiveUploader(mock_uploader,
                DB.DB(':memory:'))
        app.chunksize = 2

        response_ok = MagicMock(status_code=200)

        mock_uploader.upload.side_effect = [
                [response_ok, response_ok],
                [response_ok, response_ok]
                ]

        self.assertFalse(app.db.exists('libreoffice-fresh-sr-Latn-5.3.0-1-any.pkg.tar.xz'))
        self.assertFalse(app.db.exists('libreoffice-fresh-sr-latn-6.2.3-1-any.pkg.tar.xz'))

        ret = app.main(['./test-data/archive/packages/l/libreoffice-fresh-sr-Latn'])
        self.assertEqual(ret, 0)

        self.assertTrue(app.db.exists('libreoffice-fresh-sr-Latn-5.3.0-1-any.pkg.tar.xz'))
        self.assertFalse(app.db.exists('libreoffice-fresh-sr-latn-6.2.3-1-any.pkg.tar.xz'))

        ret = app.main(['./test-data/archive/packages/l/libreoffice-fresh-sr-latn'])
        self.assertEqual(ret, 0)

        self.assertTrue(app.db.exists('libreoffice-fresh-sr-Latn-5.3.0-1-any.pkg.tar.xz'))
        self.assertTrue(app.db.exists('libreoffice-fresh-sr-latn-6.2.3-1-any.pkg.tar.xz'))

        mock_uploader.upload.assert_has_calls([
            call('archlinux_pkg_libreoffice-fresh-sr-Latn',
                files=['./test-data/archive/packages/l/libreoffice-fresh-sr-Latn/libreoffice-fresh-sr-Latn-5.3.0-1-any.pkg.tar.xz',
                    './test-data/archive/packages/l/libreoffice-fresh-sr-Latn/libreoffice-fresh-sr-Latn-5.3.0-1-any.pkg.tar.xz.sig',],
                metadata=mock.ANY),
            # should be uploaded with the previous identifier (i.e. Latn instead of latn)
            call('archlinux_pkg_libreoffice-fresh-sr-Latn',
                files=['./test-data/archive/packages/l/libreoffice-fresh-sr-latn/libreoffice-fresh-sr-latn-6.2.3-1-any.pkg.tar.xz',
                    './test-data/archive/packages/l/libreoffice-fresh-sr-latn/libreoffice-fresh-sr-latn-6.2.3-1-any.pkg.tar.xz.sig',],
                metadata=mock.ANY),
            ])

if __name__ == '__main__':
    unittest.main()
