===============================================
Feni - A simple static site generator
===============================================

Feni is a simple static site generator. You can use it to build your
site from a set of markdown files and a number of templates (Jinja2)

**Running Feni**

feni --source articles_dir --template templates_dir --decorator designfiles --output my_site

You can put the configuration values in a yaml file and pass the path to the file in
the --config option.

Feni needs the following information to function, that it can read
from command line arguments or from a configuration file.

1. A source directory. This is where Feni looks for content. Right now it only
look for .md files. Each of this file should be of format as shown below.::

    main: true
    type: post
    permalink: test-post.html
    publish: true
    data-title: My test post
    data-subtitle: This is as test post
    ---
    ###This is the content of the post in markdown format###

Every article needs to have a header in yaml format that contain information
regarding how the final html should be generated. The first one, the 'main'
attribute denotes if the article is intended to be a whole article or if it is
part of a bigger article. If it is a whole article, this attribute should be true.
If it is a sub article, then this should be false.

The next attribute, the 'type', as the name implies, denotes the type of the article.
This attribute is used to find a template that can be used to expand this article.

'permalink' attribute is the final location of the generated html file. This should be
relative path. The generated html is placed under this path relative to the output
directory. 

'publish' attribute is used to denote wether to generate an article or not. If the
'publish' status of an article is changed to false, then that article is removed
from it's permalink location in the target folder, if it already exists.

the data- attributes are custom fields that you can define, which will be available in
your template. This can be any valid yaml value. For example, you this can be a list
where each item is information about an article. This list can be used to display a
list of articles in the target template. If you define a value 'data-article_name', then
that value will be available in the template as 'article_name' key.

2. A destination directory. This is where the generated files will be put.

3. A decorator directory. This is where all the other files, like css files, js files,
background images come from. This folder will be mostly copied as such into the output
folder. If there are files matching the enabled file handlers, then those will be passed
through them. Right now only .less files will be processed into css files.

4. A path to a templates folder that should contain all the jinja templates.

5. Path to a template configuration file. This file has the following format.::

    about.html:
        types:
            - aboutme
    post.html:
        types:
            - post
    
As you can see, this just lists the template files and declares the type of
articles it can handle. By default, Feni looks for this file in the templates folder
under the name templates.yaml. But you can change that using the --templatemap
option

Feni can read this from a configuration file in yaml format.::

    source: articles
    destination: output
    decorator: design

By default, Feni looks for the this file in the current folder and folders above it.
Paths read from it will be considers as relative to the directory where it is found.
Template paths in template.yaml will be taken relative to the template directory.
