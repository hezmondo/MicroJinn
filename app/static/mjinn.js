$(document).ready(function(){
    $("#save_delete").hide();
    $("#more_buttons").hide();
    $("#xalloc").hide();
    $("#show-xalloc").click(function(){
        $("#xalloc").toggle();
        if ($(this).text() == "show extra alloc") {
            $(this).text("hide extra alloc");
            } else {
            $(this).text("show extra alloc");
        };
    });
    $('#add-alloc').click(function() {
      var $thing = $('#xalloc').clone();
      $('#newalloc').html($thing);
    });
    $(".clickable-row").click(function() {
       alert($(this).data("href"));
        window.location = $(this).data("href");
    });
    $("#edit_view").click(function(){
        if ($(this).text() == "edit") {
            $(this).text("view");
            $(':input').prop('readonly', false);
            $("#save_delete").show();
            }
        else {
            $(this).text("edit");
            $(':input').prop('readonly', true);
            $("#save_delete").hide();
        }
    });
    $("#more_less").click(function(){
        if ($(this).text() == "more") {
            $(this).text("less");
            $("#more_buttons").show();
            }
        else {
            $(this).text("more");
            $("#more_buttons").hide();
        }
    });
    $(".custom-file-input").on("change", function() {
      var fileName = $(this).val().split("\\").pop();
      $(this).siblings(".custom-file-label").addClass("selected").html(fileName);
    });
    $('#savehtml').click(function() {
        var mysave = $('#doc_html').html();
        $('#xinput').val(mysave);
    });
    $('#address_fields').click(function() {
        var addr = $('#address_fields option:selected').text();
        var addr_split = addr.replace(/,/g, "<br />");
        $('#addr_span').html(addr_split);
        $('#addr_span').append("<br />");
    });
    $('.save_pr').click(function() {
        var pr_block = $('#doc_html').html();
        $('#pr_block').val(pr_block);
        var pr_addr = $('#addr_span').text().trim();
        var pr_addr_strip = pr_addr.replace(/[^\x20-\x7E]/gmi, "")
        $('#pr_addr').val(pr_addr_strip);
    });
    $('#bold_text').click(function(){
        add_markup('**');
    });
        $('#italic_text').click(function(){
        add_markup('^^');
    });
        $('#highlight_text').click(function(){
        add_markup('||');
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
});
$(function() {
  // Sidebar toggle behavior
  $('#sidebarCollapse').on('click', function() {
    $('#sidebar, #content').toggleClass('active');
  });
});

function add_markup(markup) {
    var txtarea = $('#form_letter_block');
    var caretStart = txtarea[0].selectionStart;
    var caretEnd = txtarea[0].selectionEnd;
    var front = (txtarea.text()).substring(0, caretStart);
    var text = (txtarea.text()).substring(caretStart, caretEnd);
    var back = (txtarea.text()).substring(caretEnd, txtarea.text().length);
    txtarea.html(front + markup + text + markup + back);
    txtarea.focus();
}