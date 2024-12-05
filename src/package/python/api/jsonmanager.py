import json
import re
from datetime import datetime, timedelta
from pathlib import Path

from package.python.api.constant import BASE_DATA_DIR

class JsonManager:
    def __init__(self):
        self.animelistefile = BASE_DATA_DIR / 'animelist.json'
        self.downloadlistfile = BASE_DATA_DIR / 'downloadlist.json'
        
        # Créer le fichier s'il n'existe pas
        self._initialize_file()
    
    def _initialize_file(self):
        """Initialise le fichier JSON avec une structure par défaut."""
        try:
            if not self.animelistefile.exists():
                self.animelistefile.touch(exist_ok=True)
                with open(self.animelistefile, 'w') as f:
                    json.dump({
                        'animes': [],
                        'last_fetch': None
                    }, f)
            
            if not self.downloadlistfile.exists():
                self.downloadlistfile.touch(exist_ok=True)
                with open(self.downloadlistfile, 'w') as f:
                    json.dump([],f)
        
        except IOError as e:
            print(f"Erreur lors de la création du fichier : {e}")
            
    
    def get_animelist(self):
        """Retourne la liste des animes si les données sont récentes."""
        try:
            with open(self.animelistefile, 'r',encoding='utf-8') as f:
                content = json.load(f)
            
            # Vérification de la structure attendue
            if 'animes' not in content or 'last_fetch' not in content:
                print("Structure du fichier JSON invalide. Réinitialisation.")
                self._initialize_file()
                return None
            
            # Vérifier si les données sont récentes
            last_fetch = content['last_fetch']
            if last_fetch is None or datetime.now() - datetime.fromtimestamp(last_fetch) > timedelta(days=7):
                return None
            
            return content['animes']
        
        except (IOError, json.JSONDecodeError) as e:
            print(f"Erreur lors de la lecture du fichier : {e}")
            return None
    
    def save_anime_list(self,animelist):
        try:
            animelist.sort(key=lambda x: x['name'])
            with open(self.animelistefile, 'w',encoding='utf-8') as f:
                json.dump({
                    'animes': animelist,
                    'last_fetch': datetime.now().timestamp()
                }, f)
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la liste des animes : {e}")
            return False
    
    def getanimejsonData(self,animename:str):
        
        json_data_file = BASE_DATA_DIR / f'{self.sanitize_filename("-".join(animename.split()).lower())}.json'
        
        if not json_data_file.exists():
            return None

        try:
            with open(json_data_file, 'r',encoding='utf-8') as f:
                content = json.load(f)
            if content.get('last_fetch') is None or datetime.now() - datetime.fromtimestamp(content.get('last_fetch')) > timedelta(days=1):
                return None
            return content.get('list')
        except (IOError, json.JSONDecodeError) as e:
            print(f"Erreur lors de la lecture du fichier : {e}")
            return None
        
    def saveanimejsonData(self,animename:str,animelist):
        json_data_file = BASE_DATA_DIR / f'{self.sanitize_filename("-".join(animename.split()).lower())}.json'

        try:
            with open(json_data_file, 'w',encoding='utf-8') as f:
                json.dump({
                    'list': animelist,
                    'last_fetch' : datetime.now().timestamp()
                }, f)
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la liste des animes : {e}")
            return False
    
    
    def getcontentJsonData(self,animename:str,animecontent:str,lang):

        try:
            content = self.getanimejsonData(animename)
            
            if content is None:
                return None
            
            anime_index = None

            for anime in content: # type: ignore
                if anime.get('name') == animecontent:
                    anime_index = content.index(anime) # type: ignore
                    break
                
            if anime_index is None:
                return None
            
            if content[anime_index].get('list') is None:
                return None
            
            final_result = content[anime_index]['list'][lang] # type: ignore
                
            if final_result is None or len(final_result) == 0:
                    return None
            
            return final_result
            
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier : {e}")
            return None
    
    
    def savecontentJsonData(self,animename:str,animecontent:str,animelist,lang):

        previos_content = self.getanimejsonData(animename)
        
        try:
            if previos_content is None:
                raise Exception("Le fichier json n'existe pas")
            
            content_index = None
            
            for content in previos_content :
                if content.get('name') == animecontent:
                    content_index = previos_content.index(content)
                    break
                
            if content_index is None:
                raise Exception("Le contenu n'existe pas")
            
            if previos_content[content_index].get('list') is None:
                previos_content[content_index]['list'] = {lang:None}
            
            previos_content[content_index]['list'][lang] = animelist

            self.saveanimejsonData(animename,previos_content)
            
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la liste des animes : {e}")
            return False
        

    def sanitize_filename(self,filename):
        # Supprime les caractères non valides
        return re.sub(r'[<>:"/\\|?*]', '', filename)
    
    
    
    #Management des telechargement
    def get_download_data(self,animename:str,animecontent:str,lang,chapiter:str):
        try:
            with open(self.downloadlistfile,'r',encoding='utf-8') as f:
                content = json.load(f)
            
            result = next((x for x in content if x['name'] == animename and x['content'] == animecontent and x['lang'] == lang and x['chapiter'] == chapiter),None)
            
            return result
    
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier : {e}")
            return None
    
    def get_all_download_data(self):
        try:
            with open(self.downloadlistfile,'r',encoding='utf-8') as f:
                content = json.load(f)
            return content

        except Exception as e:
            print(f"Erreur lors de la lecture du fichier : {e}")
            return None
    
    def save_download_data(self,animename:str,animecontent:str,lang, chapiter:str,progress):
        try:
            content = self.get_all_download_data()

            if content is None:
                content = []
            
            data_index = None

            for data in content:
                if data.get('name') == animename and data.get('content') == animecontent and data.get('lang') == lang and data.get('chapiter') == chapiter:
                    data_index = content.index(data)
                    break

            if data_index is None:
                content.append({'name':animename,'content':animecontent,'lang':lang,'chapiter':chapiter,'progress':progress})
            else:
                content[data_index] = {'name':animename,'content':animecontent,'lang':lang,'chapiter':chapiter,'progress':progress}

            with open(self.downloadlistfile,'w',encoding='utf-8') as f:
                json.dump(content,f,indent=4,ensure_ascii=False)

            return True
    
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du fichier : {e}")
            return False


