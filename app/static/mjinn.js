$(document).ready(function(){
    $("#save_delete").hide();
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
    $('#expand_div').on('hidden.bs.collapse', function () {
        $('#expand_div_toggle').removeClass('minus').addClass('plus');
    });
    $('#expand_div').on('shown.bs.collapse', function () {
        $('#expand_div_toggle').removeClass('plus').addClass('minus');
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
      return html.replace(/\*\*(.*?)\*\*/g, '<span style="font-weight:bold;">$1</span>');
    });
    $('#doc_html').html(function(i, html2) {
      return html2.replace(/\^\^(.*?)\^\^/g, '<span style="font-style:italic;">$1</span>');
    });
    $('#doc_html').html(function(i, html3) {
      return html3.replace(/\|\|(.*?)\|\|/g, '<span style="background-color:yellow;">$1</span>');
    });
    //the expandable table buttons (show more) are found with id show_more_1 or show_more_2 (we can have a maximum
    //of two expandable tables per page). We want to change the text of the buttons after they are expanded.
    $('#accordion_1').on('shown.bs.collapse', function () {
        $('#show_more_1').text('show fewer');
        $('#show_more_1').removeClass('arrow-down');
        $('#show_more_1').addClass('arrow-up');
    });
    $('#accordion_1').on('hidden.bs.collapse', function () {
        $('#show_more_1').text('show more');
        $('#show_more_1').addClass('arrow-down');
        $('#show_more_1').removeClass('arrow-up');
    });
    $('#accordion_2').on('shown.bs.collapse', function () {
        $('#show_more_2').text('show fewer');
        $('#show_more_2').removeClass('arrow-down');
        $('#show_more_2').addClass('arrow-up');
    });
    $('#accordion_2').on('hidden.bs.collapse', function () {
        $('#show_more_2').text('show more');
        $('#show_more_2').addClass('arrow-down');
        $('#show_more_2').removeClass('arrow-up');
    });
    $(document).on('shown.bs.modal', function(e) {
        $('input:visible:enabled:first', e.target).focus();
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
