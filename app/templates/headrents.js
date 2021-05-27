$(document).ready(function(){
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
        $('#form-propaddr').val(dict.propaddr);
        $('#form-agent').val(dict.agent);
        $('#form-nextrentdate').val(dict.nextrentdate);
        if(dict.nextrentdate  == '')
        {
            $('#expand_next_rent_date').collapse('hide')
        }
        else
        {
            $('#expand_next_rent_date').collapse('show')
        }
        $('#form-status').val(dict.status);
    });
    $('.search-clear').click(function(e) {
        $('#form-rentcode').val('');
        $('#form-propaddr').val('');
        $('#form-agent').val('');
        $('#form-nextrentdate').val('');
        $('#expand_next_rent_date').collapse('hide')
        $('#form-status').val('');
    });
    $('.reset-date').click(function(e) {
        var date = new Date()
        date.setDate(date.getDate() + 35)
        $('#form-nextrentdate').val(date.toISOString().split('T')[0]);
    });
    //add or remove next rent date based on visibility of next rent date input
    $('#expand_next_rent_date').on('hidden.bs.collapse', function () {
        $('#form-nextrentdate').val('');
        $('.remove-date').removeClass('minus').addClass('plus');
    });
    $('#expand_next_rent_date').on('shown.bs.collapse', function () {
        if ($('#form-nextrentdate').val() == '')
        {
            var date = new Date()
            date.setDate(date.getDate() + 35)
            $('#form-nextrentdate').val(date.toISOString().split('T')[0]);
        }
        $('.remove-date').removeClass('plus').addClass('minus');
    });
});

