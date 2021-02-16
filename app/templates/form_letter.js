$(document).ready(function(){
    $('#bold_text').click(function(){
        add_markup('**');
    });
    $('#italic_text').click(function(){
        add_markup('^^');
    });
    $('#highlight_text').click(function(){
        add_markup('||');
    });
    $('#remove_markup').click(function(){
        remove_markup();
    });
    $('#doc_html').html(function(i, html) {
      return html.replace(/\*\*(.*?)\*\*/g, '<span class="emboldened">$1</span>');
    });
    $('#doc_html').html(function(i, html2) {
      return html2.replace(/\^\^(.*?)\^\^/g, '<span class="italic">$1</span>');
    });
    $('#doc_html').html(function(i, html3) {
      return html3.replace(/\|\|(.*?)\|\|/g, '<span class="highlighted">$1</span>');
    });
    $('[name = "lease_variables"]').on('change', function() {
        var selected = $('[name = "lease_variables"]').val();
        add_word(selected);
    });
    $('[name = "mail_variables"]').on('change', function() {
        var selected = $('[name = "mail_variables"]').val();
        add_word(selected);
    });
    $('#more_vars').click(function(){
        $('#more_vars').hide();
        $('#lease_vars').show();
    });
});

function add_markup(markup) {
    var data = get_data();
    var text = (data[0].val()).substring(data[1], data[2]);
    data[0].val(data[3] + markup + text + markup + data[4]);
    data[0].focus();
}
function remove_markup() {
    var data = get_data();
    var text = (data[0].val()).substring(data[1], data[2]);
    text = text.replace(/([\*\^\|/])/g, '');
    data[0].val(data[3] + text + data[4]);
    data[0].focus();
}
function add_word(word) {
      var data = get_data();
      data[0].val(data[3] + word + data[4])
      data[0].focus();
}

function get_data() {
    var txtarea = $('#form_letter_block');
    var caretStart = txtarea[0].selectionStart;
    var caretEnd = txtarea[0].selectionEnd;
    var front = (txtarea.val()).substring(0, caretStart);
    var back = (txtarea.val()).substring(caretEnd, txtarea.val().length);
    var data = [txtarea, caretStart, caretEnd, front, back];
    return data;
}
