$(document).ready(function(){
    if ($('#statusdet').text() == 'active status') {
        $('#statusdet').removeClass("light-purple");
        $('#statusdet').addClass("light-green");
    }
    else if ($('#statusdet').text() == 'x-ray status') {
        $('#statusdet').removeClass("light-purple");
        $('#statusdet').addClass("light-red");
    }
    if ($('#actype').text() == 'normal actype') {
        $('#actype').removeClass("light-purple");
        $('#actype').addClass("light-green");
    }
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
