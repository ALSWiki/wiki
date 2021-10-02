import json
import os
import re
import shutil
import sys
from contextlib import suppress
from operator import attrgetter
from pathlib import Path

from bs4 import BeautifulSoup
from common import article_name_to_file_name, filename_to_article_name, visit_files_in_dir
from markdown import markdown


YT_VID_URL = "https://www.youtube.com/watch?v="
YT_VID_ID = re.compile(r"\?v\=(.+)$")
YT_EMBED_IFRAME = """
<iframe width="1200" height="650" src="https://www.youtube.com/embed/{}"></iframe>
""".format


def center_images(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for p in map(attrgetter("parent"), soup.select("p > img")):
        p["align"] = "center"
    return str(soup)


def remove_tag(html: str, tag: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for el in soup.select(tag):
        el.replace_with("")
    return str(soup)


def embed_yt_videos(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for el in soup.select(f'a[href^="{YT_VID_URL}"]'):
        vid_id = re.search(YT_VID_ID, el["href"]).group(1)
        el.replace_with(BeautifulSoup(YT_EMBED_IFRAME(vid_id), "html.parser"))
    return str(soup)


def get_edit_link(article_title: str) -> str:
    article_param = Path(article_name_to_file_name(article_title)).stem
    return f"../../edit?article={article_param}"


def transform_markdown(md, article_title):
    article = remove_tag(embed_yt_videos(center_images(markdown(md, extensions=["extra"]))), "h1")
    edit_link = get_edit_link(article_title)
    return f"""
<!DOCTYPE html>
<html>
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width,initial-scale=1">
        <title>{article_title} - ALSWiki</title>
        <link rel="stylesheet" href="../../index.css" />
        <script defer src="../../index.js" type="module"></script>
    </head>

    <body>
        <main class="md">
            <div class="top-right">
                <div id="google_translate_element">
                    <button onClick="loadTranslationButton()">
                        Load Google Translate
                    </button>
                </div>
                <div class="edit-container">
                    <a href="{edit_link}"><button>Edit</button></a>
                </div>
                <div class="article-search">
                    <input type="text" placeholder="Search ALSWiki" />
                </div>
            </div>
            <div class="article">
                <h1>{article_title}</h1>
                {article}
            </div>
        <main>
    </body>
</html>
    """


def transform_file(in_file, out_file):
    with open(in_file, "r") as fin:
        md = fin.read()

    article_title = filename_to_article_name(in_file)

    with open(out_file, "w+") as fout:
        print(res := transform_markdown(md, article_title), file=fout)


def is_markdown(fp):
    return fp[-3:] == ".md"


def main():
    if len(sys.argv) > 2:
        transform_file(sys.argv[1], sys.argv[2])
        return

    with suppress(FileExistsError):
        os.mkdir("__dist__")

    articles = []

    rules = dict(
        dir_exclude=lambda dir_: dir_[:3] == "./." or dir_[:10] == "./__dist__",
        file_exclude=lambda fname: not is_markdown(fname),
    )

    @visit_files_in_dir(".", **rules)
    def _(dirname, filename):
        root_dir = Path("__dist__") / dirname
        root_dir.mkdir(exist_ok=True)
        in_ = Path(dirname) / filename
        out = (root_dir / filename).with_suffix(".html")
        transform_file(in_, out)
        articles.append(filename_to_article_name(filename))

    with open(Path("__dist__") / "articles.json", "w+") as fout:
        json.dump(articles, fout)


if __name__ == "__main__":
    main()
