import json
import re
import sys
from pathlib import Path
from typing import Set

from bs4 import BeautifulSoup
from textblob import TextBlob

from common import article_name_to_file_name, filename_to_article_name, visit_files_in_dir


index = dict()
files = dict()
useless_chars = re.compile(r"[=|-|–|“|”|.| ]+")
new_lines = re.compile(r"\n+")

def get_sentence_topics(sentence: str) -> Set[str]:
    blob = TextBlob(sentence)
    return {*blob.noun_phrases.lemmatize()}

def get_topics(text: str) -> Set[str]:
    topics = set()
    sentences = re.split(new_lines, text)
    [*map(topics.update, map(get_sentence_topics, sentences))]
    return {*filter(bool, map(remove_useless_chars, topics))}

def remove_useless_chars(text: str) -> str:
    return re.sub(useless_chars, " ", text) \
        .strip() \
        .replace(" ’ ", "'")

def main():
    rules = dict(
        dir_exclude=lambda dir_: dir_.count("/") < 2,
        file_exclude=lambda fname: fname[-5:] != ".html"
    )

    with open(Path("__dist__") / "articles.json", "r") as fin:
        for i, article_fp in enumerate(map(article_name_to_file_name, json.load(fin))):
            files[article_fp] = i

    @visit_files_in_dir("./__dist__", **rules)
    def _(dirname, filename):
        with open(Path(dirname) / filename, "r") as fin:
            text = BeautifulSoup(fin.read(), "html.parser").text

        num = files[filename]
        for topic in get_topics(text):
            index[topic] = index.get(topic, [])
            index[topic].append(num)

    [*map(list.sort, index.values())]
    with open(Path("__dist__") / "index.json", "w+") as fout:
        json.dump(index, fout)

    with open(Path("__dist__") / "files.json", "w+") as fout:
        json.dump(files, fout)

if __name__ == "__main__":
    main()
