import os
from dataclasses import dataclass

@dataclass
class Config:
    BOT_TOKEN: str = "8404360124:AAHZ9FLMVQu_hWtylLL853KX1l-NOV4aLYI"
    ITPROGER_URL: str = "https://itproger.com/news"
    ARTICLES_PER_PAGE: int = 10

# Конфиг для парсера
PARSER_CONFIG = {
    'base_url': 'https://itproger.com/news',
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'articles_per_page': 10
}
