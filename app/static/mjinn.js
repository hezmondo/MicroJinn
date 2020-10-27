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
    $(".custom-file-input").on("change", function() {
      var fileName = $(this).val().split("\\").pop();
      $(this).siblings(".custom-file-label").addClass("selected").html(fileName);
    });
    $('#savehtml').click(function() {
    var mysave = $('#doc_html').html();
    $('#xinput').val(mysave);
    });
    $('#rentobjview').find(':input').attr('disabled', 'disabled');
});
