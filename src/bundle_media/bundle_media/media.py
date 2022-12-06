from bs4 import BeautifulSoup


class Media:

    def get_media_url_from_text(self, text: str) -> str:
        soup = BeautifulSoup(text, 'html.parser')
        img = soup.select('img')
        if img:
            return [
                {
                    "url": i['src'], "alt_text": i['alt'] if "alt" in i else None
                } for i in img if i['src']
            ]
        else:
            return None