from . import decorator
from . import filehandlers
from . import configuration 
from . import articles
from . import preprocessor
from bottle import default_app, route, run, template, static_file, request, auth_basic
import jinja2
import os
import markdown
import logging
from string import Template
import difflib

def create_sample():
    sample_template = '''<!DOCTYPE html>
<html lang="en">

<head>
  <title>{{title}} {% if subtitle %} - {% endif %} {{subtitle}}</title>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="">
    <meta name="author" content="">
    <link href="/css/styles.css" rel="stylesheet" type="text/css"></link>
</head>

<body>
    {% block content_block %}
    <div class="content">{{content}}</div>
    {% endblock %}
</body>
</html>'''

    sample_template_2 = '''{% extends "article.html" %}
{% block content_block %}
    <div class="content2"><i>{{content}}</i></div>
{% endblock %}'''

    sample_article = '''main: true
type: article-type-one
permalink: post1.html
publish: true
---
### Welcome to Feni static site generator : Article 1'''

    sample_article_2 = '''main: true
type: article-type-two
permalink: post2.html
publish: true
---
### Welcome to Feni static site generator : Article 2'''

    sample_config = '''
source: articles
decorator: decorator
output: site
template: templates'''

    sample_templates_config = '''
    article.html:
      types:
        - article-type-one
    article2.html:
      types:
        - article-type-two'''

    sample_css = '''
content { color: black } 
content2 { color: gray; }'''

    os.makedirs("articles")
    os.makedirs("decorator/img")
    os.makedirs("decorator/css")
    os.makedirs("templates")
    with open("templates/article.html", "w") as a:
        a.write(sample_template)

    with open("templates/article2.html", "w") as a:
        a.write(sample_template_2)

    with open("articles/article.md", "w") as a:
        a.write(sample_article)

    with open("articles/article2.md", "w") as a:
        a.write(sample_article_2)

    with open("feni.yaml", "w") as a:
        a.write(sample_config)

    with open("templates/templates.yaml", "w") as a:
        a.write(sample_templates_config)


def make_sure_dir_exists(folder_path):
    dir = os.path.dirname(folder_path)
    if not os.path.exists(dir):
        logging.info("Creating directory: %s", dir)
        try:
            os.makedirs(dir)
        except:
            logging.warning("Cannot create directory: %s", dir)

def make_embedded_articles(template):
    r = {}
    if template.embedd != None:
        for variable_name, article in template.embedd.items():
            logging.info("Embedding article: %s", article)
            r[variable_name] = markdown.markdown(articles.get_article_from(configuration['source'], article).content)
    return r

def insert_block_count(block, count):
    end_of_tag = block.find(">")
    if end_of_tag:
        return block[0:end_of_tag] + ' data-block-count="{}" '.format(count) + block[end_of_tag:]
    else:
        return block

def replace_block(file_path, block, after):
    with open(file_path, 'r') as f:
        file_contents = f.read()

    blocks = file_contents.split("\n\n")
    print(after)
    new_file_contents = "\n\n".join(blocks[0:block] + [after] + blocks[block+1:])

    with open(file_path, 'w') as f:
        f.write(new_file_contents)
        return True

def generate_article(decorator, environment, article, edit=False):
    template = decorator.get_template_for_type(article.type)
    if template == None:
        raise Exception("No template found for article type: %s", article.type)
    jinja_template = environment.get_template(template.file)
    content = ""
    if edit:
        md_content = preprocessor.process(article.content, article.name)
        blocks = md_content.split("\n\n")
        for (c, block) in enumerate(blocks):
            t = markdown.markdown(block, extensions=['markdown.extensions.toc', 'markdown.extensions.fenced_code'])
            content += insert_block_count(t, c)
    else:
        md_content = preprocessor.process(article.content, article.name)
        content = markdown.markdown(md_content, extensions=['markdown.extensions.toc', 'markdown.extensions.fenced_code'])
    data = article.data
    data.update(make_embedded_articles(template))
    return jinja_template.render(content=content, **data).encode("utf-8")

def generate(source, output, decorator_path, templates_folder, template_map):
    d = decorator.Decorator(decorator_path, templates_folder, template_map)
    d.add_handler('.less', filehandlers.LessProcessor)
    d.build_decoration(output)
    environment = jinja2.Environment(loader=jinja2.FileSystemLoader(d.template_folder))
    permalinks = {}
    for article in articles.get_articles_from(source):
        if article.permalink != None:
            if article.permalink in permalinks:
                raise Exception("Duplicate permalink found %s's permalink and %s's permalinks are same" % (article.name, permalinks[article.permalink]))
            permalinks[article.permalink] = article.name
            output_path = os.path.join(output, *os.path.split(article.permalink))
            if article.publish:
                make_sure_dir_exists(output_path)
                with open(output_path, 'wb') as f:
                    try:
                        f.write(generate_article(d, environment, article))
                    except:
                        logging.warning("Error generating article: %s", article.name)
                        pass
                    logging.info("File written: %s", output_path)
            else:
                logging.info("Not publishing %s",  article.name)
                try:
                    os.remove(output_path)
                except:
                    pass

