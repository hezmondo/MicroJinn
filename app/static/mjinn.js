$(document).ready(function(){
    $("#save_delete").hide();
    $("#edit_rent").hide();
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
    //add tick icon on click to toggle button
    $(".btn-check").click(function(){
        if($(".btn-tog").hasClass('check')){
            $(".btn-tog").removeClass("check");
        }
        else {
            $(".btn-tog").addClass("check");
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
    //copy address field and separate each line
    $('#address_fields').click(function() {
        var addr = $('#address_fields option:selected').text();
        var addr_split = addr.replace(/,/g, "<br />");
        $('#addr_span').html(addr_split);
        $('#addr_span').append("<br />");
    });
    //save pr - collect address to put in summary
    $('.save_pr').click(function() {
        var pr_block = $('#doc_html').html();
        $('#pr_block').val(pr_block);
        var pr_addr = $('#addr_span').text().trim();
        var pr_addr_strip = pr_addr.replace(/[^\x20-\x7E]/gmi, "");
        $('#pr_addr').val(pr_addr_strip);
    });
    //allow display and navbar to change for smaller screens / phones
    resizeView();
    $(window).resize(function(){
        resizeView();
    });
    var loc = window.location.pathname;
    $('#nav_bar').find('a').each(function() {
        $(this).toggleClass('active', $(this).attr('href') == loc);
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
//allows for bootstrap style tooltips
$(function () {
    $('[data-toggle="tooltip"]').tooltip();
});

//allow display and navbar to change for smaller screens / phones
function resizeView() {
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
