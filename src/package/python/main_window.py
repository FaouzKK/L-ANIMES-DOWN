from functools import partial

from PySide6 import QtCore, QtWidgets

from package.python.api.asscrapper import AnimeSamaAScrapper
from package.python.api.constant import STYLE_PATH
from package.python.widgets import MWidget
from package.python.widgets.TManager import (
    TAnimeContentScrapper,
    TChapitersScrapper,
    TSamaFethingsAll,
)


class MainWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("L-ANIMES-DOWN")
        self.setMinimumSize(1000, 600)
        self.setObjectName("main_window")
        self.setup_ui()
        with open(STYLE_PATH / "stylesheet.css") as f:
            self.setStyleSheet(f.read())
        self.anime_sama_fething = TSamaFethingsAll()
        self.anime_content_fething = TAnimeContentScrapper()
        self.chapitre_scrapper = TChapitersScrapper()

    def setup_ui(self):
        self.create_layout_and_widgets()
        self.modify_widgets()
        self.add_widgets_to_layout()
        self.connect_signals_to_slots()

    def create_layout_and_widgets(self):
        # Layouts principaux
        self.main_layout = QtWidgets.QHBoxLayout()
        self.left_layout = QtWidgets.QVBoxLayout()
        self.right_layout = QtWidgets.QVBoxLayout()

        # Widgets de gauche
        self.title_label = QtWidgets.QLabel("L-ANIME-DOWNLOADER")
        self.filter_layout = QtWidgets.QHBoxLayout()
        self.search_bar = QtWidgets.QLineEdit()
        self.lang_ccb = QtWidgets.QComboBox()

        self.anim_section_layout = QtWidgets.QHBoxLayout()

        self.anime_list = QtWidgets.QListWidget()
        self.content_list = QtWidgets.QListWidget()

        self.anime_laoding_button = MWidget.MLoadingButton()
        self.content_loading_button = MWidget.MLoadingButton()

        self.information_lbl = MWidget.infoLabel("Enjoy!!!")

        # Widgets de droite
        self.welcome_message = QtWidgets.QLabel("Bienvenue sur L-ANIMES-DOWNLOADER !")
        self.short_desc = MWidget.MInfoLabel()
        self.short_info = MWidget.MInfoLabel()

    def modify_widgets(self):
        # Modification des widgets de gauche
        self.title_label.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignLeft
        )
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold")
        self.lang_ccb.addItems(["vostfr", "vf"])
        self.lang_ccb.setMinimumWidth(100)
        self.lang_ccb.setCurrentIndex(0)
        self.filter_layout.setSpacing(50)
        self.filter_layout.setContentsMargins(10, 0, 0, 10)

        # Modification des widget de droite

        self.welcome_message.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignTop | QtCore.Qt.AlignmentFlag.AlignLeft
        )
        self.welcome_message.setStyleSheet(
            "font-size: 18px; font-weight: bold ; background-color: rgba(240,240,240,0.5);"
        )
        self.welcome_message.setSizePolicy(
            QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed
        )

        self.short_desc.setText("""
Bienvenue sur L-ANIMES-DOWN, votre application de téléchargement d'animes ! 🌟 Découvrez toutes les fonctionnalités en explorant notre interface conviviale. <a href="https://github.com/FaouzKK/L-ANIMES-DOWN">Cliquez ici</a> pour visiter le GitHub du projet et contribuer à son développement !""")

        self.short_info.setText("""
<p>
<b>Fonctionnalités principales :</b>
<ul>
    <li>Télécharger des animes en qualité HD.</li>
    <li>Rechercher des animes par leur titre.</li>
    <li>Accéder aux chapitres et épisodes, et les télécharger.</li>
</ul>
</p>
<p>
<b>À savoir :</b>  
Utilisez l'icône de recharge (ou loader 🔄) pour actualiser la liste des animes, le contenu ou les chapitres.  
Les données sont sauvegardées dans votre stockage interne pour une meilleure fluidité.  
Merci de signaler tout bug rencontré sur l'application.
</p>
""")

        # modification des Layout

        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.right_layout.setSpacing(0)
        self.main_layout.setSpacing(20)
        self.left_layout.setSpacing(30)

    def add_widgets_to_layout(self):
        # Ajout des widgets aux layouts

        #################left-layout#######################
        self.left_layout.addWidget(self.title_label)

        # Ajouter des label au filter
        search_vbox = QtWidgets.QVBoxLayout()
        search_vbox.addWidget(MWidget.MHeader("Rechercher un anime"))
        search_vbox.addWidget(self.search_bar)
        search_vbox.setSpacing(10)
        search_vbox.addWidget(self.information_lbl)
        self.filter_layout.addLayout(search_vbox)

        cbb_vbox = QtWidgets.QVBoxLayout()
        cbb_vbox.addWidget(MWidget.MHeader("Langue"))
        cbb_vbox.addWidget(self.lang_ccb)
        cbb_vbox.setSpacing(10)
        self.filter_layout.addLayout(cbb_vbox)

        self.left_layout.addLayout(self.filter_layout)

        # mettre des label au anim_section_layout
        animelist_Vbox = QtWidgets.QVBoxLayout()

        line_layout = QtWidgets.QHBoxLayout()
        line_layout.addWidget(MWidget.MHeader("Liste des animes"))
        line_layout.addWidget(self.anime_laoding_button)

        animelist_Vbox.addLayout(line_layout)
        animelist_Vbox.addWidget(self.anime_list)
        animelist_Vbox.setSpacing(10)

        self.anim_section_layout.addLayout(animelist_Vbox)

        contentlist_Vbox = QtWidgets.QVBoxLayout()

        line_layout2 = QtWidgets.QHBoxLayout()
        line_layout2.addWidget(MWidget.MHeader("Contenu"))
        line_layout2.addWidget(self.content_loading_button)

        contentlist_Vbox.addLayout(line_layout2)
        contentlist_Vbox.addWidget(self.content_list)
        contentlist_Vbox.setSpacing(10)

        self.anim_section_layout.addLayout(contentlist_Vbox)

        self.left_layout.addLayout(self.anim_section_layout)
        # Fin

        ##################right-layout######################
        self.right_layout.addWidget(self.welcome_message)
        self.right_layout.addWidget(self.short_desc)
        self.right_layout.addWidget(self.short_info)

        # Ajout des layouts au layout
        leftWidget = QtWidgets.QWidget()
        leftWidget.setLayout(self.left_layout)
        leftWidget.setObjectName("left_widget")
        # leftWidget.setStyleSheet()
        leftWidget.setMinimumSize(500, 400)

        self.rightWidget = MWidget.MRightWidget()
        self.rightWidget.setLayout(self.right_layout)
        self.right_layout.setSpacing(50)
        self.right_layout.addStretch()

        self.main_layout.addWidget(leftWidget)
        self.main_layout.addWidget(self.rightWidget)

        # Définir le layout principal
        self.setLayout(self.main_layout)

    def connect_signals_to_slots(self):
        self.anime_laoding_button.clicked.connect(self.fetch_anime_list)
        self.content_loading_button.clicked.connect(self.printError)
        self.search_bar.textChanged.connect(self.filter_anime)
        self.anime_list.itemClicked.connect(self.load_item_content)
        self.content_list.itemClicked.connect(
            partial(self.show_chapiters_in_right_widget, force_reload=False)
        )

    def fetch_anime_list(self):
        self.disable_all()
        self.anime_laoding_button.start_loading()
        self.anime_sama_fething.partial_result_signal.connect(self.load_anime_list)
        self.anime_sama_fething.result_signal.connect(self.printResult)
        self.anime_sama_fething.error_signal.connect(self.printError)
        self.anime_sama_fething.progress_signal.connect(self.show_progress)

        self.anime_sama_fething.start()

    def load_anime_list(self, anime_list: list[dict[str, str]]):
        items_list = [
            self.anime_list.item(i).text() for i in range(self.anime_list.count())
        ]
        for anime in anime_list:
            if anime["name"] not in items_list:
                self.anime_list.addItem(anime["name"])

    def printResult(self, result):
        self.anime_laoding_button.stop_loading()
        self.enable_all()
        self.information_lbl.setText(result)

    def printError(self, error="hi"):
        QtWidgets.QMessageBox.information(
            self, "Erreur", error, QtWidgets.QMessageBox.StandardButton.Close
        )
        self.enable_all()
        self.anime_laoding_button.stop_loading()
        self.content_loading_button.stop_loading()
        self.chapiters_widget.loading_button.stop_loading()
        self.information_lbl.setText("Reessayer!!")

    def filter_anime(self, text):
        animeList = AnimeSamaAScrapper().get_animes(text)
        if animeList is None:
            return
        self.anime_list.clear()
        for anime in animeList:
            self.anime_list.addItem(anime["name"])

    def show_progress(self, progress):
        self.information_lbl.setText(f"Chargement des mangas... {progress}")

    def load_item_content(self, item):
        if self.anime_content_fething.isCurrentThread():
            return
        self.disable_all()

        self.anime_content_fething.setAnimeName(item.text())
        self.anime_content_fething.result_signal.connect(self.load_content_list)
        self.anime_content_fething.error_signal.connect(self.printError)

        self.content_loading_button.start_loading()
        self.anime_content_fething.start()

    def load_content_list(self, result):
        self.content_loading_button.stop_loading()
        self.enable_all()
        self.content_list.clear()
        for content in result:
            self.content_list.addItem(content["name"])

    def show_chapiters_in_right_widget(self, item=None, *, force_reload=False):
        right_widget = self.main_layout.itemAt(1).widget()
        if right_widget != None:
            right_widget.deleteLater()

        anime_name = self.anime_list.currentItem().text()
        content_name = self.content_list.currentItem().text()
        anime = AnimeSamaAScrapper().get_anime_contents(anime_name)  # type: ignore
        animeLink = next(
            content["link"] for content in anime if content["name"] == content_name
        )

        if "scan" in animeLink:
            language = "scan"
        else:
            language = self.lang_ccb.currentText()

        self.chapiters_widget = MWidget.ChapitersWidget(
            anime_name, content_name, language
        )
        self.chapiters_widget.loading_button.clicked.connect(
            partial(self.show_chapiters_in_right_widget, force_reload=True)
        )
        self.main_layout.addWidget(self.chapiters_widget)
        self.chapiters_widget.loading_button.start_loading()
        self.disable_all()
        self.chapitre_scrapper.setAnimeContent(content_name)
        self.chapitre_scrapper.setAnimeName(anime_name)
        self.chapitre_scrapper.setLanguage(language)
        self.chapitre_scrapper.setReload(force_reload)
        self.chapitre_scrapper.result_signal.connect(self.load_chapiters)
        self.chapitre_scrapper.error_signal.connect(self.printError)
        self.chapitre_scrapper.start()

    def disable_all(self):
        self.anime_laoding_button.setDisabled(True)
        self.content_loading_button.setDisabled(True)
        self.search_bar.setDisabled(True)
        self.anime_list.setDisabled(True)
        self.content_list.setDisabled(True)

    def enable_all(self):
        self.anime_laoding_button.setDisabled(False)
        self.content_loading_button.setDisabled(False)
        self.search_bar.setDisabled(False)
        self.anime_list.setDisabled(False)
        self.content_list.setDisabled(False)

    def load_chapiters(self, results):
        self.chapiters_widget.chapiters_list.clear()
        for result in results:
            self.chapiters_widget.add_item_in_listWidget(result)

        self.chapiters_widget.loading_button.stop_loading()
        self.enable_all()

