#!/usr/bin/env python3
import argparse
from datetime import datetime, date
from feedgen.feed import FeedGenerator
import frontmatter
import io
import os
from pathlib import Path
import subprocess
from sys import exit
import tempfile
import time
from typing import List

BUILD_DIR = "build"
CONTENT_DIR = "content"
BASE_URL = "https://andyls.co.uk"

class WebsitePage:
    def __init__(self, file_path):
        self.file_path = file_path
        self.frontmatter = frontmatter.load(self.file_path)
    
    def get_input_file_path(self):
        return self.file_path
    
    def get_output_file_path(self, build_dir_path) -> Path:
        return Path(
            os.path.join(
                build_dir_path,
                os.path.basename(self.file_path).replace(".md", ""),
                "index.html"))

    def get_title(self) -> str:
        return self.frontmatter["title"]

class BlogPost(WebsitePage):
    def __init__(self, file_path):
        super().__init__(file_path)
        # Update publicationDate on build if not published
        if "published" not in self.frontmatter or not self.frontmatter["published"]:
            self.frontmatter["publicationDate"] = date.today()
            self.frontmatter["published"] = False
            with open(file_path, 'w', encoding='utf8') as f:
                f.write(frontmatter.dumps(self.frontmatter))

    def get_output_file_path(self, build_dir_path) -> Path:
        return Path(
            os.path.join(
                build_dir_path,
                "blog",
                str(self.get_publication_date().year),
                os.path.basename(self.file_path).replace(".md", ""),
                "index.html"))
    
    def get_tags(self) -> List[str]:
        return self.frontmatter['tags'] if "tags" in self.frontmatter else []
    
    def get_publication_date(self) -> date:
        return self.frontmatter['publicationDate'] if "publicationDate" in self.frontmatter else date.today()


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

def get_website_url_from_file_path(file_path : Path, parent_path : Path) -> Path:
    return file_path.relative_to(parent_path)

def get_blog_pages_to_build():
    paths = []
    content_dir = os.path.join(os.getcwd(), CONTENT_DIR, "blog")
    for path, subdirs, files in os.walk(content_dir):
        for f in files:
            if not f.endswith(".md"):
                continue
            paths.append(
                os.path.relpath(
                    os.path.join(path, f), os.getcwd()))
    return paths


def get_pages_to_build():
    paths = []
    content_dir = os.path.join(os.getcwd(), CONTENT_DIR)
    for path, subdirs, files in os.walk(content_dir):
        for f in files:
            if os.path.basename(f) == "index.md":
                continue
            if not f.endswith(".md"):
                continue
            paths.append(
                os.path.relpath(
                    os.path.join(path, f), os.getcwd()))
    return paths

def generate_html_for(page, build_dir_path, template="template.html"):
    print(f"Building HTML for '{page.get_title()} ({page.get_input_file_path()})'")
    
    info = os.stat(page.get_input_file_path())
    publicationDate = ""
    if hasattr(page, "get_publication_date"):
        publicationDate = custom_strftime("%B {S}, %Y", datetime.strptime(str(page.get_publication_date()), "%Y-%m-%d"))
    modificationDate = custom_strftime("%B {S}, %Y", datetime.strptime(time.ctime(info.st_mtime), "%c"))

    # if hasattr(page, "get_publication_date"):
    #     p_date = page.get_publication_date()
    #     m_date = datetime.strptime(time.ctime(info.st_mtime), "%c").date()

    #     print(p_date)
    #     print(m_date)
    #     print( p_date > m_date )

    output_filename = page.get_output_file_path(build_dir_path)

    if not os.path.exists(output_filename.parent):
        os.makedirs(output_filename.parent)

    command = [
        "pandoc", "-f", "markdown+gfm_auto_identifiers", "-t", "html",
        "-s", "-o", str(output_filename),
        page.get_input_file_path(),
        F"--template={template}",
        "--lua-filter='filters/heading-anchor-links.lua'",
        f"-V publicationDate='{publicationDate}'"
    ]

    if hasattr(page, "get_publication_date"):
        p_date = page.get_publication_date()
        m_date = datetime.strptime(time.ctime(info.st_mtime), "%c").date()

        # print(p_date)
        # print(m_date)
        # print( p_date > m_date )
        print(m_date > p_date)
        if m_date > p_date:
            print("Adding modification date!")
            command.append(f"-V modificationDate='{modificationDate}'")

    full_cmd = " ".join(command)
    subprocess.check_output(full_cmd, shell=True)

