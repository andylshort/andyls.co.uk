#!/usr/local/bin/python3
import argparse
from datetime import datetime, date
import frontmatter
import os
from pathlib import Path
import shutil
import subprocess
import yaml

def create_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build-drafts", action="store_true", dest="drafts")
    return parser

def post_sorter(p):
    return p["publicationDate"]

def build_metadata(drafts):
    data = {}
    data["posts"] = []
    for file in os.listdir("blog"):
        p = f"blog/{file}"
        pa = Path(p)
        with open(p, "r") as f:
            meta = frontmatter.load(f)
            print(meta.keys())
            if "title" in meta:
                print(meta["title"])
            meta["filePath"] = p
            meta["url"] = str(pa.with_suffix(".html"))
            if drafts:
                data["posts"].append(meta.metadata)
            else:
                if "draft" not in meta or not meta["draft"]:
                    data["posts"].append(meta.metadata)
            if "publicationDate" not in meta:
                meta["publicationDate"] = date.today()
    
    data["posts"].sort(key=post_sorter, reverse=True)

    for p in data["posts"]:
        p["publicationDate"] = p["publicationDate"].strftime("%B %d, %Y")

    with open("metadata.yaml", "w+") as w:
        yaml.dump(data, w)

    return data

def build_index():
    args = ["pandoc", "-s",
        "-f", "markdown-markdown_in_html_blocks+raw_html", "-t", "html", "index.md",
        "--highlight-style=tango",
        "-o", "public/index.html",
        "-B", "nav.html",
        "--metadata-file=metadata.yaml",
        "--template=template-index.html"]
    
    r = subprocess.call(args)

def build_pages(metadata):
    for post in metadata["posts"]:
        print(post["filePath"])

        path = Path(post["filePath"])

        date = post["publicationDate"]
        url = post["url"]

        args = ["pandoc", "-s",
           "-f", "markdown", "-t", "html", str(path),
           "-o", f"public/blog/{path.stem}.html",
           "-B", "nav.html",
           "-V", f"publicationDate:{date}",
           "-V", f"url:{url}",
           "--template=template-post.html"]

        print(args)
        
        r = subprocess.call(args)

def main(args):
    shutil.rmtree("public")
    os.mkdir("public")
    os.mkdir("public/blog")

    metadata = build_metadata(args.drafts)
    build_index()
    build_pages(metadata)
    

    # ps = Path(".").glob("blog/*.md")
    # blog_posts = [f for f in ps if f.is_file()]


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()
    main(args)
