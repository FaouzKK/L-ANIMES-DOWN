from PySide6 import QtWidgets , QtCore , QtGui
from functools import partial


from package.python.api.constant import MEDIA_PATH
from package.python.api.jsonmanager import JsonManager
from package.python.widgets.TManager import TChapiterDownloader
from package.python.api import DownloadSate
from package.python.api.downloadthreatmanager import DownloadThreatManager


class MRightWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Assigner un nom unique à ce widget
        self.setObjectName("mRightWidget")


class MInfoLabel(QtWidgets.QLabel):
    def __init__(self, text=""):
        super().__init__(text)

        # Assigner un nom unique à ce widget
        self.setObjectName("mInfoLabel")

        self.setStyleSheet("font-size: 14px ; background-color: rgb(240, 240, 240); border-radius : 10px ; padding : 5px")
        self.setOpenExternalLinks(True)
        self.setWordWrap(True)
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignLeft)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Fixed)

class MHeader(QtWidgets.QLabel):
    def __init__(self, text=""):
        super().__init__(text)

        # Assigner un nom unique à ce widget
        self.setObjectName("mHeader")
        
class MLoadingButton(QtWidgets.QPushButton):
    def __init__(self, text=""):
        super().__init__(text)

        # Assigner un nom unique à ce widget
        self.setObjectName("mLoadingButton")
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        gif_path = MEDIA_PATH / 'loading.gif'
        self.loading_gif = QtGui.QMovie(gif_path.as_posix())
        self.loading_gif.setScaledSize(QtCore.QSize(20, 20))
        
        current_frame = self.loading_gif.currentPixmap()
        self.setIcon(QtGui.QIcon(current_frame))
        self.setIconSize(QtCore.QSize(24, 24))
        # Connecter le signal frameChanged pour mettre à jour l'icône
        self.loading_gif.frameChanged.connect(self.update_icon)

        # Initialiser l'icône avec la première frame
        self.loading_gif.jumpToFrame(0)
        self.update_icon()

    def update_icon(self):
        """Met à jour l'icône du bouton avec l'image actuelle du GIF."""
        current_frame = self.loading_gif.currentPixmap()
        self.setIcon(QtGui.QIcon(current_frame))
        self.setIconSize(QtCore.QSize(20, 20))

    def start_loading(self):
        """Démarre l'animation de chargement."""
        self.loading_gif.start()

    def stop_loading(self):
        """Arrête l'animation de chargement."""
        self.loading_gif.stop()
        self.loading_gif.jumpToFrame(0)  # Supprime l'icône
        
        
class infoLabel(QtWidgets.QLabel):
    def __init__(self, text=""):
        super().__init__(text)

        # Assigner un nom unique à ce widget
        self.setObjectName("infoLabel")


class ChapitersWidget(QtWidgets.QWidget):
    def __init__(self ,anime_name,anime_content,language, parent=None):
        super().__init__(parent)
        self.anime_name = anime_name
        self.content_name = anime_content
        self.language = language
        self.json_manager = JsonManager()
        
        # Assigner un nom unique à ce widget
        self.setObjectName("chapitersWidget")
        self.setMinimumWidth(500)
        self._setup_ui()
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        
    def _setup_ui(self):
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.addWidget(MHeader("Liste des chapitres/Episodes :"))
        self.main_layout.addWidget(MInfoLabel("<p>Vous pouvez cliquer sur un chapitre ou un episode pour le télécharger.</p>"))
        
        self.loading_button = MLoadingButton("Recharger la liste des chapitres")
        self.loading_button.setStyleSheet("background-color: rgb(240, 240, 240) ; padding : 10px  ; border-radius : 10px")
        self.main_layout.addWidget(self.loading_button)
        
        self.main_layout.setSpacing(20)
        self.setContentsMargins(10,10,10,10)

        self.chapiters_list = QtWidgets.QListWidget()
        self.chapiters_list.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.MinimumExpanding)
        self.chapiters_list.setObjectName('chapitersListWidget')
        self.main_layout.addWidget(self.chapiters_list)
        
        self.setLayout(self.main_layout)
        
        
    def add_item_in_listWidget(self,item_name):
        
        # for i in range(self.chapiters_list.count()):
        #     widgjet_item = self.chapiters_list.item(i)
        #     layout = widgjet_item.layout() # type: ignore
        #     chapiter_name = layout.itemAt(0).widget()
        #     if chapiter_name.text() == item_name:
        #         return
        
        layout = QtWidgets.QHBoxLayout()
        chapiter_name = QtWidgets.QLabel(item_name)
        
        download_info = self.json_manager.get_download_data(self.anime_name,self.content_name,self.language,item_name)
        
        
        def manage_download():
            download_btn.setDisabled(True)
            as_downloader = TChapiterDownloader()
            as_downloader.setAnimeName(self.anime_name)
            as_downloader.setAnimeContent(self.content_name)
            as_downloader.setLanguage(self.language)
            as_downloader.setChapter(item_name)
            DownloadThreatManager.add_threat(self.anime_name,self.content_name,self.language,item_name,as_downloader)
            as_downloader.progress_signal.connect(update_progress)
            as_downloader.result_signal.connect(inform_result)
            as_downloader.error_signal.connect(printError)
            
            as_downloader.start()

            
        def update_progress(progress):
            try:
                download_btn.setText(progress)
            except RuntimeError:
                pass
            
        def inform_result(result):
            try:
                download_btn.setDisabled(False)
                path = result
                
                def open_file():
                    QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(path))

                if path != None:
                    download_btn.setText("Ouvir")
                    download_btn.clicked.disconnect()  # Déconnecter toute connexion précédente
                    download_btn.clicked.connect(open_file)
            except RuntimeError:
                pass

        def printError(error):
            try:
                download_btn.setDisabled(False)
                download_btn.setText("Erreur survenue")
                message = QtWidgets.QErrorMessage()
                message.showMessage(f"Une erreur est survenue lors du telechargement de {self.anime_name} - {self.content_name} - {self.language} - {item_name} : {error}")
                message.exec_()
            except RuntimeError:
                pass

        download_btn = QtWidgets.QPushButton()
        
        if download_info is not None:
            progress = download_info.get('progress')
            
            if progress == DownloadSate.ERROR :
                download_btn.setText('Reesayer')
                download_btn.clicked.connect(manage_download)
                
            elif progress == DownloadSate.LOADING:
                threat: TChapiterDownloader = DownloadThreatManager.get_threat(self.anime_name,self.content_name,self.language,item_name) # type: ignore
                
                if threat is not None:
                    
                    if threat.isRunning():
                        download_btn.setDisabled(True)
                        download_btn.setText('En cours de telechargement')
                        threat.progress_signal.connect(update_progress)
                        threat.result_signal.connect(inform_result)
                else:
                    download_btn.setText('Reessayer')
                    download_btn.clicked.connect(manage_download)
                    
            else:
                path = progress
                download_btn.clicked.connect(lambda: QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(path)))
                download_btn.setText("Ouvrir")
                

        else:
            download_btn.setText("Télécharger")
            download_btn.clicked.connect(manage_download)


        layout.addWidget(chapiter_name)
        layout.addWidget(download_btn)
        
        item_widget = QtWidgets.QWidget()
        item_widget.setLayout(layout)
        
        list_widget = QtWidgets.QListWidgetItem()
        list_widget.setSizeHint(item_widget.sizeHint())
        self.chapiters_list.addItem(list_widget)
        self.chapiters_list.setItemWidget(list_widget, item_widget)
            
        
        
    
        
        
    