import sys

from PySide6 import QtWidgets , QtGui
from package.python.main_window import MainWindow

from package.python.api.asscrapper import AnimeSamaAScrapper
from package.python.api.constant import MEDIA_PATH


ico_path = MEDIA_PATH / 'ico.png'

app = QtWidgets.QApplication()

app.setWindowIcon(QtGui.QIcon(ico_path.as_posix()))
main_window = MainWindow()

main_window.setWindowIcon(QtGui.QIcon(ico_path.as_posix()))
main_window.show()
anime_list = AnimeSamaAScrapper().get_animes()
if anime_list != None:
    main_window.load_anime_list(anime_list)
    main_window.information_lbl.setText(f"Liste total : {len(anime_list)}")

sys.exit(app.exec())
