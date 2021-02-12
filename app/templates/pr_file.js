$(document).ready(function(){
    var email_dets = $('#hidden_email_dets').html();
    $('#email_dets_span').html(email_dets);
    var subject = $('#subject_span').html();
    $('#email_subject_span').html(subject);
    var owings = $('#owings_div').html();
    $('#email_owings_span').html(owings);
    var manager_name = $('.manager-name').html();
    var manager_addr = $('.manager-addr').html();
    $('#email_manager_span').html(manager_name + "<br />" + manager_addr);
});