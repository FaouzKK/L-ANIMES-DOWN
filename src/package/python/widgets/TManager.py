import re
import concurrent.futures

from package.python.api.constant import DOWNLOAD_PATH


from PySide6 import QtCore
from package.python.api.asscrapper import AnimeSamaAScrapper
from package.python.api.asdownloader import AnimeSamaVideoDownloader,AnimeSamaMangaDownloader
from package.python.api.jsonmanager import JsonManager
from package.python.api import DownloadSate

class TSamaFethingsAll(QtCore.QThread):
    result_signal = QtCore.Signal(str)
    error_signal = QtCore.Signal(str)
    progress_signal = QtCore.Signal(str)
    partial_result_signal = QtCore.Signal(list)
        
    def __init__(self, parent=None):
        super().__init__(parent)
        self._anime_name = None
        
        
    def setAnimeName(self, anime_name):
        self._anime_name = anime_name
        
    def run(self):
        try:
            # anime_content = AnimeSamaAScrapper().get_animes(self._anime_name)
            # if anime_content != None:
            #     self.partial_result_signal.emit(anime_content)
            #     self.result_signal.emit(len(anime_content))
            #     return None 
            page_size = AnimeSamaAScrapper()._get_c_page_len()
            anime_count = 0
            self.progress_signal.emit(f'0/{page_size}')
            for i in range(1, page_size + 1):
                self.progress_signal.emit(f'{i}/{page_size}')
                resultArray = AnimeSamaAScrapper().fetch_page(i)
                if resultArray != None:
                    self.partial_result_signal.emit(resultArray)
                    AnimeSamaAScrapper().save_partel_in_json(resultArray)
                    anime_count += len(resultArray)
            
            self.result_signal.emit(f"Liste total : {anime_count}")
        except Exception as e:
            self.error_signal.emit(str(e)) # type: ignore


class TAnimeContentScrapper(QtCore.QThread):
    result_signal = QtCore.Signal(list)
    error_signal = QtCore.Signal(str)
    progress_signal = QtCore.Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._anime_name = None
        

    def setAnimeName(self, anime_name):
        self._anime_name = anime_name
    
    def run(self):
        if self._anime_name == None:
            self.error_signal.emit("Anime name is not set")
            return None
        try:
            animeContent = AnimeSamaAScrapper().get_anime_contents(anime_name=self._anime_name)
            self.result_signal.emit(animeContent)
        except:
            self.error_signal.emit("Error while scrapping anime content")
            return None


class TChapitersScrapper(QtCore.QThread):
    result_signal = QtCore.Signal(list)
    error_signal = QtCore.Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._anime_name = None
        self._anime_content = None

    def setAnimeName(self, anime_name):
        self._anime_name = anime_name

    def setAnimeContent(self, anime_content):
        self._anime_content = anime_content
    def setLanguage(self, language):
        self._language = language
    
    def setReload(self, reload:bool):
        self._reload:bool = reload

    def run(self):
        if self._anime_name == None or self._anime_content == None:
            return self.error_signal.emit("Anime name or anime content is not set")
        try:
            result = AnimeSamaAScrapper().get_content_list(anime_name=self._anime_name, anime_content=self._anime_content, lang=self._language,force_reload=self._reload)
            self.result_signal.emit(result)
        except:
            self.error_signal.emit("Aucune donee trouver pour cette langue")
            return None


