$(document).ready(function(){
    $("#save_delete").hide();
    $("#more_buttons").hide();
    $("#xalloc").hide();

//    if ($("#item_id").text() == "0") {
//       $("#toggleview").click();
//            }
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
        var addr_split = addr.replace(/,/g, "<br />")
        $('#addr_span').html(addr_split)
    });
    $('.save_pr').click(function() {
        var pr_block = $('#doc_html').html();
        $('#pr_block').val(pr_block);
        var pr_addr = $('#addr_span').text().trim();
        var pr_addr_strip = pr_addr.replace(/[^\x20-\x7E]/gmi, "")
        $('#pr_addr').val(pr_addr_strip);

//        var pr_email = $('#email_span').text();
//        $('#pr_email').val(pr_email);
//        var pr_subject = $('#subject_span').text();
//        $('#pr_subject').val(pr_subject);
    });
    $('#pr_email').click(function() {
        $('.post_div').hide();
        $('.email_div').show();
        $('#doc_html').show();
        var salutation_subject = $('#salutation_subject_span').html();
        $('#email_salutation_subject_span').html(salutation_subject);
        $('#send_email').prop('disabled', false);
    });
    $('#pr_attachment').click(function() {
        $('.post_div').show();
        $('.email_div').hide();
        $('#doc_html').show();
        var salutation_subject = $('#salutation_subject_span').html();
        var ref_email = $('#ref_email').html();
        $('#email_header_span').html(ref_email);
        $('#email_header_span').append(salutation_subject);
        $('#salutation_subject_span').html(salutation_subject);
        $('#send_email').prop('disabled', false);
    });
//    $('#radio_email').click(function() {
//        $('#email_html').show();
//    });
//    $('#radio_post').click(function() {
//        $('#email_html').hide();
//    });
//    $("#email").on("paste keyup", function() {
//        $("#email_span").html(this.value);
//    });
//    $("#subject").on("paste keyup", function() {
//        $("#subject_span").html(this.value);
//    });
//    $("#email_span").on('change', function() {
//        $("#email").val(this.value);
//    });
});
$(function() {
  // Sidebar toggle behavior
  $('#sidebarCollapse').on('click', function() {
    $('#sidebar, #content').toggleClass('active');
  });
});