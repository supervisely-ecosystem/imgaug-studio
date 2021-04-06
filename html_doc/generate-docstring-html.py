import os
import shutil
from bs4 import BeautifulSoup
import supervisely_lib as sly

def pretty_py_html(text, output, html_name="index"):
    # Sphinx conf.py
    conf = """import os
import sys

sys.path.insert(0, os.path.abspath("my_file"))

project = "Python"
copyright = ""
author = ""
extensions = ["sphinx.ext.autodoc", "sphinx_copybutton"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
templates_path = ["_templates"]

html_show_sourcelink = False

html_theme = "sphinx_rtd_theme"
html_theme_options = {
    'analytics_anonymize_ip': True,
    'logo_only': True,
    'display_version': False,
    'prev_next_buttons_location': 'None',
    'style_external_links': False,
    'vcs_pageview_mode': '',
    'style_nav_header_background': 'white',
    'collapse_navigation': True,
    'sticky_navigation': False,
    'navigation_depth': 0,
    'includehidden': False,
    'titles_only': True
}

"""
    with open("conf.py", "w") as config:
        config.write(conf)

    # Text variable
    os.mkdir("my_file")
    with open("my_file/my_script.py", "w") as my_script:
        my_script.write(text)

    # rst
    rst_conf = """modules
=======

.. toctree::
   :maxdepth: 4

   modules
     """
    with open("index.rst", "w") as rst:
        rst.write(rst_conf)

    # File structure and cleaning
    os.system("sphinx-apidoc -o .  my_file")
    os.system("sphinx-build -b html . _build")

    os.remove("index.rst")
    os.remove("modules.rst")
    os.remove("my_script.rst")
    os.remove("conf.py")

    kit_dir = "html_kit"
    os.mkdir(kit_dir)

    shutil.move("_build/my_script.html", os.path.join(kit_dir, html_name + ".html"))
    shutil.move("_build/_static", os.path.join(kit_dir, "_static"))

    shutil.rmtree('my_file', ignore_errors=True)
    shutil.rmtree('_build', ignore_errors=True)

    # HTML Edits
    with open(os.path.join(kit_dir, html_name + ".html")) as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, 'html.parser')
    dd = soup.find('dd')

    if dd is None:
        raise Exception('Not found')

    dd.find('p').decompose()  # remove Bases: object

    head_t = soup.find('head')

    css = soup.new_tag('style')

    css.string = """
       ul.simple li {
         list-style: disc;
         margin-left: 24px;
       }
     """

    head_t.append(css)

    body_t = soup.find('body')

    body_t.clear()
    body_t['class'] = ''

    container = soup.new_tag('div', attrs={
        #"class": "rst-content section wy-nav-content",
        #"style": "margin: 0 auto; border-radius: 8px; box-shadow: 0 0px 24px 0 rgb(0 0 0 / 6%), 0 1px 0px 0 rgb(0 0 0 / 2%);",
    })

    container.append(dd)

    wrapper = soup.new_tag('div', attrs={
        #"style": "padding: 30px;"
    })
    wrapper.append(container)

    body_t.append(wrapper)

    with open(os.path.join(kit_dir, html_name + ".html"), "w") as file:
        file.write(str(soup))

    # Cleaning unnecessary files
    for file in os.listdir(os.path.join(kit_dir, "_static")):
        file_path = os.path.join("_static", file)
        req_files = ["clipboard.min.js", "copy-button.svg", "documentation_options.js", "copybutton.js",
                     "copybutton.css", "copybutton_funcs.js", "pygments.css"]
        if os.path.isfile(file_path) and file not in req_files:
            os.remove(file_path)

    # Move to Output folder
    for src_dir, dirs, files in os.walk(kit_dir):
        dst_dir = src_dir.replace(kit_dir, output, 1)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dst_file = os.path.join(dst_dir, file_)
            if os.path.exists(dst_file):
                if os.path.samefile(src_file, dst_file):
                    continue
                os.remove(dst_file)
            shutil.move(src_file, dst_dir)
    shutil.rmtree(kit_dir)


py_code = '''
class InsertDocString:"""
{}
"""
'''

#exit(0) #

html_dir = "../html_kit"
sly.fs.mkdir(html_dir)
sly.fs.clean_dir(html_dir)
sly.fs.remove_dir("my_file")

from src.allowed_augs import augs_modules

for module_name, methods in augs_modules.items():
    for method in methods:
        docstr = py_code.format(method.__doc__)
        pretty_py_html(docstr, "../html_kit", html_name=f"{module_name.lower()}.{method.__name__.lower()}")