class TChapiterDownloader(QtCore.QThread):
    result_signal = QtCore.Signal(str)
    error_signal = QtCore.Signal(str)
    progress_signal = QtCore.Signal(str)

    

    def __init__(self, parent=None):
        super().__init__(parent)
        self._anime_name = None
        self._anime_content = None
        self._chapter = None
        self.anime_scrapper = AnimeSamaAScrapper()
        self.anime_downloader = AnimeSamaVideoDownloader()
        self.manga_downloader = AnimeSamaMangaDownloader()
        self.json_manager = JsonManager()
    
    def setAnimeName(self, anime_name):
        self._anime_name = anime_name
        
    def setAnimeContent(self, anime_content):
        self._anime_content = anime_content
        
    def setLanguage(self, language):
        self._language = language

    def setChapter(self, chapter):
        self._chapter = chapter
    
    def run(self):
        if self._anime_name == None or self._anime_content == None or self._chapter == None:
            return self.error_signal.emit("Anime name or anime content or chapter is not set")
        try:
            contents = self.anime_scrapper.get_anime_contents(anime_name=self._anime_name)
            
            animeLink = next(content.get('link') for content in contents if content.get('name') == self._anime_content)
            
            if 'vostfr' in animeLink and self._language == 'vf':
                animeLink = animeLink.replace('vostfr','vf')
            
            if 'scan' in self._language:
                self.download_chapitre(animeLink,self._chapter)
                
            else:
                self.json_manager.save_download_data(self._anime_name, self._anime_content,self._language,self._chapter, DownloadSate.LOADING)
                
                self.downloadEpisode(animeLink,self._chapter) 
            
        except Exception as e:
            self.error_signal.emit(str(f"Une erreur est survenue lors du telechargement de {self._chapter} de l'anime {self._anime_name} : {e}"))
            return None
        
    
    def downloadEpisode(self,animeLink,chapiter):
        
        self.progress_signal.emit("recherhce...")
        
        master_mu38_request = self.anime_downloader.get_episode_m3u8_url(animeLink,chapiter)
        if master_mu38_request == None:
            return self.error_signal.emit("Aucun lien de telechargement disponible")
        try:
            
            master_mu38:dict = self.anime_downloader.get_m3u8_video_quality(master_mu38_request)
            if master_mu38 == None:
                return self.error_signal.emit("Aucun lien de telechargement disponible")
            
            keys = list(master_mu38.keys())
            
            final_key = None
            if '1080x720' in keys:
                final_key = '1080x720'
            elif '1920x1080' in keys:
                final_key = '1920x1080'
            else:
                final_key = keys[0]
            
            m3u8_url = master_mu38[final_key]
            
            self.progress_signal.emit("recuperation...")
            
            m3u8_segments = self.anime_downloader.download_m3u8(m3u8_url,master_mu38_request.headers.get('referer'))
            if m3u8_segments == None:
                raise Exception("Aucun lien de telechargement disponible")
            
            segemts_list = [segment for segment in m3u8_segments.splitlines() if segment.endswith('.ts')] # type: ignore
            
            result_file = DOWNLOAD_PATH / self.remove_invalide_character(self._anime_name) / self.remove_invalide_character(self._anime_content) / self.remove_invalide_character(f"{self._chapter}.mp4")
            
            if not result_file.exists():
                result_file.parent.mkdir(parents=True, exist_ok=True)
            if result_file.exists():
                result_file.touch()
            
            self.progress_signal.emit('telechargement...') 
            
            self.count = 0  
            
            def download_segments(index,segment,result_list):
                
                buffer = self.anime_downloader.download_segments(segment,master_mu38_request.headers.get('referer'))
                if buffer == None:
                    raise Exception("Aucun lien de telechargement disponible")
                result_list[index] = buffer
                
                self.count+= 1
                self.progress_signal.emit(f"progression {self.get_percentage(self.count,len(segemts_list))}%")
            
            chunk = 10 
            chunked_segemts_list = [segemts_list[i:i+chunk] for i in range(0, len(segemts_list), chunk)]
            
            for chunk in chunked_segemts_list:
                result = {}
                # Utilisation d'un ThreadPoolExecutor pour télécharger les segments en parallèle
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    # Créer un itérable de tuples (index, segment)
                    tasks = [(index, segment) for index, segment in enumerate(chunk)]
                    # Lancer l'exécution en parallèle
                    executor.map(lambda task: download_segments(task[0], task[1], result), tasks)

                # Écrire les segments téléchargés dans le fichier de sortie
                with open(result_file, 'ab') as f:
                    keys = list(result.keys())
                    keys.sort()
                    for key in keys:
                        f.write(result[key])
                
        
            self.result_signal.emit(result_file.as_posix())
            self.json_manager.save_download_data(self._anime_name,self._anime_content,self._language,self._chapter,result_file.as_posix()) # type: ignore
            
        except Exception as e:
            self.error_signal.emit(str(f"Une erreur est survenue lors du telechargement de {self._chapter} de l'anime {self._anime_name} : {e}"))
            
            self.json_manager.save_download_data(self._anime_name,self._anime_content,self._language,self._chapter,DownloadSate.ERROR) # type: ignore
            return None
        
        
      
    def download_chapitre(self,manga_link,chapiter):
        self.progress_signal.emit("recuperation...")
        
        manga_href = self.manga_downloader.scrapp_manga_href(manga_link,chapiter)
        
        if manga_href == None:
            raise Exception("Aucun lien de telechargement disponible")
        
        result_dir = DOWNLOAD_PATH / self.remove_invalide_character(self._anime_name) / self.remove_invalide_character(self._anime_content) / self.remove_invalide_character(f"{self._chapter}")
        
        self.json_manager.save_download_data(self._anime_name,self._anime_content,self._language,self._chapter,DownloadSate.LOADING) # type: ignore

        if not result_dir.exists():
            result_dir.mkdir(parents=True, exist_ok=True)
            
        self.progress_signal.emit("telechargement...")
        
        path = self.manga_downloader.downnload_manga_href(manga_href,'jpg',result_dir,True,self.progress_signal)
        
        self.result_signal.emit(path)
        self.json_manager.save_download_data(self._anime_name,self._anime_content,self._language,self._chapter,path) # type: ignore
        
    def get_percentage(self,index,lenght):
        return round((index/lenght)*100,2)
    
    
    def remove_invalide_character(self,dir_or_filename):
        return re.sub(r'[<>:"/\\|?*]', '', dir_or_filename)