def generate_rss(pages):
    fg = FeedGenerator()

    for page, fm in pages:
        fe = fg.add_entry()
        fe.id('http://lernfunk.de/media/654321/1')
        fe.title(fm['title'])
        fe.link(href="http://lernfunk.de/feed")

    fg.rss_str(pretty=True)
    fg.rss_file(f"{BUILD_DIR}/rss.xml")

def generate_page(content, output_file_path, template="template.html"):
    with tempfile.NamedTemporaryFile(suffix=".md") as tf:
        with open(tf.name, "w") as temp_file:
            temp_file.writelines(line + '\n' for line in content)

        command = ' '.join([
            "pandoc",
            "-f", "markdown+gfm_auto_identifiers", "-t", "html", tf.name,
            f"-o {output_file_path}",
            f"--template={template}",
            "--lua-filter='filters/heading-anchor-links.lua'",
            "--section-divs"
        ])
        subprocess.check_output(command, shell=True)


def generate_sitemap():
    pass


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

    all_blog_pages = get_blog_pages_to_build()
    print(all_blog_pages)


    if len(all_blog_pages) == 0:
        print("Could not find any blog posts to make. Exiting...")
        exit(1)

    print("Building blog and tag pages...")

    # Collect and parse information into relevant structures and models
    blog_posts = [BlogPost(post) for post in get_blog_pages_to_build()]
    five_recent_blog_posts = sorted(blog_posts, key = lambda x: x.get_publication_date())[-5:]
    publication_years = sorted(set([bp.get_publication_date().year for bp in blog_posts]))

    # Get all unique tags
    all_tags = [bp.get_tags() for bp in blog_posts]
    all_tag_set = set([tag for tag_list in all_tags for tag in tag_list])

    # Create mapping of each tag and blog posts that have that tag
    blog_posts_by_tag = {}
    for tag in all_tag_set:
        blog_posts_by_tag.update({tag: [bp for bp in blog_posts if tag in bp.get_tags()]})

    # Build blog posts
    for blog_post in blog_posts:
        # Creates blog/, blog/{year}, and blog/{year}/{post} for each blog post
        os.makedirs(blog_post.get_output_file_path(build_dir_path).parent, exist_ok=True)

        # build blog/{year}/{post}
        generate_html_for(blog_post, build_dir_path, template="template-blog-post.html")

    for publication_year in publication_years:
        # create blog/{year}/index.html
        blog_year_content = [
            "---",
            f"title: Blog Posts from {publication_year}",
            "---"
        ]
        blog_posts_in_year = [bp for bp in blog_posts if bp.get_publication_date().year == publication_year]
        for blog_post in sorted(blog_posts_in_year, key = lambda x: x.get_publication_date()):
            post_url = get_website_url_from_file_path(
                blog_post.get_output_file_path(build_dir_path).parent,
                build_dir_path)
            # print(str(post_url))
            blog_year_content.append(f"- {blog_post.get_publication_date()}: [{blog_post.get_title()}](/{post_url})")

        blog_year_build_path = os.path.join(build_dir_path, "blog", str(publication_year), "index.html")
        generate_page(blog_year_content, blog_year_build_path)
    
    # Build blog/index.html
    blog_index_content = [
        "---",
        f"title: All Posts",
        f"preamble: |",
        f"    Everything that I have written. [All tags](/tags).",
        "---"
    ]
    
    blog_index_content.append("## Explore Topics I've Written About{#blog-tags}")
    tag_block = "<ul class='tags'>"
    for tag in sorted(list(all_tag_set)):
        blog_post_count = len(blog_posts_by_tag[tag])
        post_url = f"/tags/{tag}"
        tag_block += f"<li class='tag'><a href='{post_url}'>{tag} ({blog_post_count})</a></li>"
    tag_block += "</ul>"
    blog_index_content.append(tag_block)

    blog_index_content.append(f"## Explore Posts by Year{{#posts-by-year}}")
    for publication_year in publication_years:
        blog_index_content.append(f"### [{publication_year}](/blog/{publication_year})")
        # for blog_post in year..
        blog_posts_in_year = [bp for bp in blog_posts if bp.get_publication_date().year == publication_year]
        for blog_post in sorted(blog_posts_in_year, key = lambda x: x.get_publication_date()):
            post_url = get_website_url_from_file_path(
                blog_post.get_output_file_path(build_dir_path).parent,
                build_dir_path)
            print(str(post_url))
            blog_index_content.append(f"- {blog_post.get_publication_date()}: [{blog_post.get_title()}](/{post_url})")
        blog_index_content.append("\n")

    # blog_index_content.append(f"## Explore Posts by Tag{{#posts-by-tag}}\n")
    # for tag in sorted(list(all_tag_set)):
    #     blog_posts_with_tag = blog_posts_by_tag[tag]
    #     print(tag, blog_posts_with_tag)
    #     blog_index_content.append(f"### [{tag}](/tags/{tag})\n")
    #     for blog_post in sorted(blog_posts_with_tag, key = lambda x: x.get_publication_date()):
    #         post_url = get_website_url_from_file_path(
    #             blog_post.get_output_file_path(build_dir_path).parent,
    #             build_dir_path)
    #         blog_index_content.append(f"- {blog_post.get_publication_date()}: [{blog_post.get_title()}](/{post_url})")
    #     blog_index_content.append("\n")


    blog_index_build_path = os.path.join(build_dir_path, "blog", "index.html")
    generate_page(blog_index_content, blog_index_build_path)

    # Build tag pages
    print("Generating pages for tags:", ", ".join(all_tag_set))
    for tag in all_tag_set:
        # Creates tags/ and tags/{tag} for each recognised tag
        tag_build_path = Path(
            os.path.join(
                build_dir_path, 
                "tags", str(tag).lower().replace(" ", "-"), "index.html"))
        os.makedirs(tag_build_path.parent, exist_ok=True)

        # create tags/{tag}/index.html
        tag_page_content = [
            "---",
            f"title: Posts Tagged with '{tag}'",
            "---"
        ]
        blog_posts_with_tag = [bp for bp in blog_posts if tag in bp.get_tags()]
        for blog_post in sorted(blog_posts_with_tag, key = lambda x: x.get_publication_date()):
            post_url = get_website_url_from_file_path(
                blog_post.get_output_file_path(build_dir_path).parent,
                build_dir_path)
            # print(str(post_url))
            tag_page_content.append(f"- {blog_post.get_publication_date()}: [{blog_post.get_title()}](/{post_url}/)")

        generate_page(tag_page_content, tag_build_path)

    # create tags/index.html
    tags_index_content = [
        "---",
        "title: Tags",
        "---"
    ]
    for tag in sorted(list(all_tag_set)):
        blog_posts_with_tag = [bp for bp in blog_posts if tag in bp.get_tags()]
        post_url = "/".join(["tags", str(tag)])
        tags_index_content.append(f"- [{tag}](/{post_url}/) ({len(blog_posts_with_tag)})")

    tags_index_build_path = os.path.join(build_dir_path, "tags", "index.html")
    generate_page(tags_index_content, tags_index_build_path)

    # Build top-most level non-index pages
    for p in get_pages_to_build():
        generate_html_for(WebsitePage(p), build_dir_path)

    # Build index page
    with open("content/index.md", "r") as index_file:
        index_page = index_file.readlines()
        with tempfile.NamedTemporaryFile(suffix=".md") as tf:
            with open(tf.name, "w") as temp_file:
                temp_file.writelines(line for line in index_page)
                for recent_bp in five_recent_blog_posts:
                    post_url = get_website_url_from_file_path(
                        recent_bp.get_output_file_path(build_dir_path).parent,
                        build_dir_path)
                    temp_file.write(f"- {recent_bp.get_publication_date()} [{recent_bp.get_title()}](/{post_url}/)\n")

            command = [
                "pandoc",
                "-f", "markdown+gfm_auto_identifiers", "-t", "html", tf.name,
                f"-o {BUILD_DIR}/index.html",
                "--template=template.html",
                "--lua-filter='filters/heading-anchor-links.lua'"
            ]
            
            subprocess.check_output(' '.join(command), shell=True)
