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

def replace_string(file_path, before, after):
    with open(file_path, 'r') as f:
        file_contents = f.read()

    with open(file_path, 'w') as f:
        if (file_contents.count(before) != 1):
            return False
        else:
            new_contents = file_contents.replace(before, after)
            f.write(new_contents)
            return True

def generate_article(decorator, environment, article):
    template = decorator.get_template_for_type(article.type)
    if template == None:
        raise Exception("No template found for article type: %s", article.type)
    jinja_template = environment.get_template(template.file)
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
        var before = "";
        function openDialog(e) {
            if ($$('#save-button').length > 0) {
                return;
            }
            var je = $$(e);
            before = je.text();
            var saveB = $$('<button>').insertAfter(je).html("Save");
            var cancelB = $$('<button>').insertAfter(saveB).html("Cancel");
            saveB.attr('id', "save-button");
            cancelB.attr('id', "cancel-button");
            cancelB.click(function() {
                je.text = before;
                je.attr('contenteditable', "false");
                saveB.remove();
                cancelB.remove();
            });

            saveB.click(function() {
                $$.post('/save/'+ permalink, {before: before, after: je.text()}, function() {
                    je.attr('contenteditable', "false");
                    saveB.remove();
                    cancelB.remove();
                });
            });
            je.attr('contenteditable', 'true');
            je.focus();
        }
        $$(function() {
            $$('p').click(function(e) {
                openDialog(e.target);
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
    <div><a href="edit/{{item.permalink}}">{{ item.name }}</a></div>
    <% end %>
</body>

</html>'''

@route('/save/<permalink:path>', method='POST')
def save(permalink):
    before = request.forms.get('before')
    after = request.forms.get('after')
    config = configuration.read()
    for article in articles.get_articles_from(config['source']):
        if article.permalink == permalink:
            if replace_string(article.path, before, after):
                return template("{{content}}", content="success")
    return template("{{content}}", content="failed")

@route('/edit/<permalink:path>')
def edit(permalink):
    config = configuration.read()
    d = decorator.Decorator(config['decorator'], config['template'],  config['templatemap'])
    d.add_handler('.less', filehandlers.LessProcessor)
    environment = jinja2.Environment(loader=jinja2.FileSystemLoader(d.template_folder))
    for article in articles.get_articles_from(config['source']):
        if article.permalink == permalink:
            article_html = generate_article(d,environment,article)
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
        config = configuration.read()
        if config['server']:
            run(host='0.0.0.0')
        generate(config['source'], config['output'], config['decorator'], config['template'], config['templatemap'])
        logging.info("Successfully created site in %s", config['output'])
    except Exception as ex:
        logging.error(str(ex))
        raise

app = default_app()
