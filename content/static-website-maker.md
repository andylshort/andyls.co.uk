---
title: "Quintessential Static Website Generator Blogpost!"
tags: ["project", "website", "pandoc"]
pubDate: "2022/07/06"
---
There comes a time and a place where a budding young developer will want to carve out their own small slice of the internet to call their own. Fed up of writing their own HTML, CSS, and JavaScript by hand, they will look at the myriad options for generating them automatically - Jekyll, Hugo, Gatsby - and ultimately say to themselves, "I will just make my own; _how hard can it be?_"

Today, that developer is me.

Personal websites are inherently _personal_. They should be a reflection of you as a person, your interests, quirks. It also acts as a nice technical showcase of what you can do, so show off!

I have no need for a dynamic website with all kinds of lazily-loaded fonts, scripts, analytics, bells, or whistles. In my opinion, most websites today don't need half of what they need, and take substantial liberties with their visitors' bandwidth and provide a lacklustre experience. That's a blog post for another time. To that end, I looked at all of the available static website generators available. An earlier incarnation of this website actually used [Hugo](https://gohugo.io/) as it (initially) seemed like the simplest to use and allowed me to get something up and running quickly. If there's one like I like, it's expediency of results!

One metric I like to evaluate software by is how easy it is to pick it back up after some time spent not using it. Hugo failed this. The workflow was not intuitive without revisiting documentation. There were more external dependencies than I wanted providing a lot of functionality that I wouldn't actually use. Theming was the final point of contention. Making small tweaks to an existing theme or wanting to add a few styles to the vanilla black and white involves creating an entire theme, and the project structure starts ballooning like Violet Beauregarde...

[Pandoc](https://pandoc.org/) is a tool I had previously used to generate some PDF files and had kept on my sytem as it was a useful utility. Several other people have articles detailing how they used it to generate HTML from Markdown for their own websites, so I decided to explore its documentation and give it a try. It definitely checked my boxes in terms of what I wanted a website generator to do: it's easy to script; has templating functionality for consistency and code reuse; extensibility; and great documentation.  It's easy to revisit too as the simplest invocation is `pandoc from_file to_file`! Any additional complexity is solely my responsibility to refine in whatever scripts and interfaces I make.

The build process is fairly simple: a `Makefile` that calls a Python script that calls `pandoc` repeatedly. I maintain a `content/` directory that I can symlink into with all of my writing. The python script enumerates all of the Markdown content and calls `pandoc` on each file, generating the respective HTMl using a simple template. The current incarnation of the website is a one-page design, so the content template is just a fancy `<article>` tag that gets various pieces of content and metadata filled in by Pandoc.

All of the individual pieces of content are concatenated together in date order, and included in one final Pandoc call to generate the index.html page, using a larger template, via:

```python
subprocess.run(["pandoc",
    "--from=markdown", "index.md",
    f"-o {BUILD_DIR}/index.html",
    "--template=template-index.html",
    f"-V my_content='{content}'", shell=True])
```

Inside the build directory is now a flat list of a handful of files that just need uploading to my web hosting provider. Having a minimalistic website and consolidated set of files to handle are two important things for me, and this achieves that. There are rough edges, and the design of the website might change, but for now, I'm happy with it.



[Here is a link to the project on GitHub.](https://github.com/andylshort/andyls.co.uk)