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
            $(this).removeClass("edit");
            $(this).addClass("eye");
            $(this).text("view");
            $(':input').prop('readonly', false);
            $("#save_delete").show();
            }
        else {
            $(this).addClass("edit");
            $(this).removeClass("eye");
            $(this).text("edit");
            $(':input').prop('readonly', true);
            $("#save_delete").hide();
        }
    });
    $(".btn-check").click(function(){
        if($(".btn-tog").hasClass('check')){
            $(".btn-tog").removeClass("check");
        }
        else {
            $(".btn-tog").addClass("check");
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
        var pr_addr_strip = pr_addr.replace(/[^\x20-\x7E]/gmi, "");
        $('#pr_addr').val(pr_addr_strip);
    });

    resize_view();
    $(window).resize(function(){
        resize_view();
    });
      var loc = window.location.pathname;

   $('#nav_bar').find('a').each(function() {
     $(this).toggleClass('active', $(this).attr('href') == loc);
  });

});
$(function() {
  // Sidebar toggle behavior
  $('#sidebarCollapse').on('click', function() {
    $('#sidebar, #content').toggleClass('active');
  });
});
$(function () {
    $('[data-toggle="tooltip"]').tooltip();
});

function resize_view() {
            var viewportwidth;
        if(typeof window.innerWidth!='undefined'){
              viewportwidth=window.innerWidth;
        }
       $('#nav_aside').removeClass("fixed-top");
       $('#nav_aside').removeClass("nav-display");
       $('#nav_bar').removeClass("navbar-expand");

       if(viewportwidth >= 768){
           $('#nav_aside').addClass("fixed-top");
           $('#nav_aside').addClass("nav-display");
           $('#nav_bar').removeClass("navbar-expand");
       }
       else {
           $('#nav_bar').addClass("navbar-expand");
        }
}