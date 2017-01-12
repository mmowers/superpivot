$(document).ready(function(){
    $('body').on('click', '[id^=modelid_x_dropdown]', function(){
        $('div[id^=modelid_x_drop_]').toggle();
    });
    $('body').on('click', '[id^=modelid_y_dropdown]', function(){
        $('div[id^=modelid_y_drop_]').toggle();
    });
    $('body').on('click', '[id^=modelid_series_dropdown]', function(){
        $('div[id^=modelid_series_drop_]').toggle();
    });
    $('body').on('click', '[id^=modelid_explode_dropdown]', function(){
        $('div[id^=modelid_explode_drop_]').toggle();
    });
    $('body').on('click', '[id^=modelid_filters]', function(){
        $('[id^=modelid_heading_filter_]').toggle();
        $('[id^=modelid_update_button]').toggle();
        $('.select-all-none').hide();
        $('.bk-widget[id^=modelid_filter_]').hide();
    });
    $('body').on('click', '[id^=modelid_heading_filter_]', function(){
        if($(this).next('.select-all-none').length == 0){
            $(this).after('<div class="select-all-none"><span class="select-all select-opt">All</span>|<span class="select-none select-opt">None</span>');
        }else{
            $(this).next(".select-all-none").toggle();
        }
        $(this).next(".select-all-none").next(".bk-widget[id^=modelid_filter_]").toggle();
    });
    $('body').on('click', '[id^=modelid_adjust_plots]', function(){
        $('div[id^=modelid_adjust_plot_]').toggle();
    });
    $('body').on('click', '.select-opt', function(){
        var checked_bool = $(this).hasClass('select-all') ? true: false;
        $(this).parent().next('.bk-widget').find('.bk-bs-checkbox input').prop( "checked", checked_bool);
        $(this).parent().next('.bk-widget').find('.bk-bs-checkbox input').first().click();
        $(this).parent().next('.bk-widget').find('.bk-bs-checkbox input').first().click();
    });
    $('body').on('click', '.legend-header', function(){
        $(this).next('.legend-body').toggle();
    });
});