def inject_scripts(article):
    return Template('''
    <script src="//code.jquery.com/jquery-3.3.1.min.js"></script>
    <script>
        var permalink = '${permalink}';
        var block = null;
        function openDialog(je, file_contents) {
            if ($$('#save-button').length > 0) {
                return;
            }
            text_area = $$('<textarea>')
            text_area.val(file_contents);
            var saveB = $$('<button>').insertAfter(je).html("Save");
            var cancelB = $$('<button>').insertAfter(saveB).html("Cancel");
            saveB.attr('id', "save-button");
            cancelB.attr('id', "cancel-button");
            cancelB.click(function() {
                location.reload();
            });

            saveB.click(function() {
                $$.post('/feni_rt_save_/'+ permalink, {block: block, after: text_area.val()}, function(response) {
                    block = null;
                    if (response == 'failed') {
                        je.html(before);
                    }
                    location.reload();
                });
            });
            text_area.css({'width':(je.width()+'px')});
            text_area.css({'height':(je.height()+'px')});
            je.replaceWith(text_area);
            text_area.focus();
        }
        $$(function() {
            $$('p, h1, h2, h3, h4, h5, h6, blockquote, b, i, strong, em, small, ul, ol').click(function(e) {
                if (block !== null) return;
                var je = $$(e.target);
                while (true) {
                    block = je.data('block-count');
                    if (block === undefined) {
                        je = je.parent();
                        if (je.is('body')) {
                            break;
                        }
                    } else {
                        break;
                    }
                }
                if (block) {
                    $$.post('/feni_rt_get_/'+permalink, {block: block}, function(file_content) {
                        openDialog(je, file_content);
                    });
                }
            });
        });

    </script>''').substitute({'permalink': article.permalink})

template_html =  '''
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="">
    <meta name="author" content="">
    <link href="/styles.css" rel="stylesheet" type="text/css"></link>
</head>

<body class="language-markup">
    <% for item in items: %>
    <div><a href="feni_rt_edit_/{{item.permalink}}">{{ item.name }}</a></div>
    <% end %>
</body>

</html>'''

@route('/feni_rt_get_/<permalink:path>', method='POST')
def get_matching(permalink):
    block = int(request.forms.get('block'))
    config = configuration.read()
    for article in articles.get_articles_from(config['source']):
        if article.permalink == permalink:
            with open(article.path, 'r') as f:
                file_contents = f.read()
                blocks = file_contents.split("\n\n")
                return blocks[block]

@route('/feni_rt_save_/<permalink:path>', method='POST')
def save(permalink):
    block = int(request.forms.get('block'))
    after = request.forms.get('after')
    config = configuration.read()
    for article in articles.get_articles_from(config['source']):
        if article.permalink == permalink:
            if replace_block(article.path, block, after):
                return template("{{content}}", content="success")
    return template("{{content}}", content="failed")

@route('/feni_rt_edit_/<permalink:path>')
def edit(permalink):
    config = configuration.read()
    d = decorator.Decorator(config['decorator'], config['template'],  config['templatemap'])
    d.add_handler('.less', filehandlers.LessProcessor)
    environment = jinja2.Environment(loader=jinja2.FileSystemLoader(d.template_folder))
    for article in articles.get_articles_from(config['source']):
        if article.permalink == permalink:
            article_html = generate_article(d,environment, article, edit=True)
            article_html = article_html.replace(str.encode("</head>"), str.encode(inject_scripts(article) + "</head>"))
            return article_html
    return template("Article not found!")

@route('/')
def index():
    config = configuration.read()
    items = []
    for article in articles.get_articles_from(config['source']):
        items.append(article)
    return template(template_html, items=items)

@route('/<filename:path>', name='static')
def serve_static(filename):
    config = configuration.read()
    return static_file(filename, root=config['decorator'])

def main():
    try:
        (config, args) = configuration.read()
        if args.server:
            port = 8080
            while True:
                try:
                    run(host='0.0.0.0', port=port)
                    break
                except OSError:
                    port += 1
        elif args.sample:
            print("Generating sample")
            create_sample()
        else:
            generate(config['source'], config['output'], config['decorator'], config['template'], config['templatemap'])
            logging.info("Successfully created site in %s", config['output'])
    except Exception as ex:
        logging.error(str(ex))
        raise

app = default_app()
