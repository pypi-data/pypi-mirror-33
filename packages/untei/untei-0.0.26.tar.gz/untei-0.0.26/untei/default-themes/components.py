def create_short_article_box(article):
    temp = """
    <div class='common_box article_box'>
        <h2 class='article_box_article_title'>
            <a href='{{link}}'>{{article.title}}</a>
        </h2>

        <span class='article_box_tag'>{{tag_list}}</span><br />
        <!--<p class='article_box_body'>{{article.description}}</p>-->
        <div class='article_box_button_read'>
            <a href='{{link}}'>⇨ READ</a>
        </div>
    </div>
    """

    tags = ""

    for tag in article.get_property('tags'):
        tags = tags + "<a href='" + tag + ".html'>" + tag + "</a>  "

    box = temp.replace("{{link}}", article.get_property('title'))\
            .replace("{{article.title}}", article.get_property('title'))\
            .replace("{{tag_list}}", tags)\
            .replace("{{article.description}}", article.get_property('description'))
    return box
