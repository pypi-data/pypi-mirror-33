"""
UI related code for dialogs used by Mu.

Copyright (c) 2015-2017 Nicholas H.Tollervey and others (see the AUTHORS file).

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
import logging
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import (QVBoxLayout, QListWidget, QLabel, QListWidgetItem,
                             QDialog, QDialogButtonBox, QPlainTextEdit,
                             QTabWidget, QWidget, QCheckBox, QLineEdit)
from mu.resources import load_icon
from mu.interface.themes import NIGHT_STYLE, DAY_STYLE, CONTRAST_STYLE


logger = logging.getLogger(__name__)


class ModeItem(QListWidgetItem):
    """
    Represents an available mode listed for selection.
    """

    def __init__(self, name, description, icon, parent=None):
        super().__init__(parent)
        self.name = name
        self.description = description
        self.icon = icon
        text = "{}\n{}".format(name, description)
        self.setText(text)
        self.setIcon(load_icon(self.icon))


class ModeSelector(QDialog):
    """
    Defines a UI for selecting the mode for Mu.
    """

    def setup(self, modes, current_mode, theme):
        if theme == 'day':
            self.setStyleSheet(DAY_STYLE)
        elif theme == 'night':
            self.setStyleSheet(NIGHT_STYLE)
        else:
            self.setStyleSheet(CONTRAST_STYLE)
        self.setMinimumSize(600, 400)
        self.setWindowTitle(_('Select Mode'))
        widget_layout = QVBoxLayout()
        label = QLabel(_('Please select the desired mode then click "OK". '
                         'Otherwise, click "Cancel".'))
        label.setWordWrap(True)
        widget_layout.addWidget(label)
        self.setLayout(widget_layout)
        self.mode_list = QListWidget()
        self.mode_list.itemDoubleClicked.connect(self.select_and_accept)
        widget_layout.addWidget(self.mode_list)
        self.mode_list.setIconSize(QSize(48, 48))
        for name, item in modes.items():
            if not item.is_debugger:
                ModeItem(item.name, item.description, item.icon,
                         self.mode_list)
        self.mode_list.sortItems()
        instructions = QLabel(_('Change mode at any time by clicking '
                                'the "Mode" button containing Mu\'s logo.'))
        instructions.setWordWrap(True)
        widget_layout.addWidget(instructions)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok |
                                      QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        widget_layout.addWidget(button_box)

    def select_and_accept(self):
        """
        Handler for when an item is double-clicked.
        """
        self.accept()

    def get_mode(self):
        """
        Return details of the newly selected mode.
        """
        if self.result() == QDialog.Accepted:
            return self.mode_list.currentItem().icon
        else:
            raise RuntimeError('Mode change cancelled.')


class LogWidget(QWidget):
    """
    Used to display Mu's logs.
    """

    def setup(self, log):
        widget_layout = QVBoxLayout()
        self.setLayout(widget_layout)
        label = QLabel(_('When reporting a bug, copy and paste the content of '
                         'the following log file.'))
        label.setWordWrap(True)
        widget_layout.addWidget(label)
        self.log_text_area = QPlainTextEdit()
        self.log_text_area.setReadOnly(True)
        self.log_text_area.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.log_text_area.setPlainText(log)
        widget_layout.addWidget(self.log_text_area)


class EnvironmentVariablesWidget(QWidget):
    """
    Used for editing and displaying environment variables used with Python 3
    mode.
    """

    def setup(self, envars):
        widget_layout = QVBoxLayout()
        self.setLayout(widget_layout)
        label = QLabel(_('The environment variables shown below will be '
                         'set each time you run a Python 3 script.\n\n'
                         'Each separate enviroment variable should be on a '
                         'new line and of the form:\nNAME=VALUE'))
        label.setWordWrap(True)
        widget_layout.addWidget(label)
        self.text_area = QPlainTextEdit()
        self.text_area.setLineWrapMode(QPlainTextEdit.NoWrap)
        self.text_area.setPlainText(envars)
        widget_layout.addWidget(self.text_area)


class MicrobitSettingsWidget(QWidget):
    """
    Used for configuring how to interact with the micro:bit:

    * Minification flag.
    * Override runtime version to use.
    """

    def setup(self, minify, custom_runtime_path):
        widget_layout = QVBoxLayout()
        self.setLayout(widget_layout)
        self.minify = QCheckBox(_('Minify Python code before flashing?'))
        self.minify.setChecked(minify)
        widget_layout.addWidget(self.minify)
        label = QLabel(_('Override the built-in MicroPython runtime with '
                         'the following hex file (empty means use the '
                         'default):'))
        label.setWordWrap(True)
        widget_layout.addWidget(label)
        self.runtime_path = QLineEdit()
        self.runtime_path.setText(custom_runtime_path)
        widget_layout.addWidget(self.runtime_path)
        widget_layout.addStretch()


class AdminDialog(QDialog):
    """
    Displays administrative related information and settings (logs, environment
    variables etc...).
    """

    def setup(self, log, settings, theme):
        if theme == 'day':
            self.setStyleSheet(DAY_STYLE)
        elif theme == 'night':
            self.setStyleSheet(NIGHT_STYLE)
        else:
            self.setStyleSheet(CONTRAST_STYLE)
        self.setMinimumSize(600, 400)
        self.setWindowTitle(_('Mu Administration'))
        widget_layout = QVBoxLayout()
        self.setLayout(widget_layout)
        self.tabs = QTabWidget()
        widget_layout.addWidget(self.tabs)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok)
        button_box.accepted.connect(self.accept)
        widget_layout.addWidget(button_box)
        # Tabs
        self.log_widget = LogWidget()
        self.log_widget.setup(log)
        self.tabs.addTab(self.log_widget, _("Current Log"))
        self.envar_widget = EnvironmentVariablesWidget()
        self.envar_widget.setup(settings.get('envars', ''))
        self.tabs.addTab(self.envar_widget, _('Python3 Environment'))
        self.log_widget.log_text_area.setFocus()
        self.microbit_widget = MicrobitSettingsWidget()
        self.microbit_widget.setup(settings.get('minify', False),
                                   settings.get('microbit_runtime', ''))
        self.tabs.addTab(self.microbit_widget, _('BBC micro:bit Settings'))

    def settings(self):
        """
        Return a dictionary representation of the raw settings information
        generated by this dialog. Such settings will need to be processed /
        checked in the "logic" layer of Mu.
        """
        return {
            'envars': self.envar_widget.text_area.toPlainText(),
            'minify': self.microbit_widget.minify.isChecked(),
            'microbit_runtime': self.microbit_widget.runtime_path.text(),
        }
