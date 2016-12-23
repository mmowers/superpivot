$(document).ready(function(){
    $('body').on('click', '#modelid_filters', function(){
        $('[id$=_filter_heading]').toggle();
        $('.select-all-none').hide();
        $('.bk-widget[id$=_dropboxes]').hide();
    });
    $('body').on('click', '[id$=_filter_heading]', function(){
        if($(this).next('.select-all-none').length == 0){
            $(this).after('<div class="select-all-none"><span class="select-all select-opt">All</span>|<span class="select-none select-opt">None</span>');
        }else{
            $(this).next(".select-all-none").toggle();
        }
        $(this).next(".select-all-none").next(".bk-widget[id$=_dropboxes]").toggle();
    });
    $('body').on('click', '#modelid_adjust_plots', function(){
        $('div[id$=_adjust]').toggle();
    });
    $('body').on('click', '.select-opt', function(){
        var checked_bool = $(this).hasClass('select-all') ? true: false;
        $(this).parent().next('.bk-widget').find('.bk-bs-checkbox input').prop( "checked", checked_bool);
        $(this).parent().next('.bk-widget').find('.bk-bs-checkbox input').first().click();
        $(this).parent().next('.bk-widget').find('.bk-bs-checkbox input').first().click();
    });
});