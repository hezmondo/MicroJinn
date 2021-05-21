$(document).ready(function(){
    var subject = $('#subject_span').html();
    $('#email_subject_span').html(subject);
    var owings = $('#owings_div').html();
    $('#email_owings_span').html(owings);
    var manager_name = $('.manager-name').html();
    var manager_addr = $('.manager-addr').html();
    $('#email_manager_span').html(manager_name + "<br />" + manager_addr);
    $('#send_email').mousedown(function(e) {
        var html_body = $('#email_html').html();
        $('#html_body').val(html_body);
        var subject = $.trim($('#email_subject_span').text().replace(/[\t\n]+/g,' '));
        $('#subject').val(subject);
        var recipients = $('#email_span').text();
        $('#recipients').val(recipients);
        $('.modal-body').append(' '+ recipients)
    });
});