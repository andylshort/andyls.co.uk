#!/usr/bin/env python3
import datetime
import frontmatter
import glob

def update_post(path):
    with open(file, "r") as f:
        fm = frontmatter.load(f)
        edited = False

        dt = datetime.datetime.now()
        print(dt.strftime("%Y-%m-%dT%H:%M:%SZ"))
        if fm.get('draft') == True:
            print("draft")
            fm["date"] = dt.strftime("%Y-%m-%dT%H:%M:%SZ")
            edited = True
        
        f.close()
        
        if edited:
            with open(file, "wb") as new_file:
                frontmatter.dump(fm, new_file)


def main():
    for path in glob.glob("content/posts/*.md"):
        update_post(path)

if __name__ == "__main__":
    main()
