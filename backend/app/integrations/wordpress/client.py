import requests

class WordPressClient:
    def __init__(self, url, username, password):
        self.url = url.rstrip("/")
        self.session = requests.Session()
        self.session.auth = (username, password)
    
    def get_posts(self):
        response = self.session.get(
            f"{self.url}/wp-json/wp/v2/posts"
        )
        response.raise_for_status()
        return response.json()
    
    def get_categories(self):
        response = self.session.get(
            f"{self.url}/wp-json/wp/v2/categories"
        )
        response.raise_for_status()
        return response.json()
    
    def get_tags(self):
        response = self.session.get(
            f"{self.url}/wp-json/wp/v2/tags"
        )
        response.raise_for_status()
        return response.json()
