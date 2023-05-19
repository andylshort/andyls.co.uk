#!/usr/bin/env python3
import argparse
from datetime import datetime as dt
from feedgen.feed import FeedGenerator
import frontmatter
from pathlib import Path
import os
import subprocess
from sys import exit
import time

BUILD_DIR = "build"
BASE_URL = "https://andyls.co.uk"

# From: https://stackoverflow.com/a/5891598/9552003
def suffix(d):
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')

def custom_strftime(format, t):
    return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))

def create_parser():
    parser = argparse.ArgumentParser(
        description="Andy's custom static website generator",
        allow_abbrev=False
    )

    parser.add_argument('-B',
                       "--build-dir",
                       dest='build_dir',
                       type=str,
                       help='the path to the build directory')
    
    parser.add_argument("--test", required=False, action="store_true")

    return parser

def get_pages_to_build():
    paths = []
    content_dir = os.path.join(os.getcwd(), "content")
    for path, subdirs, files in os.walk(content_dir):
        for f in files:
            paths.append(
                os.path.relpath(
                    os.path.join(path, f), os.getcwd()))
    
    to_build = [(path, frontmatter.load(path)) for path in paths]

    to_build.sort(key=lambda x: x[1]["pubDate"], reverse=True)

    return to_build

def load_content(paths):
    content = []
    for path in paths:
        fm = frontmatter.load(path)
        # with open(path, mode="r") as f:
    return content

def generate_html_for(page, index):
    info = os.stat(page)
    post_time = custom_strftime("%B {S}, %Y", dt.strptime(time.ctime(info.st_ctime), "%c"))
    command = [
        "pandoc", page,
        "--template=template.html",
        f"-V post_date='{post_time}'",
        f"-V post_index={index}"
    ]
    full_cmd = " ".join(command)
    result = subprocess.check_output(full_cmd, shell=True)
    s = result.decode('utf-8')

    fm = frontmatter.load(page)
    tag_list = " ".join(fm['tags'])
    placeholder = "{{post_tags}}"
    s = s.replace(placeholder, tag_list)
    return s

def generate_rss(pages):
    fg = FeedGenerator()

    for page, fm in pages:
        fe = fg.add_entry()
        fe.id('http://lernfunk.de/media/654321/1')
        fe.title(fm['title'])
        fe.link(href="http://lernfunk.de/feed")

    fg.rss_str(pretty=True)
    fg.rss_file(f"{BUILD_DIR}/rss.xml")

if __name__ == "__main__":
    parser = create_parser()
    parsed_args = parser.parse_args()

    if parsed_args.test:
        get_pages_to_build()
        exit(0)

    if parsed_args.build_dir:
        BUILD_DIR = parsed_args.build_dir
        print("build directory:", BUILD_DIR)

    build_dir_path = os.path.join(os.getcwd(), BUILD_DIR)
    if not os.path.exists(build_dir_path):
        os.mkdir(build_dir_path)
    
    content = []
    for i, (p, fm) in enumerate(get_pages_to_build()):
        content.append(generate_html_for(p, i))
    content = '\n'.join(content)

    command = ' '.join([
        "pandoc",
        "--from=markdown", "index.md",
        f"-o {BUILD_DIR}/index.html",
        "--template=template-index.html",
        f"-V my_content='{content}'"
    ])
    subprocess.check_output(command, shell=True)