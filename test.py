#!/usr/bin/env python

import upload_pkg_internetarchive

import mock
from unittest.mock import MagicMock
import unittest

class TestUploader(unittest.TestCase):

    def test_upload_pkg(self):
        mock_uploader = MagicMock()
        app = upload_pkg_internetarchive.ArchiveUploader(mock_uploader)
        app.main('./test-data/archive/packages/f/fb-client', ['2018'])
        mock_uploader.upload.assert_called()



if __name__ == '__main__':
    unittest.main()
