import os
import configparser
import json

from PyQt5.QtWidgets import QDialog, QFileDialog
from PyQt5 import uic

from helper import BorgException


class Config(QDialog):
    def __init__(self):
        # Setting all the PyQt relevant parts
        super(QDialog, self).__init__()
        dir_path = os.path.dirname(os.path.realpath(__file__))
        ui_path = os.path.join(dir_path + '/static/UI/Settings.ui')
        uic.loadUi(ui_path, self)

        self.button_box.accepted.connect(self.accept)
        self.button_include_file.clicked.connect(self.include_file)
        self.button_include_directory.clicked.connect(self.include_directory)
        self.button_exclude_file.clicked.connect(self.exclude_file)
        self.button_exclude_directory.clicked.connect(self.exclude_directory)
        self.button_remove_include.clicked.connect(self.remove_include)
        self.button_remove_exclude.clicked.connect(self.remove_exclude)
        self.button_restore_exclude_defaults.clicked.connect(
            self.restore_exclude_defaults)

    @property
    def full_path(self):
        if 'repository_path' in self.config['borgqt']:
            if self.config['borgqt']['server']:
                return self._create_server_path()
            else:
                return self.config['borgqt']['repository_path']
        else:
            return ""

    @property
    def repository_path(self):
        return self._return_single_option('repository_path')

    @property
    def password(self):
        return self._return_single_option('password')

    @property
    def includes(self):
        return self._return_list_option('includes')

    @property
    def excludes(self):
        return self._return_list_option('excludes')

    @property
    def server(self):
        return self._return_single_option('server')

    @property
    def port(self):
        return self._return_single_option('port')

    @property
    def user(self):
        return self._return_single_option('user')

    @property
    def prefix(self):
        return self._return_single_option('prefix')

    def _return_single_option(self, option):
        if option in self.config['borgqt']:
            return self.config['borgqt'][option]
        else:
            return ""

    def _return_list_option(self, option):
        if option in self.config['borgqt']:
            return json.loads(self.config['borgqt'][option])
        else:
            return []

    def _get_path(self):
        home = os.environ['HOME']
        dir_path = os.path.dirname(os.path.realpath(__file__))

        if os.path.exists(os.path.join(home, '.config/borg_qt/borg_qt.conf')):
            return os.path.join(home, '.config/borg_qt/borg_qt.conf')
        elif os.path.exists(os.path.join(dir_path, 'borg_qt.conf')):
            return os.path.join(dir_path, 'borg_qt.conf')
        else:
            raise BorgException("Configuration file not found!")

    def _set_environment_variables(self):
        os.environ['BORG_REPO'] = self.full_path
        os.environ['BORG_PASSPHRASE'] = self.password

    def _create_server_path(self):
        if not self.config['borgqt']['user']:
            raise BorgException("User is missing in config.")
        if not self.config['borgqt']['port']:
            raise BorgException("Port is missing in config.")
        server_path = (self.config['borgqt']['user']
                       + "@"
                       + self.config['borgqt']['server']
                       + ":"
                       + self.config['borgqt']['port']
                       + self.config['borgqt']['repository_path'])
        return server_path

    def _select_file(self):
        dialog = QFileDialog
        dialog.ExistingFile
        file_path, ignore = dialog.getOpenFileName(
            self, "Select Directory", os.getenv('HOME'), "All Files (*)")
        return file_path

    def _select_directory(self):
        dialog = QFileDialog
        dialog.DirectoryOnly
        return dialog.getExistingDirectory(
            self, "Select Directory", os.getenv('HOME'))

    def include_file(self):
        file_path = self._select_file()
        if file_path:
            self.list_include.addItem(file_path)

    def include_directory(self):
        directory_path = self._select_directory()
        if directory_path:
            self.list_include.addItem(directory_path)

    def exclude_file(self):
        file_path = self._select_file()
        if file_path:
            self.list_exclude.addItem(file_path)

    def exclude_directory(self):
        directory_path = self._select_directory()
        if directory_path:
            self.list_exclude.addItem(directory_path)

    def remove_include(self):
        self.list_include.takeItem(self.list_include.currentRow())

    def remove_exclude(self):
        self.list_exclude.takeItem(self.list_exclude.currentRow())

    def restore_exclude_defaults(self):
        self.list_exclude.clear()
        default_excludes = json.loads(self.config['DEFAULT']['excludes'])
        self.list_exclude.addItems(default_excludes)

    def read(self):
        """Reads the config file
        """
        self.path = self._get_path()
        self.config = configparser.ConfigParser()
        self.config.read(self.path)

    def set_form_values(self):
        self.line_edit_repository_path.setText(self.repository_path)
        self.line_edit_password.setText(self.password)
        self.line_edit_prefix.setText(self.prefix)
        self.line_edit_server.setText(self.server)
        self.line_edit_port.setText(self.port)
        self.line_edit_user.setText(self.user)
        self.list_include.clear()
        self.list_include.addItems(self.includes)
        self.list_exclude.clear()
        self.list_exclude.addItems(self.excludes)

    def apply_options(self):
        self.config['borgqt']['repository_path'] = self.line_edit_repository_path.text()
        self.config['borgqt']['password'] = self.line_edit_password.text()
        self.config['borgqt']['prefix'] = self.line_edit_prefix.text()
        self.config['borgqt']['server'] = self.line_edit_server.text()
        self.config['borgqt']['port'] = self.line_edit_port.text()
        self.config['borgqt']['user'] = self.line_edit_user.text()

        excludes = []
        for index in range(self.list_exclude.count()):
            excludes.append(self.list_exclude.item(index).text())

        includes = []
        for index in range(self.list_include.count()):
            includes.append(self.list_include.item(index).text())

        self.config['borgqt']['includes'] = json.dumps(includes,
                                                       indent=4,
                                                       sort_keys=True)
        self.config['borgqt']['excludes'] = json.dumps(excludes,
                                                       indent=4,
                                                       sort_keys=True)
        self._set_environment_variables()

    def write(self):
        with open(self.path, 'w+') as configfile:
            self.config.write(configfile)

    def accept(self):
        super().accept()
        self.apply_options()
        self.write()