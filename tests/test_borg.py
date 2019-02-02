import os
import sys
import subprocess
from time import strftime
import shutil
from unittest.mock import MagicMock

from PyQt5.QtWidgets import QApplication

import context
from testcase import BorgQtTestCase
import borg_interface as borg


app = QApplication(sys.argv)


class BorgQtBackupTestCase(BorgQtTestCase):
    def setUp(self):
        super().setUp()
        self.repository_path = '/tmp/test-borgqt'
        os.environ['BORG_REPO'] = self.repository_path
        os.environ['BORG_PASSPHRASE'] = 'foo'
        os.environ['BORG_DISPLAY_PASSPHRASE'] = 'no'
        subprocess.run(['borg', 'init',
                        '--encryption=repokey-blake2'],
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)

    def tearDown(self):
        if os.path.exists(self.repository_path):
            shutil.rmtree(self.repository_path)

    def test_backup(self):
        borg.background_backup(['.'])
        output = subprocess.check_output(['borg', 'list'], encoding='utf8')
        self.assertNotEqual(-1, output.find(strftime('%Y-%m-%d_%H:')))

    def test_backup_with_prefix(self):
        borg.background_backup(['.'], prefix='test')
        output = subprocess.check_output(['borg', 'list'], encoding='utf8')
        self.assertNotEqual(-1, output.find(strftime('test_%Y-%m-%d_%H:')))