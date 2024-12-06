import time
from pathlib import Path

import requests
from playwright import sync_api
import img2pdf

Debug = False
Debug = not Debug

class AnimeSamaVideoDownloader:
    def __init__(self):
        self.episode_m3u8 = None
    
    
    def get_episode_m3u8_url(self, url:str, episode:str|None=None):
        try:
            with sync_api.sync_playwright() as p:
                self.get_episode_browser = p.firefox.launch(headless=False)
                
                # Ouverture du browser 
                self.get_episode_page = self.get_episode_browser.new_page()
                self.get_episode_page.on('request',self._get_episode_m3u8)
                # page.route('**/*', self._close_redirect)
                #Activer la page
                try:
                    self.get_episode_page.goto(url,timeout=60_000,wait_until='domcontentloaded')
                except:
                    raise Exception('Erreur survenue lors de l\'acces a la page')
                
                accept_cokkie = self.get_episode_page.get_by_role('button',name='J\'ACCEPTE')
                
                try:
                    accept_cokkie.wait_for(state='visible',timeout=15000)
                    accept_cokkie.click()
                except:
                    print('no cokkie founded')
                
                #Changer de episode si requis:
                if episode is not None:
                    try:
                        self.get_episode_page.select_option('#selectEpisodes', episode.capitalize())
                    except :
                        raise Exception('Erreur survenue lors de la recherche du selecteur d\'episode')
                    
                play_button = self.get_episode_page.locator("#playerDF").content_frame.get_by_role("button", name="Play")
                try_count = 0
                while try_count < 5:  # Limiter à 5 tentatives
                    if self.episode_m3u8:  # Si l'URL est capturée, quitter
                        break
                    if play_button.is_visible():
                        try:
                            play_button.click(force=True)
                            time.sleep(5 if try_count < 2 else 10)
                            try_count += 1
                        except:
                            print("Erreur lors du clic sur le bouton Play.")
                # Attendre que l'URL m3u8 soit récupérée avant de fermer
                if self.episode_m3u8 is not None:
                    return self.episode_m3u8
        except Exception as e:
            if self.episode_m3u8:
                return self.episode_m3u8
            else :
                raise e
    
     
     
    ##############################get_episode_callback#############################################
    def _close_redirect(self,route):
        response = route.fetch()
        if response.status in {301, 302, 303}:
            route.abort()
        else:
            route.continue_() 
    
    def _get_episode_m3u8(self,request):
        global CanClose
        if ".m3u8" in request.url:
            print(f"m3u8 founded")
            if 'urlset/master' in request.url:
                print(f'master found {request.url}')
                self.episode_m3u8 = request
                
                
        else:
            pass
    
    ################################################################################################
    
    def get_m3u8_video_quality(self,request):
        result = requests.get(request.url,headers=request.headers)
        
        if result.status_code == 200:
            video_quality: dict[str,str] = {}
            for index,line in enumerate(result.text.splitlines()):
                if '#EXT-X-STREAM-INF' in line:
                    resolution = line.split('RESOLUTION=')[1].split(',')[0]
                    video_quality[resolution] = result.text.splitlines()[index+1]

            return video_quality  
        else:
            raise Exception('Erreur survenue lors de la recuperation du m3u8')

    ##Fonction pour telecharger le m3u8 conteneant les segment
    def download_m3u8(self,url,referer):
        result = requests.get(url,headers={'referer':referer})
        if result.status_code == 200:
            return result.text
        else:
            raise Exception('Erreur survenue lors de la recuperation du m3u8')
        
    ##Fonction pour telecharger un segment
    def download_segments(self,url,referer):
        result = requests.get(url,headers={'referer':referer})
        if result.status_code == 200:
            return result.content
        else:
            raise Exception('Erreur survenue lors de la recuperation du m3u8')
 
 
 

class AnimeSamaMangaDownloader():
    def __init__(self):
        pass
 
    def scrapp_manga_href(self, url:str, chapitre:str|None=None):
        try:
            with sync_api.sync_playwright() as pw:
                browser = pw.firefox.launch(headless=Debug)
                page = browser.new_page()
                try:
                    page.goto(url,timeout=60_000,wait_until='domcontentloaded')
                except:
                    raise Exception('Erreur survenue lors de la connexion a la page')
                
                accept_cokkie = page.get_by_role('button',name='J\'ACCEPTE')
                    
                try:
                    accept_cokkie.wait_for(state='visible',timeout=15000)
                    accept_cokkie.click()
                except:
                    print('no cokkie founded')
                
                #Changer de episode si requis:
                if  chapitre is not None:
                    try:
                        page.select_option('#selectChapitres', chapitre.capitalize())
                    except :
                        raise Exception('Erreur survenue lors de la recherche du selecteur d\'episode')
                
                mangas_href_len = 0
                try_count = 0
                
                while True:
                    mangas_href = page.query_selector_all('#scansPlacement > img')
                    if len(mangas_href) > mangas_href_len:
                        mangas_href_len = len(mangas_href)
                        try_count = 0
                    else:
                        try_count += 1
                        if try_count == 3:
                            break
                        time.sleep(3)
                finale_array = []
                for manga in mangas_href:
                    finale_array.append(manga.get_attribute('src'))
                return finale_array
        
        except Exception as e:
            raise e
            
            
    def downnload_manga_href(self,  url:list[str],  type:str="jpg", file_path:str|Path="output",pdf=False,progress_sigal=None):
        
        if isinstance(file_path, str):
            file_path = Path(file_path)
            if not file_path.exists():
                file_path.mkdir()
                
        progress_sigal.emit(f"recupération des images...") # type: ignore
        try:
            for index,element in enumerate(url):
                with open(file_path / f'{index}.{type}','wb') as f:
                    f.write(requests.get(element).content)
                    progress_sigal.emit(f"Telechargement... {index+1}/{len(url)}") # type: ignore
        except Exception as e:
            raise e    
        if not pdf :
            return file_path.resolve()
        
        else:
            imgs = file_path.glob(f'*.{type}')
            imgs = sorted(imgs, key=lambda x: int(x.stem))
            imgs = [img.resolve() for img in imgs]
            
            progress_sigal.emit(f"conversion en pdf...") # type: ignore
            
            with open(file_path.as_posix() + '.pdf', "wb") as f:
                f.write(img2pdf.convert(imgs)) # type: ignore
            for img in imgs:
                img.unlink()
            file_path.rmdir()
            return file_path.as_posix() + '.pdf'

 
 
 

 
############################################tester#################################################

if __name__ == '__main__':
    anime = AnimeSamaVideoDownloader()
    RESUL = anime.get_episode_m3u8_url("https://anime-sama.fr/catalogue/dandadan/saison1/vostfr/")
    print(RESUL)