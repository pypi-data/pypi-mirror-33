import sys
import os
from untei import site_config
from untei import article
from untei import utils
from distutils import dir_util
import shutil
from untei.constants import Const

def main():
    args = sys.argv
    if args[1] == "init":

        quick_start()

        sys.exit()

    # obtain the list of all files in the directory and its child directories, besides essential files like config
    # It seems better to create another directory for config and templates
    files = utils.handled_files()

    # read a config file
    config = site_config.SiteConfig(Const.SITE_CONFIG_PATH)

    config.add_articles(files)

    for a in config.all_articles():
        a.save_to(config.output_path, config)

    # config.configure_all()
    config.create_tag_pages()

    config.create_index_page()

    # move config files
    config.copy_theme_files()

def quick_start():
    # site_title
    print("What is your web site name?\n >  ", end='')
    site_title = input()

    # copyright information
    print("What is your name?\n >  ", end='')
    author = input()

    # theme color
    print("What is your favorite color? Choose one out of ...")
    print("RED GREEN BLUE YELLOW BLACK GRAY or any CSS color codes.")
    print("or, you can skip this question, by typing 'pass'\n >  ", end='')
    color = input()
    if color in ["skip", "pass"]:
        color = "#9999CC"

    while True:
        print("Do you need sample articles?  [yes/no]\n >  ", end='')
        sample_article = utils.user_input_yes_or_no(input())
        if not(sample_article == None):
            break
        else:
            print("Only 'yes' and 'no' are accepted, sorry.")

    if not os.path.exists("./theme"):
        os.mkdir("./theme")
    copy_from = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/untei/default-themes"
    dir_util.copy_tree(copy_from, "./theme")

    with open("./theme/site_config.txt", "w") as f:
        body = Const.SITE_CONFIG_KEY_TITLE + " = " + site_title + "\n"
        body += Const.SITE_CONFIG_KEY_COPYRIGHT + " = (c) " + author
        f.write(body)

    with open("./theme/template.css", "r+") as f:
        f.write(f.read().replace("{{favorite_color}}", color))

    if sample_article:
        document = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/untei/documentation/"
        shutil.copy2(document + "How to use Untei.md", "./" + "How to use Untei.md")
        shutil.copy2(document + "How to create a theme.md", "./" + "How to create a theme.md")
        shutil.copy2(document + "How to create a theme.md", "./" + "Sangaku.md")
        shutil.copy2(document + "How to create a theme.md", "./" + "Untei reference.md")

    if not os.path.exists("./output"):
        os.mkdir("./output")
    print("Your project is successfully created!")




if __name__ == "__main__":
    main()
