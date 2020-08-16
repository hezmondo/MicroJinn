$(document).ready(function(){
    $("#show-xalloc").click(function(){
      $("#xalloc").toggle();
      if ($(this).text() == "Show extra allocation") {
        $(this).text("Hide extra allocation");
      } else {
        $(this).text("Show extra allocation");
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
    $('#savehtml').click(function() {
    var mysave = $('#letter_html').html();
    $('#xinput').val(mysave);
    });
});
