# Blogposts

This repository contains all the blogposts published in the 4geeksacademy.com blogs section: https://4geeksacademy.com/us/blog

Here we'll upload all the files with the content of each post that will be published in the blog.

## How to add a new post?

In order to add a new post to the website, you have to follow the next steps:

1. Fork this repository to create a copy but yours.

2. Create a markdown file (`.md` file extension) in the `blog` folder.

    + The name of the file should be a slug that only includes letters, numbers and `-`. Do not include spaces, uppercase letters or other characters. i.e.: `welcome-to-4geeks.md`.

    + If you want to publish a post in other language, add the language abreviation at the end of the name, right before the file extension. i.e.: This a post in spanish `bienvenido-a-4geeks.es.md`.

    + **Important:** Each post must include proper YAML frontmatter metadata. See `.cursor/rules/blog-metadata.mdc` for detailed guidelines.

3. Add your changes to your repository (`git add .`, `git commit -m "A message describing your contribution"` and `git push`).

4. Create a pull request in GitHub.

That's it! Then we'll review your changes and hopefully accept it soon!

## Metadata Requirements

All blog posts must include the following metadata in their YAML frontmatter:

```yaml
---
author: "4Geeks Academy"
cluster: "trends-and-tech"
excerpt: "A compelling 50-100 word summary (max 160 characters)"
status: "published"
tags: ["tag1", "tag2", "tag3"]
template: "landing_post"
title: "SEO-optimized title (5-10 words)"
---
```

For complete metadata guidelines, see `.cursor/rules/blog-metadata.mdc`.

Thanks for contributing to 4Geeks!
