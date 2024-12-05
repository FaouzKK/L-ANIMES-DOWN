class DownloadThreatManager:
    
    threat_list = []  # Liste statique pour stocker les threads
    
    @staticmethod
    def add_threat(anime_name, content_name, lang, chapter, thread):
        """
        Ajouter un thread à la liste de gestion des threads de téléchargement.
        """
        DownloadThreatManager.threat_list.append({
            "anime_name": anime_name,
            "content_name": content_name,
            "lang": lang,
            "chapter": chapter,
            "thread": thread
        })
        
    @staticmethod
    def get_threat_list():
        """
        Retourner la liste de tous les threads enregistrés.
        """
        return DownloadThreatManager.threat_list

    @staticmethod
    def get_threat(anime_name, content_name, lang, chapter):
        """
        Trouver un thread spécifique basé sur les critères donnés.
        """
        for threat in DownloadThreatManager.threat_list:
            if (threat["anime_name"] == anime_name and 
                threat["content_name"] == content_name and 
                threat["lang"] == lang and 
                threat["chapter"] == chapter):
                return threat.get('thread')  # Retourner le thread correspondant
        return None  # Aucun thread trouvé
