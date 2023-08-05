# Overview
Untei is a static site generator, which enables you ...
- to configure your own blog-website only with markdown documents, and
- to enrich your theme as if you code in python.

# Documents
## How to use Untei
- [English](How to use Untei.html)
- [日本語](Unteiの使い方.html)

## How to use Untei
- [English](How to create a theme.html)
- [日本語](ブログテーマの作り方.html)


# Quick start
## Installation
If you are familiar with python3, it is easy to install
```
pip3 install untei
```

Now you got ready to start!

## Your first web page
Untei provides a _quick start_ mode, to set up a theme and site configuration information.

Go to your empty directory, and execute
```
untei init
```

It will make several questions on your site. Answering these questions, least necessary files will be created on the directory.

Questions are:

- your site title
- your name
- your favorite color (used as header color)
- whether you need a sample article


If you answer 'yes' to both questions of whether you need a sample article, and whether you want to create an output directory right now, you can immediately try untei's functionality.

```
untei .
```

By executing this command, you will find a file named as `index.html` generated in `/output`. Open it with any browser to confirm the result.

# Programming your theme
You can create your own theme by coding python.

For example, the code below is the simplest example of how to code an article page.

```
body = "Articles tagged as " + tag + "<br />\n\n"
for article in latest_tagged_articles(2):
    body = body + "Page Title: <a href='" + article.path + "'>" + article.title + "</a><br />\n\n"
```

This page lists the latest two articles tagged. The last value of `body` will be used as the content of the page for the tag.

An example output from this code can be

```
Articles tagged as Untei document<br />

Page Title: <a href='How to use Untei.html'>How to use untei</a><br />

Page Title: <a href='How to create a theme.html'>How to create a theme</a><br />


```

if there are the two articles in the tag of "Untei document".

# Status
Currently the project is in beta. I really appreciate if you try Untei and give me feedback. Thank you.

# License
MIT
