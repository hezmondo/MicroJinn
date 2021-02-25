$(document).ready(function(){
    //copy text from readonly input on click
    $('.copyable-input').click(function(e) {
        if ( $(this).is('[readonly]') ) {
            var element = $(this);
            copyToClipboard(this);
            $('#copy_modal').modal();
            setTimeout(function() {$('#copy_modal').modal('hide');}, 1000);
        }
    });
    //copy text from table on click
    $('.copyable-text').click(function(e) {
        let range = new Range();
        range.setStart(this, 0);
        range.setEnd(this, this.childNodes.length);
        window.getSelection().removeAllRanges();
        window.getSelection().addRange(range);
        document.execCommand("copy");
        $('#copy_modal').modal();
        setTimeout(function() {$('#copy_modal').modal('hide');}, 1000);
    });
    $('#edit_tenant').click(function(e) {
        $('#tenant_modal').modal();
    });
    //show more details and scroll to bottom
    $("#open_edit_rent").click(function(){
        $('#edit_modal').modal();
        });
    $('#copy_modal').on('show.bs.modal', function (e) {
        $('body').addClass("modal-no-backdrop");
    }).on('hide.bs.modal', function (e) {
        setTimeout(function() {$('body').removeClass("modal-no-backdrop");}, 1000);
    });
});
//function to copy text from text area (in rent screen) to clipboard
function copyToClipboard(element) {
  element.select();
  element.setSelectionRange(0, 99999)
  document.execCommand("copy");
}
