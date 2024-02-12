import re
from pathlib import Path

from kwiq.core.flow import Flow
from kwiq.iterator.json_iterator import JsonIterator
from kwiq.db.sqlite import DB as SqliteDB

CLEAN_STRING_PATTERNS = [
    r'^--[\s]*(.*)$',
    r'^-[\s]*(.*)$',
    r'^[\s]*[*][\s]*(.*)$',
    r'^[0-9]+[.:][\s]*(.*)$',
    r"^'(.*)'$",
    r'^"(.*)"$',
    r'^`(.*)`$',
    r'^/\*[\s]*(.*)\*/$',
    r'^#[\s]*(.*)$',
    r'^///[\s]*(.*)$',
    r'^//[\s]*(.*)$',
]


class BuildTranslationCache(Flow):
    name: str = "build-translation-cache"

    def fn(self, translation_file: Path, db_path: Path) -> None:
        """
        Builds translation cache from json file
        """
        command = SqliteDB(db_path=db_path)
        command.command(sql='''
            CREATE TABLE IF NOT EXISTS translations (
                original_text TEXT NOT NULL,
                translated_text TEXT NOT NULL,
                PRIMARY KEY (original_text)
            )
            ''')

        for data in JsonIterator(file_path=translation_file, json_path="[*]"):
            original_text = clean_strings(data['original_text'])
            translated_text = clean_strings(data['translated_text'])
            command.command(sql='''
            INSERT INTO translations (original_text, translated_text)
            VALUES (?, ?)
            ON CONFLICT(original_text) DO UPDATE SET
            translated_text = excluded.translated_text
            ''',
                            parameters=(original_text, translated_text))


def clean_strings(text: str) -> str:
    for pattern in CLEAN_STRING_PATTERNS:
        match = re.search(pattern, text, re.DOTALL)
        if match:
            text = match.group(1)

    return text.strip()
