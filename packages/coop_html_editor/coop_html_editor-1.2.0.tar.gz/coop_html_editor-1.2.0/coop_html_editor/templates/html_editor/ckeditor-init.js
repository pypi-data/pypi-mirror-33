CKEDITOR.disableAutoInline = true;

/**
 *
 * Transform images and document links when dropped in editor from media-library
 *
 */
var adaptDroppedElement = function () {

    $(".inline-editable img[data-class=library-thumbnail]").each(function(idx, elt) {
      $(elt).removeClass("library-thumbnail");
      $(elt).removeAttr("data-class");
      $(elt).attr("src", $(elt).attr("rel"));
      $(elt).attr("data-cke-saved-src", $(elt).attr("rel"));
      $(elt).removeAttr('rel');
      {% if config.image_default_class %}
      $(elt).addClass('{{ config.image_default_class }}');
      {% endif %}
    });

    $(".inline-editable img[data-class=library-document]").each(function(idx, elt) {
      $(elt).removeAttr("data-class");
      var doc_url = $(elt).attr('rel');
      var doc_title = $(elt).attr('title');
      var icon_url = $(elt).attr('src');
      var doc_ext = icon_url.replace(/\\/g,'/').replace( /.*\//, '').replace('.png', '');
      var link = '<a href="'+doc_url+'" target="_blank" class="doc-link" rel="'+doc_ext+'">'+'<img src="'+icon_url+'" /><span class="doc-title">'+doc_title+'</span></a>';
      $(link).insertAfter($(elt));
      $(elt).remove();
    });
};

/**
 *
 * Save the editor content in form field
 *
 */
var saveInlineEditorData = function(editorId, editorElt) {
    var data = editorElt.getData();
    $('#' + editorId + '_hidden').attr('value', data);
};

/**
 *
 * Editor ready
 *
 */
$(document).ready(function() {
    CKEDITOR.stylesSet.add( 'cms_styles', [
        {% for style in config.css_classes %}
        {{ style|safe }}{% if not forloop.last %},{% endif %}
        {% endfor %}
    ]);
    $('.inline-editable').attr('contenteditable', 'true');
    $('.inline-editable').each(function(index, elt) {
        var editorId = $(elt).attr('id');
        CKEDITOR.inline(editorId, {
            customConfig: '{% url "ckeditor_config" %}',
            filebrowserBrowseUrl: '{% url "browser_urls" %}',
            filebrowserImageBrowseUrl: '{% url "browser_images" %}',
            on: {
                change: function( event ) {
                    saveInlineEditorData(editorId, event.editor);
                },
                drop: function (event) {
                    setTimeout(function() {
                        adaptDroppedElement();
                        saveInlineEditorData(editorId, event.editor);
                    }, 100);
                }
            }
        });
    });
});