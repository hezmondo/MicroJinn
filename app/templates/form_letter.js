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
    $('#expand_edit').on('shown.bs.collapse', function () {
        $("#doc_html").css({"background-color": "white"});
        $(':input').prop('readonly', false);
    });
    $('#expand_edit').on('hidden.bs.collapse', function () {
        $("#doc_html").css({"background-color": "#f8f8f8"});
        $(':input').prop('readonly', true);
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
