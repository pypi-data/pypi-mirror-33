coop HTML Editor
===============================================

* `What is coop_html_editor good for?`_
* `Quick start`_
* `Settings`_

.. _What is coop_html_editor good for?: #good-for
.. _Quick start?: #quick-start
.. _Settings?: #settings

.. _good-for:

What is coop_html_editor good for?
------------------------------------
coop_html_editor is a backend for using inline HTML editor into a Django site.
It enables inline editing for your HTML content.
It includes a django Form and a Widget helper.
It supports Aloha Editor and CK Editor

.. _quick-start:

Quick start
------------------------------------
In settings.py, add 'coop_html_editor' to the INSTALLED_APPS
In urls.py add ``(r'^html-editor/', include('coop_html_editor.urls'))`` to your urlpatterns

Then create a form. For example something like ::

    import floppyforms.__future__ as floppyforms
    from models import Note
    from coop_html_editor.widgets import get_inline_html_widget
    
    class NoteForm(floppyforms.ModelForm):
        class Meta:
            model = Note
            fields = ('text',)
            widgets = {
                'text': get_inline_html_widget(),
            }


Let's assume that you've a ``form`` variable pointing on an instance of a NoteForm.
In the template file, call the form and don't forget to put ``{{form.media}}`` in the headers.

.. _settings:

Settings
------------------------------------

The following constants can be set in your django project settings.py

You can choose between 2 HTML editors : Aloha editor or CkEditor. We recommend to use CkEditor but keep Aloha by default
for compatibility. Add one the 2 lines below in your settings.py

    COOP_HTML_EDITOR = 'aloha'
    COOP_HTML_EDITOR = 'ck-editor'

You can tune your editor by changing the settings below. The values in this README correspond to defaults

For both, we package a default version than can be overriden by copying your own version folder in ste static files
and define the new version by

    ALOHA_VERSION = "aloha.0.23.26"
    CKEDITOR_VERSION = "ckeditor.4.6.2"

The initialisation code of the editor is set in a javascript file. You can change the file to use by seetings

    ALOHA_INIT_JS_TEMPLATE = "html_editor/aloha_init.js"
    CKEDITOR_INIT_JS_TEMPLATE = "html_editor/ckeditor-init.js"

If you choose CkEditor, you can add your own styles

    CKEDITOR_CSS_CLASSES = [
         "{name: 'Highlight', element: 'span', attributes: {'class': 'highlight'}}",
         "{name: 'Red Title', element: 'h3', styles: {color: '#880000'}}",
    ]


InlineHtmlInput has a "provider" that allows you to add local links to your models (articles, contacts, whatever) easily, through an autocomplete field that will search for objects based on rules you defined for each model :

* search this kind of models using get_absolute_url()
* search this kind of models using another method
* search this kind of models using a specified model field

You can set the ``HTML_EDITOR_LINK_MODELS`` setting in your settings.py to tell which django models will be available in the auto-complete field of the "add link" widget like this ::

    HTML_EDITOR_LINK_MODELS = ('coop_local.Article', 'calendar.Event', )
    
    
djaloha requires jquery and is provided by default with jquery.1.7.2. You can change the jquery version if needed ::

    HTML_EDITOR_JQUERY = 'js/jquery.1.7.2.js'
    
    
Aloha has a nice plugin architecture. coop_html_editor includes by default the main Aloha plugins. You may want to have a different set of plugins.
Please refer to the Aloha docs for more information on plugins ::

    ALOHA_PLUGINS = (
        "common/format",
        "common/highlighteditables",
        "common/list",
        "common/link",
        "common/undo",
        "common/paste",
        "common/commands",
        "common/image",
        "common/align",
        "extra/attributes",
        "common/characterpicker",
        "common/abbr",
        "common/horizontalruler",
        "common/table",
        "extra/browser",
    )
    

Please note that the ``ALOHA_PLUGINS`` setting is a global setting. If you need to change the set of plugins for a specific form field, you
can pass a similar tuple in the ``aloha_plugins`` attribute of your ``coop_html_editor`` widget.
The ``extra_aloha_plugins`` attribute will add additional plugins to the default set.

``HTML_EDITOR_INIT_URL`` setting make possible to overload the aloha init file of djaloha.
``html_editor_init_url`` attribute of ``InlineHtmlInput`` can also be used to overload it for a specific form field.

License
=======

coop_html_editor is based on apidev-djaloha is a fork from credis/djaloha (see http://github.com/credis/djaloha)

coop_html_editor uses the BSD license. see license.txt

Djaloha development was funded by `CREDIS <http://credis.org/>`_, FSE (European Social Fund) and Conseil Regional d'Auvergne.
