import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

KEYWORDS = ['дизайн', 'фото', 'web', 'python']

URL = 'https://habr.com/ru/articles/'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36'
}

session = requests.Session()
session.headers.update(HEADERS)

keywords = [kw.lower() for kw in KEYWORDS]

def has_keywords(text: str) -> bool:
    text = text.lower()
    return any(kw in text for kw in keywords)

page = session.get(URL, timeout=20)
page.raise_for_status()

soup = BeautifulSoup(page.text, 'html.parser')

for article in soup.select('article.tm-articles-list__item'):
    title_el = article.select_one('h2.tm-title a')
    if not title_el:
        continue

    title = title_el.text.replace('\n', ' ').strip()
    link = urljoin(URL, title_el.get('href', ''))

    time_el = article.select_one('time')
    date = time_el.get('datetime', '').strip() if time_el else ''

    preview_block = article.select_one('.article-formatted-body') or article
    preview_text = preview_block.text.replace('\n', ' ').strip().lower()

    if has_keywords(preview_text):
        print(f'{date} – {title} – {link}')
        continue

    if link:
        article_page = session.get(link, timeout=20)
        article_page.raise_for_status()
        article_soup = BeautifulSoup(article_page.text, 'html.parser')

        full_text_block = article_soup.select_one('.article-formatted-body') or article_soup.select_one('.tm-article-body')
        full_text = full_text_block.text.replace('\n', ' ').strip().lower() if full_text_block else article_soup.text.replace('\n', ' ').strip().lower()

        if has_keywords(full_text):
            print(f'{date} – {title} – {link}')