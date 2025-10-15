import requests
from bs4 import BeautifulSoup
import logging
import re
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class ITProgerParser:
    def __init__(self):
        self.base_url = "https://itproger.com"
        self.news_url = "https://itproger.com/news"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def parse_articles(self, page=1):
        """Парсинг статей с указанной страницы"""
        try:
            # Правильные URL для itproger.com
            if page == 1:
                url = self.news_url
            else:
                url = f"{self.news_url}/page-{page}"

            logger.info(f"Parsing URL: {url}")

            response = self.session.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            articles = []

            # Основной контейнер со статьями на itproger.com
            articles_container = soup.find('div', class_='allArticles')

            if not articles_container:
                # Альтернативный поиск
                articles_container = soup.find('main') or soup.find('div', class_=re.compile(r'content|main'))

            if articles_container:
                # Ищем все div с классом article внутри контейнера
                article_containers = articles_container.find_all('div', class_='article')
                logger.info(f"Found {len(article_containers)} articles in container")
            else:
                article_containers = []
                logger.warning("No articles container found")

            for container in article_containers:
                article = self._parse_article_card(container)
                if article and article['title'] and article['title'] != "Без заголовка":
                    articles.append(article)

            return articles

        except Exception as e:
            logger.error(f"Error parsing articles from page {page}: {e}")
            return []

    def _parse_article_card(self, container):
        """Парсинг карточки статьи согласно структуре HTML itproger.com"""
        try:
            article = {}

            # Заголовок - находится в span внутри ссылки
            title_elem = container.find('a')
            if title_elem:
                # Ищем span с заголовком
                title_span = title_elem.find('span')
                if title_span:
                    article['title'] = title_span.get_text().strip()
                else:
                    article['title'] = title_elem.get_text().strip()

                # Ссылка
                if title_elem.get('href'):
                    article['link'] = urljoin(self.base_url, title_elem['href'])
                else:
                    article['link'] = ""
            else:
                article['title'] = "Без заголовка"
                article['link'] = ""

            # Изображение
            img_elem = container.find('img')
            if img_elem and img_elem.get('src'):
                article['image'] = urljoin(self.base_url, img_elem['src'])
            else:
                article['image'] = ""

            # Описание - второй span в контейнере
            spans = container.find_all('span')
            if len(spans) >= 2:
                description = spans[1].get_text().strip()
                # Очищаем описание от лишних пробелов
                description = re.sub(r'\s+', ' ', description)
                if len(description) > 200:
                    article['description'] = description[:200] + "..."
                else:
                    article['description'] = description
            else:
                article['description'] = ""

            # Мета-информация (просмотры и дата)
            meta_div = container.find('div')
            if meta_div:
                meta_text = meta_div.get_text().strip()

                # Извлекаем количество просмотров
                views_match = re.search(r'(\d+)\s*<', meta_text)
                if views_match:
                    views = views_match.group(1)
                else:
                    # Альтернативный поиск просмотров
                    views_match = re.search(r'(\d+)\s*просмотр', meta_text)
                    views = views_match.group(1) if views_match else "0"

                # Извлекаем дату
                date_match = re.search(r'(\d{1,2}\s+\w+\s+\d{4}\s+в\s+\d{1,2}:\d{2})', meta_text)
                if date_match:
                    date = date_match.group(1)
                else:
                    # Альтернативный формат даты
                    date_match = re.search(r'(\d{2}\.\d{2}\.\d{4})', meta_text)
                    date = date_match.group(1) if date_match else ""

                article['meta'] = f"{views} просмотров • {date}" if date else f"{views} просмотров"
                article['views'] = views
            else:
                article['meta'] = ""
                article['views'] = "0"

            logger.debug(f"Parsed article: {article['title'][:30]}...")
            return article

        except Exception as e:
            logger.error(f"Error parsing article card: {e}")
            return {}

    def get_total_pages(self):
        """Получение общего количества страниц"""
        try:
            response = self.session.get(self.news_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Ищем пагинацию itproger.com
            pagination = soup.find('div', class_='pagination')

            if pagination:
                # Ищем все ссылки в пагинации
                page_links = pagination.find_all('a')
                page_numbers = []

                for link in page_links:
                    try:
                        text = link.get_text().strip()
                        if text.isdigit():
                            page_numbers.append(int(text))
                    except ValueError:
                        continue

                if page_numbers:
                    max_page = max(page_numbers)
                    logger.info(f"Found {max_page} total pages from pagination")
                    return max_page

                # Если нет цифровых ссылок, проверяем есть ли многоточие (значит страниц много)
                if pagination.find('span', string='...'):
                    logger.info("Found ellipsis in pagination, using 84 pages")
                    return 84

            # Проверяем есть ли ссылка на последнюю страницу
            last_page_link = pagination.find('a', href=re.compile(r'page-84')) if pagination else None
            if last_page_link:
                logger.info("Found direct link to page 84")
                return 84

            # Если пагинация не найдена или не удалось определить, возвращаем 84
            logger.info("Using default 84 pages")
            return 84

        except Exception as e:
            logger.error(f"Error getting total pages: {e}")
            return 84

    def parse_full_article(self, article_url):
        """Парсинг полного содержимого статьи"""
        try:
            response = self.session.get(article_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Ищем основной контент статьи на itproger.com
            content_elem = (soup.find('article') or
                            soup.find('div', class_='content') or
                            soup.find('div', class_=re.compile(r'post-content|article-content')))

            if not content_elem:
                return "📝 Полное содержимое статьи будет доступно в ближайшее время!"

            # Извлекаем текст и форматируем его в Markdown
            full_text = self._extract_formatted_text(content_elem)

            if not full_text:
                # Альтернативный метод: собираем все параграфы
                paragraphs = content_elem.find_all('p')
                full_text = "\n\n".join(p.get_text().strip() for p in paragraphs if p.get_text().strip())

            return full_text if full_text else "📝 Полное содержимое статьи будет доступно скоро!"

        except Exception as e:
            logger.error(f"Error parsing full article: {e}")
            return "📝 Полное содержимое статьи будет доступно в ближайшее время!"

    def _extract_formatted_text(self, element):
        """Извлечение форматированного текста с поддержкой Markdown"""
        try:
            # Удаляем ненужные элементы
            for unwanted in element(['script', 'style', 'nav', 'header', 'footer', 'aside', 'form']):
                unwanted.decompose()

            text_parts = []

            # Обрабатываем основные элементы
            for elem in element.find_all(['h1', 'h2', 'h3', 'h4', 'p', 'pre', 'code', 'ul', 'ol', 'blockquote']):
                if elem.name in ['h1', 'h2', 'h3', 'h4']:
                    text = elem.get_text().strip()
                    if text:
                        level = int(elem.name[1])
                        text_parts.append(f"{'#' * level} {text}\n\n")

                elif elem.name == 'p':
                    text = elem.get_text().strip()
                    if text and len(text) > 10:  # Игнорируем короткие параграфы (могут быть мета-данными)
                        text_parts.append(f"{text}\n\n")

                elif elem.name == 'pre':
                    code_text = elem.get_text().strip()
                    if code_text:
                        text_parts.append(f"```\n{code_text}\n```\n\n")

                elif elem.name == 'code':
                    if elem.parent and elem.parent.name != 'pre':
                        text = elem.get_text().strip()
                        if text:
                            text_parts.append(f"`{text}` ")

                elif elem.name == 'ul':
                    items = []
                    for li in elem.find_all('li'):
                        text = li.get_text().strip()
                        if text:
                            items.append(f"• {text}")
                    if items:
                        text_parts.append("\n".join(items) + "\n\n")

                elif elem.name == 'ol':
                    items = []
                    for i, li in enumerate(elem.find_all('li'), 1):
                        text = li.get_text().strip()
                        if text:
                            items.append(f"{i}. {text}")
                    if items:
                        text_parts.append("\n".join(items) + "\n\n")

                elif elem.name == 'blockquote':
                    text = elem.get_text().strip()
                    if text:
                        text_parts.append(f"> {text}\n\n")

            result = ''.join(text_parts)
            result = re.sub(r'\n{3,}', '\n\n', result).strip()

            # Ограничиваем длину для телеграма
            if len(result) > 4000:
                result = result[:4000] + "...\n\n📖 Читать продолжение на сайте"

            return result if result else None

        except Exception as e:
            logger.error(f"Error extracting formatted text: {e}")
            return None

    def test_parsing(self, page=1):
        """Тестовая функция для проверки парсинга"""
        articles = self.parse_articles(page)
        print(f"=== Page {page} ===")
        for i, article in enumerate(articles, 1):
            print(f"{i}. {article['title']}")
            print(f"   Description: {article['description'][:50]}...")
            print(f"   Image: {article['image'][:50]}...")
            print(f"   Meta: {article['meta']}")
            print()
        return articles


# Тестирование парсера
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = ITProgerParser()

    # Тест парсинга первой страницы
    articles = parser.test_parsing(1)

    # Проверка количества страниц
    total_pages = parser.get_total_pages()
    print(f"Total pages: {total_pages}")