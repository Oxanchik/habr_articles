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

def has_keywords(text: str):
    text = text.lower()
    return [kw for kw in keywords if kw in text]

page = session.get(URL, timeout=20)
page.raise_for_status()

soup = BeautifulSoup(page.text, 'html.parser')

for article in soup.select('article.tm-articles-list__item'):
    title_el = article.select_one('h2.tm-title a')
    if not title_el:
        continue

    title = title_el.text.replace('\n', '').strip()
    link = urljoin(URL, title_el.get('href', ''))

    time_el = article.select_one('time')
    date = time_el.get('datetime', '').strip() if time_el else ''

    preview_parts = [title]

    preview_block = article.select_one('.article-formatted-body')
    if preview_block:
        preview_parts.append(preview_block.text.replace('\n', '').strip())

    tags = article.select('.tm-publication-hub__link span, .tm-publication-hub__link')
    preview_parts.extend(tag.text.replace('\n', '').strip() for tag in tags if tag.get_text(strip=True))

    tags_text = ' '.join(tag.text.replace('\n', '').strip() for tag in tags if tag.get_text(strip=True))
    if tags_text:
        preview_parts.append(tags_text)
    preview_text = ' '.join(preview_parts).lower()

    fields = [
        ('заголовок', title),
        ('превью', preview_text),
        ('теги', tags_text),
    ]

    found = []
    for field_name, field_text in fields:
        matched = has_keywords(field_text)
        if matched:
            found.append(f'{field_name}: {", ".join(matched)}')

    if found:
        print(f'{date} – {title} – {link} – найдено в: {", ".join(found)}')