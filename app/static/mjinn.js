$(document).ready(function(){
    $("#save_delete").hide();
    $("#more_buttons").hide();
    $("#xalloc").hide();
    $("#new_address_fields").hide();
    $("#new_address_fields").attr('disabled', '');

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
        $("#add_remove_address").click(function(){
        if ($(this).text() == "manually change address") {
            $(this).text("use original address");
            $("#new_address_fields").show();
            $("#new_address_fields").removeAttr('disabled');
            $("#address_fields").hide();
            $("#address_fields").attr('disabled', '');
            }
        else {
            $(this).text("manually change address");
            $("#new_address_fields").hide();
            $("#new_address_fields").attr('disabled', '');
            $("#address_fields").show();
            $("#address_fields").removeAttr('disabled');
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
});
$(function() {
  // Sidebar toggle behavior
  $('#sidebarCollapse').on('click', function() {
    $('#sidebar, #content').toggleClass('active');
  });
});