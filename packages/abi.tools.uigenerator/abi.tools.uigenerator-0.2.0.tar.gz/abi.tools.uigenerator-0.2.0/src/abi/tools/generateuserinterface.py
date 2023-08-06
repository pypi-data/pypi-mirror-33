
__version__ = '0.2.0'

import os
import sys
import argparse
import fnmatch
import platform

try:
    from PySide import QtGui
    from PySide import QtCore
    from pysideuic import compileUi
    from abi.tools.ui.ui_uifileconverter import Ui_UIFileConverterDialog
except ImportError:
    from PySide2 import QtCore
    from PySide2 import QtWidgets as QtGui
    from pyside2uic import compileUi
    from abi.tools.ui.ui2_uifileconverter import Ui_UIFileConverterDialog


ORGANISATION = 'abi'
ORGANISATION_DOMAIN = 'abi.auckland.ac.nz'


class SrcDirSettings(object):

    def __init__(self, src_dir):
        self._src_dir = src_dir
        self._side_by_side_output = True
        self._out_dir = ''
        self._current_index = 0

    def get_src_dir(self):
        return self._src_dir

    def is_side_by_side_output(self):
        return self._side_by_side_output

    def set_side_by_side_output(self, value=True):
        self._side_by_side_output = value

    def get_current_index(self):
        return self._current_index

    def set_current_index(self, value):
        self._current_index = value

    def get_out_dir(self):
        return self._out_dir

    def set_out_dir(self, value):
        self._out_dir = value

    def load(self, settings):
        settings.beginGroup(self._src_dir)
        self.set_current_index(int(settings.value('current_index', '0')))
        self.set_out_dir(settings.value('out_dir', ''))
        self.set_side_by_side_output(settings.value('side_by_side', 'true') == 'true')
        settings.endGroup()

    def save(self, settings):
        settings.beginGroup(self._src_dir)
        settings.setValue('current_index', self.get_current_index())
        settings.setValue('out_dir', self.get_out_dir())
        settings.setValue('side_by_side', self.is_side_by_side_output())
        settings.endGroup()


class UiFileConverterDialog(QtGui.QDialog):

    def __init__(self, src_root_dir):
        super(UiFileConverterDialog, self).__init__()
        self._ui = Ui_UIFileConverterDialog()
        self._ui.setupUi(self)

        self._src_dir_settings = SrcDirSettings(src_root_dir)

        if platform.system() == 'Darwin':
            organisation_string = ORGANISATION_DOMAIN
        else:
            organisation_string = ORGANISATION
        self._settings = QtCore.QSettings(QtCore.QSettings.IniFormat, QtCore.QSettings.UserScope,
                                          organisation_string, 'uigenerator')
        self._settings.setFallbacksEnabled(False)
        self._load_settings()

        self._update_ui()
        self._make_connections()

    def closeEvent(self, event):
        self._save_settings()
        event.accept()

    def _load_settings(self):
        self.resize(self._settings.value('size', QtCore.QSize(270, 225)))
        self.move(self._settings.value('pos', QtCore.QPoint(50, 50)))
        self._src_dir_settings.load(self._settings)

    def _save_settings(self):
        self._settings.setValue('size', self.size())
        self._settings.setValue('pos', self.pos())
        self._src_dir_settings.save(self._settings)

    def _update_ui(self):
        src_dir = self._src_dir_settings.get_src_dir()
        files = find_ui_files(src_dir)
        self._ui.uiFile_comboBox.addItems([os.path.relpath(name, src_dir) for name in files])
        self._ui.uiFile_comboBox.setCurrentIndex(self._src_dir_settings.get_current_index())
        self._ui.uiFile_pushButton.setEnabled(self._ui.uiFile_comboBox.count() > 0)
        side_by_side = self._src_dir_settings.is_side_by_side_output()
        self._ui.sideBySide_groupBox.setChecked(side_by_side)
        self._side_by_side_changed(side_by_side)
        self._ui.outDir_lineEdit.setText(self._src_dir_settings.get_out_dir())

    def _make_connections(self):
        self._ui.uiFile_pushButton.clicked.connect(self._convert)
        self._ui.uiFile_comboBox.currentIndexChanged.connect(self._src_dir_settings.set_current_index)
        self._ui.sideBySide_groupBox.toggled.connect(self._side_by_side_changed)
        self._ui.outDir_pushButton.clicked.connect(self._choose_output_directory)

    def _side_by_side_changed(self, state):
        self._ui.outDir_lineEdit.setEnabled(not state)
        self._ui.outDir_pushButton.setEnabled(not state)
        self._ui.outDir_label.setEnabled(not state)
        self._src_dir_settings.set_side_by_side_output(state)

    def _choose_output_directory(self):
        selected_directory = QtGui.QFileDialog.getExistingDirectory()
        if selected_directory:
            self._ui.outDir_lineEdit.setText(selected_directory)
            self._src_dir_settings.set_out_dir(selected_directory)

    def _convert(self):
        src_dir = self._src_dir_settings.get_src_dir()
        ui_file = self._ui.uiFile_comboBox.currentText()

        abs_path_to_ui_file = os.path.join(src_dir, ui_file)
        ui_file_directory = os.path.dirname(abs_path_to_ui_file)

        file_root_name = os.path.splitext(os.path.basename(ui_file))[0]
        if self._src_dir_settings.is_side_by_side_output():
            out_directory = ui_file_directory
        else:
            out_directory = self._src_dir_settings.get_out_dir()

        abs_path_to_out_file = os.path.join(out_directory, 'ui_' + file_root_name + '.py')

        with open(ui_file, 'r') as f:
            with open(abs_path_to_out_file, 'w') as g:
                pre_compile_text = 'Compiling ui file \n\t"%s"\n and writing out to \n\t"%s".'\
                                   % (abs_path_to_ui_file, abs_path_to_out_file)
                self._ui.screen_label.setText(pre_compile_text)
                compileUi(f, g, from_imports=True)
                self._ui.screen_label.setText(pre_compile_text + '\n\nCompiled.')


def find_ui_files(search_dir):
    matches = []
    for root, dirnames, filenames in os.walk(search_dir):
        for filename in fnmatch.filter(filenames, '*.ui'):
            matches.append(os.path.join(root, filename))

    return matches


def main():

    app = QtGui.QApplication(sys.argv)

    app.setOrganizationName('ABI')
    app.setOrganizationDomain('abi.auckland.ac.nz')
    app.setApplicationName('uigenerator')

    parser = argparse.ArgumentParser()
    parser.add_argument("src_dir", nargs='?', default=os.getcwd(),
                        help="the directory to search (recursively) for ui files.")
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s {version}'.format(version=__version__))
    args = parser.parse_args()

    src_root_dir = os.path.realpath(args.src_dir)
    os.chdir(src_root_dir)

    dialog = UiFileConverterDialog(src_root_dir)
    dialog.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
