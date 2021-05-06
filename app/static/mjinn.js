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
    //On selecting a next rent date element in a table, we want to copy that element value, paste it into the search
    //field and search the database
    $('.search-date').mousedown(function(e) {
        var date = $(this).val();
        $('.date').val(date);
    });
    // Selecting an item from search history will populate the search fields and complete the search
    $('.search-history').mousedown(function(e) {
        var dict = $.parseJSON($(this).val());
        $('#form-rentcode').val(dict.rentcode);
        $('#form-address').val(dict.address);
        $('#form-agent').val(dict.agent);
        $('#form-nextrentdate').val(dict.nextrentdate);
        $('#form-status').val(dict.status);
    });
    $('.search-clear').click(function(e) {
        $('#form-rentcode').val('');
        $('#form-address').val('');
        $('#form-agent').val('');
        $('#form-nextrentdate').val((new Date()).toISOString().split('T')[0]);
        $('#form-status').val('');
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
