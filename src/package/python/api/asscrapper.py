import requests
from bs4 import BeautifulSoup
from playwright import sync_api

from package.python.api.constant import ANIMESAMA_LINK,ANIMESAMA_CATALOGUE
from package.python.api.jsonmanager import JsonManager

class AnimeSamaAScrapper:
    def __init__(self):
        pass
    
    
    
    def get_animes(self, anime_name:str | None = None):
        try:
            
            annimelist = self._get_animelist()
            if annimelist is None:
                return None
            
            if anime_name is None or  anime_name.strip() == '':
                return annimelist
            
            else:
                return [anime for anime in annimelist if anime_name.lower() in anime['name'].lower()] # type: ignore

        except Exception as e:
            raise e
            
    
    def get_anime_contents(self, anime_name:str):
        try:
            anime = self.get_animes(anime_name)
            if anime is None:
                raise Exception('Anime not found')
            anime = anime[0]

            json_result = JsonManager().getanimejsonData(anime['name'])
            if json_result is not None:
                return json_result

            else:
                with sync_api.sync_playwright() as pw:
                    browser = pw.firefox.launch(headless=True)
                    page = browser.new_page()
                    page.goto(anime['link'], timeout=30000, wait_until='networkidle')

                    accept_cokkie = page.get_by_role('button', name="J'ACCEPTE")
                    try:
                        accept_cokkie.wait_for(state='visible', timeout=15000)
                        accept_cokkie.click()
                    except:
                        print('No cookie found')
                    content = page.content()
                    
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    divs = soup.select('div#sousBlocMilieu div.flex.flex-wrap')
                    
                    anime_contents = []
                    for div in divs:
                        anchor_elements = div.select('a')
                        for anchor in anchor_elements:
                            anime_contents.append({
                                'name': anchor.select_one('div').text, # type: ignore
                                'link': anime['link'].removesuffix('/') + "/" + anchor['href'] # type: ignore
                            })
                    
                    JsonManager().saveanimejsonData(anime['name'], anime_contents)
                    return anime_contents
                    
           
        except Exception as e:
            raise e
    
    
    def _get_animelist(self):
        try:
            animelist = JsonManager().get_animelist()
            return animelist    
        except Exception as e:
            raise e
    
        
    def _get_c_page_len(self):
        result = requests.get(ANIMESAMA_CATALOGUE)
        if result.status_code != 200:
            raise Exception('Error while getting the page length')
        
        soup = BeautifulSoup(result.text, 'html.parser')
        page_len = soup.select_one('div#nav_pages > div > a:last-child')
        if page_len is None:
            raise Exception('Error while getting the page length')
        return int(page_len.text)
    
    
    def save_partel_in_json(self,results):
        content = JsonManager().get_animelist()
        if content != None:
            for result in results:
                if result not in content:
                    content.append(result) # type: ignore
        else :
            content = results
        
        JsonManager().save_anime_list(content)
    
    
    def fetch_page(self,i):
            anime_in_page = []
            with sync_api.sync_playwright() as pw:
                print("Gettings data from page : {i}".format(i=i))
                browser = pw.firefox.launch(headless=True)
                page = browser.new_page()
                page.goto(f'{ANIMESAMA_CATALOGUE}/index.php?page={i}', timeout=30000, wait_until='domcontentloaded')

                accept_cokkie = page.get_by_role('button', name="J'ACCEPTE")
                try:
                    accept_cokkie.wait_for(state='visible', timeout=15000)
                    accept_cokkie.click()
                except:
                    print('No cookie found')
                content = page.content()
                page.close()
                
                soup = BeautifulSoup(content, 'html.parser')
                catalogue_list = soup.select('#result_catalogue > div.cardListAnime')

                if catalogue_list:
                    for anime in catalogue_list:
                        anime_dict = {}
                        anime_dict['link'] = anime.select_one('a').get('href')  # type: ignore
                        anime_dict['name'] = anime.select_one('h1').text.capitalize()  # type: ignore
                        anime_in_page.append(anime_dict)

            return anime_in_page
    
    
    
    def get_content_list(self, anime_name,anime_content,lang,force_reload:bool):
        
        if not force_reload:
            jsonContent = JsonManager().getcontentJsonData(anime_name,anime_content,lang)
            if jsonContent != None:
                return jsonContent
        
        anime_content_result = self._fetch_chapiters_list(anime_name,anime_content,lang)
        
        if anime_content_result != None:
            JsonManager().savecontentJsonData(anime_name,anime_content,anime_content_result,lang)
            return anime_content_result
        raise Exception('Error while getting the anime content')
    
        
    def _fetch_chapiters_list(self, anime_name,anime_content,lang):
        try:
            anime_content_result:list = self.get_anime_contents(anime_name)
            chapiters_list = []
            anime_link = next((x['link'] for x in anime_content_result if x['name'] == anime_content), None)
            # print(anime_link)
            if anime_link is None:
                raise Exception('Error while getting the anime link')
            
            if 'scan' not in anime_link and lang != 'vostfr':
                anime_link = anime_link.replace('vostfr','vf')
            
            with sync_api.sync_playwright() as pw:
                browser = pw.firefox.launch(headless=True)
                page = browser.new_page()
                response = page.goto(anime_link, timeout=30000, wait_until='domcontentloaded') 

                if response != None and response.status != 200: 
                    raise Exception('Error while getting the anime page')
                    
                accept_cokkie = page.get_by_role('button', name="J'ACCEPTE")
                try:
                    accept_cokkie.wait_for(state='visible', timeout=15000)
                    accept_cokkie.click()
                except:
                    print('No cookie found')
                result = page.content()
            
            soup = BeautifulSoup(result, 'html.parser')
            
            if 'scan' in anime_link:
                chapiters = soup.select('select#selectChapitres > option')
                for chap in chapiters:
                    chapiters_list.append(chap.text)

            else:
                chapiters = soup.select('select#selectEpisodes > option')
                for chap in chapiters:
                    chapiters_list.append(chap.text)
            
            return chapiters_list
        
        except Exception as e:
            raise e
        
        