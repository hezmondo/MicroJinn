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
        // remove unwanted characters
        var pr_addr_strip = pr_addr.replace(/[^\x20-\x7E]/gmi, "");
        // remove extra whitespace
        var pr_addr_strip_clean = pr_addr.replace(/\s+/g, " ");
        $('#pr_addr').val(pr_addr_strip_clean);
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
    // Selecting an filter from advanced filters will populate the search fields
    $('.load-filters').mousedown(function(e) {
        var dict = $.parseJSON($(this).val());
        $('#filter-rentcode').val(dict.rentcode);
        $('#filter-tenantname').val(dict.tenantname);
        $('#filter-propaddr').val(dict.propaddr);
        $('#filter-agentdetail').val(dict.agentdetail);
        $('#filter-landlord').val(dict.landlord);
        $('#filter-tenure').val(dict.tenure);
        $('#filter-status').val(dict.status);
        $('#filter-salegrade').val(dict.salegrade);
        $('#filter-actype').val(dict.actype);
        $('#filter-source').val(dict.source);
        $('#filter-rentpa').val(dict.rentpa);
        $('#filer-arrears').val(dict.arrears);
        $('#filter-rentperiods').val(dict.rentperiods);
        $('#filter-enddate').val(dict.enddate);
        $('#filter-charges').val(dict.charges);
        $('#filter-agentmailto').val(dict.agentmailto);
        $('#filter-emailable').val(dict.emailable);
        $('#filter-prdelivery').val(dict.prdelivery);
        $('#filter-filtertype').val(dict.filtertype);
        // expand filters
        $('.collapse-filter').collapse('show');
    });
    $('.hide-filters').mousedown(function(e) {
        $('.collapse').collapse('hide');
    });
    $('.clear-filters').mousedown(function(e) {
        $('#filter-rentcode').val('');
        $('#filter-tenantname').val('');
        $('#filter-propaddr').val('');
        $('#filter-agentdetail').val('');
        $('#filter-landlord').val('');
        $('#filter-tenure').val('');
        $('#filter-status').val('');
        $('#filter-salegrade').val('');
        $('#filter-actype').val('');
        $('#filter-source').val('');
        $('#filter-rentpa').val('');
        $('#filer-arrears').val('');
        $('#filter-rentperiods').val('');
        $('#filter-enddate').val((new Date()).toISOString().split('T')[0]);
        $('#filter-charges').val('');
        $('#filter-agentmailto').val('');
        $('#filter-emailable').val('');
        $('#filter-prdelivery').val('');
        $('#filter-filtertype').val('');
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
