tags = untei, documentation

[toc]

<!-- TODO:
- how to handle internal linkages
- function of copying css files and so on
- update template variables

-->
# Overview
In an entry of [How to use Untei](How to use Untei.html), you have learned how to write an article, and learned that in order to define the appearance and configuration a **theme** must be used.

When you processed one directory with `untei` command, the `theme` directory stored at the directory is referred to. The theme directory includes your website template information and programs you code to define how to configure special pages. This entry introduces how to put these information on theme directory.

# Structure

The following directory tree shows you the simplest form of a theme.

```
theme
├── site_config.txt
├── index.py
├── tag.py
└── template.html
```
You have to include these four files in your theme. In the following chapters, it will be shown how to create these files.

Though the list above does not show any image files or CSS files, this does not mean that you cannot use a CSS file and images. Any file and directory which is not listed on the list above will be copied to the output directory, maintaining the hierarchal structure.

The statement above might seem too abstract. So let's see an example:

```
.
├── sample_article1.md
├── sample_article2.md
└── theme
    ├── img
    │   └── icon.png
    ├── site_config.txt
    ├── tag.py
    ├── index.py
    ├── template.css
    └── template.html
```

This is an example directory to store your articles. Under the current directory `./`, you have two articles named `sample_article1.md` and `sample_article2.md`. Also, you put the `theme` directory there and it stores `img/icon.png` and `template.css` in addition to the least set of three files mentioned in the above tree diagram.


By executing at your output directory the command
```
untei .
```
your articles are processed and the produced HTML files will be generated.

The result of the command will be like
```
output
├── sample_article1.html
├── sample_article2.html
├── index.html
├── {{tag pages}}
├── img
│   └── icon.png
└── template.css
```
though tag pages will differ depending on the content of markdown files.

Now you have found what the above statement means. Two excessive files `img/icon.png` and `template.css` are copied to the directory, holding their original relative directory relations. As shown in this example, you can include any file and folder in your theme, whatever they are. This means you can include JS files, CSS files, image files and any other components you want to use.

Strictly speaking there is an exception of python files. Any python files with its extension `.py` are not copied, so you can import your python files other than `index.py` or `tag.py` without copying these python files.

# Site configuration with `site_config.txt`
Site config is a set of item and its value. At the file `theme/site_config.txt`, you can record the settings like

```
# The title of site
title  = Example Web Site
```
With a flag `# `, you can put comments inside the file.

Currently the following items can be defined.

## title
Example
```
# The title of site
title  = Example Web Site
```
This value `Example Web Site` will be the title of your website. This value can be accessed inside `theme/template.html` as a **template variable**, later explained.

## copyright
Example
```
# Copyright information
copyright = (c) Untei
```

If you want to create a template for articles with a copyright information, you can define the value here. The defined copyright statement can be accessed with a template variable, later explained.

# Create tag pages with `tag.py`
This file usage is a bit tricky.
The python file will be executed while creating a tag page, and the last value of `body` inside the file will be used as a content of the tag page. You can access some information through variables like `tag` and `latest_tagged_articles(int)`.

One simple example of `tag.py` is like this:
```python
body = "These are articles tagged as " + tag + " <br />\n<ul>"

for article in latest_tagged_articles(10):
    body = body + "<li>" + article.title + "</li>\n"
body = body + "</ul>"
```

Suppose that it is a tag page for "computer science" and you have two articles tagged as "computer science":
- an article titled as "Sorting algorithms"
- an article titled as "Deterministic finite automaton"

The tag page for `computer science` will be
```html
These are articles tagged as computer science <br />
<ul>
<li>Sorting algorithms</li>
<li>Deterministic finite automaton</li>
</ul>
```

## Tag
`tag` is a string-valued variable, that stores the tag name. Since this page is for tag "computer science", the value of `tag` is "computer science".


## Latest articles on the tag
`latest_tagged_articles(n)` is a method that returns a list of articles tagged as `tag` value. The argument `n` indicates the maximum number of articles to be stored at the list. Each article has several fields convenient to create tag pages effectively.


## Reference
There are several variables and methods that can be used on tag pages. For more information, you can visit [Untei reference](Untei reference.html)



# Define the page view : `template.html`

The file `template.html` is the base to define the appearance. `template.html` can be written in HTML, but also it can contain special words called _template variables_. These variables will be replaced with its value, which is predefined with files in the `theme` directory, or changed by untei.


This is one simplest example of template.html.
```
<html>
  <head>
    <title>{{site_config.title}}</title>
  </head>
  <body>
    <h1>{{site_config.title}}</h1>
    {{article.content}}
    <p>{{site_configcopyright}}
  </body>
</html>
```

`{{site_config.title}}`, `{{article.title}}`, `{{article.content}}` and `{{site_config.copyright}}` are template variables. As the name of variables shows, `{{site_config.title}}` is replaced with the name of your site defined on `theme/site_config.txt`, for example.


## site_config.title

The value is defined at `theme/site_config.txt` as
```
title = .....
```
## site_config.copyright
The value is defined at `theme/site_config.txt` as
```
copyright = .....
```
## article.title
The value is defined at each markdown to be processed. At the top of the file, you can put
```
title = .....
```
to define the title of the article. If you do not specify, then the file name without its extension will be used as `{{article.title}}`

## article.content
The value is the result of processing each article.


## An Example
sample_article.md
```
title = Introduction to Game Theory
Have you ever heard of an area in Mathematics called **game theory**? ....
```
template.html
```
This page is on {{article.title}}. If it is not what you want, go back to <a src='index.html'>TOP page</a><br />.
<hr>
{{article.content}}
```
Output: sample_article.html
```
This page is on Introduction to Game Theory. If it is not what you want, go back to <a src='index.html'>TOP page</a><br />.
<hr>
Have you ever heard of an area in Mathematics called <strong>game theory</strong>? ....
```
`{{article.title}}` is replaced with 'Introduction to Game Theory' and
`{{article.content}}` is replaced with the parse result of markdown.
