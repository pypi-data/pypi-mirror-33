
__version__ = '0.1.0'

import glob
import os
import sys
import argparse

try:
    from PySide import QtGui
    from pysideuic import compileUi
    from abi.tools.ui.ui_uifileconverter import Ui_UIFileConverterDialog
except ImportError:
    from PySide2 import QtWidgets as QtGui
    from pyside2uic import compileUi
    from abi.tools.ui.ui2_uifileconverter import Ui_UIFileConverterDialog


class UiFileConverterDialog(QtGui.QDialog):

    def __init__(self, src_root_dir):
        super(UiFileConverterDialog, self).__init__()
        self._ui = Ui_UIFileConverterDialog()
        self._ui.setupUi(self)

        self._src_root_dir = src_root_dir
        self._update_ui()
        self._make_connections()

    def _update_ui(self):
        files = glob.glob(os.path.join(self._src_root_dir, 'ui', '*.ui'))
        self._ui.uiFile_comboBox.addItems([os.path.relpath(name, self._src_root_dir) for name in files])
        self._ui.uiFile_pushButton.setEnabled(self._ui.uiFile_comboBox.count() > 0)

    def _make_connections(self):
        self._ui.uiFile_pushButton.clicked.connect(self._convert)

    def _convert(self):
        ui_file = self._ui.uiFile_comboBox.currentText()

        abs_path_to_ui_file = os.path.join(self._src_root_dir, ui_file)
        ui_file_directory = os.path.dirname(abs_path_to_ui_file)

        file_root_name = os.path.splitext(os.path.basename(ui_file))[0]
        abs_path_to_out_file = os.path.join(ui_file_directory, 'ui_' + file_root_name + '.py')

        # self._ui.screen_label.clear()
        with open(ui_file, 'r') as f:
            with open(abs_path_to_out_file, 'w') as g:
                pre_compile_text = 'Compiling ui file \n\t"%s"\n and writing out to \n\t"%s".'\
                                   % (abs_path_to_ui_file, abs_path_to_out_file)
                self._ui.screen_label.setText(pre_compile_text)
                compileUi(f, g, from_imports=True)
                self._ui.screen_label.setText(pre_compile_text + '\n\nCompiled.')


def main():

    app = QtGui.QApplication(sys.argv)

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
