title = How to use Untei
tags = untei, documentation
date = 2018-01-01

[toc]

# Overview

Untei is a programable static site generator. By using untei, you can easily arrange documents to be published on the Internet.

Simply put, untei provides following functions:

- You can easily create a blog-like website with markdown documents
- You can configure settings on top page and tag pages as if you are programming

Bad news for you, currently the only available programming language is python3. In the future, other language options will be available.
## Name origin
This application is named after the first open library in Japan. As the original library Untei(芸亭), I hope your great idea can be easily open and shared through this application.



# Quick start
## Setup Untei
If you are familiar with python3, it is easy to install
```
pip3 install untei
```

Now you got ready to start!
## Try Untei
For beginners untei provides a _quick start_ option, to set up a theme and site configuration information.

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


... Sorry for the developer's poor sense in designing web templates. But he is pretty sure that you can at least confirm that the theme includes your favorite color.

Even if you are dissatisfied with the template, this is never enough reason to quit using Untei. You can also ask for themes designed by other talented designers. Of course your can configure your theme. Please visit [How to create a theme]("How to create a theme.html").



If you have used Untei and you have a theme other than the default theme, then this initialization step is not mandatory. In that case, you can construct your directory by yourself by following How to execute and [How to create a theme]("How to create a theme.html).

# How to execute untei

```
untei your/document/directory
```

The directroy structure must be

```
your/document/directory
├── { articles }
├── { other files you need }
└── theme
    └── {Detail will be explained in another article}
```
As you can see, your articles will be stored right under the directory. If you have things you want to include, put them there as well. These files include picture files used in your web site. Though this document


An example directory structure is
```
Documentation
├── "How to use untei.md"
├── "How to create a theme.md"
└── theme
    └── ....
```


```
untei your/document/directory
```

At least the following files will be generated in the current directory.
```
.
├── "How to use untei.html"
└── "How to create a theme.html"
```

In addition to the files on the diagram, files like `template.css`, `index.html` and pages for tags will be added. For more details, please refer to each page or chapter.

<!--
If you want to specify a directory to store output files, then you can use `-o` option like
```
untei your/document/directory -o output
```

If you do not specify the name, then the output directory is set as the current directory.-->

# Articles
As mentioned in How to execute untei, your articles must be put right under the directory. You can write articles in either markdown or HTML. You can choose different formats for different articles.

## Markdown
You can write articles in a _markdown_ format. Articles written with markdown must have `.md` extension. If you are not familiar with markdown, then you are recommended to read [untei markdown page](Syntax of Sangaku.html) later.

These will be processed with markdown parser and generate an HTML file that reflects its content. The applied templated is `theme/template.html`.

Honestly speaking, the format used in untei is a bit different from plain markdown. Differences can be classified into two groups - settings of the article, and extended markdown -.



First of the two, you can specify article settings.
Article settings must be put at the top of the article. If a body part of the article begins, then you cannot set any value. An example is the right page here.
```
title = How to use Untei
tags = untei, documentation
date = 2018-01-01

# Overview
Untei is a programable static site generator. .....
```
Here settings on `title`, `tags`, and `date` are set. As the example shows one line has one setting and once body part `# Overview ....` begins, there is no setting.

### Title

```
title = How to use Untei
```
You can include spaces in the article title.
If you do not include `title = ...` on the document, the article title will be the file name without its extension.

### Tags
```
tags = untei, documentation
```
In this example, two tags `untei` and `documentation` are set on the article.
As you can see, you can specify several tags for one article. In that case tags must be split with `, `. That is why you cannot create any tag that includes `, `, the divisor. Though, you can use spaces for tag names.

### Date
```
date = 2018-01-01
```
This will be interpreted as January 1st, 2018. The format of date must follow `YYYY-MM-DD`.


### Status
You can the phase of writing an article.
Currently `draft` and `ready` are available. The default value is ready.

If you specify the status `draft`, then the article is not processed and no HTML file is generated for this markdown file. In addition, tag pages and the index page are not affected with the markdown.
```
status = draft
```

If you specify the status `ready`, then the article will be processed as planned. Since the default value is `ready`, this status option only provides an explicit way of stating the status.
```
status = ready
```


<br />
<br />
Secondly, it includes some extensions for mathematical expressions. For more details you can see [Sangaku](Syntax of Sangaku.html)

<!--
## HTML
You can write articles in HTML format, for more expression power or for utilizing your past HTML assets. A template `theme/template.html` will be applied. -->

# Theme
Until this part, you learned how to create a document. But, it is not enough for a beautiful website. You will need a **theme** to define the style and appearance of each article in the site.

Detailed explanation is given at [How to create a theme](How to create a theme.html), and on this page instruction is limited to an overall picture.


The configuration of theme is stored at the `theme` directory on the document page. The directory stores a wide range of information like:

- site title (on site_config.txt)
- copyright information (on site_config.txt)
- template
- how to configure tag and index page

If you want to change the title of your website, then open `theme/site_config.txt` and edit it. An example content of `site_config.txt` is
```
title = Untei documentation
copyright = (c) Untei
```

If you can modify the configuration of the top page or tag pages, you can edit `index.py` and `tag.py` respectively. The output of the source code will be exactly what is displayed. Untei provides several useful functions and variables to configure these pages. For more details visit [How to create a theme](How to create a theme.html).

# Lastly
Thank you for your reading and trying untei. I hope you have a wonderful writing experience.
