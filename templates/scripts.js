$(document).ready(function(){
    $('body').on('click', '#modelid_filters', function(){
        $('[id$=_filter_heading]').toggle();
    });
    $('body').on('click', '[id$=_heading]', function(){
        $(this).next().toggle();
    });
    $('body').on('click', '#modelid_adjust_plots', function(){
        $('div[id$=_adjust]').toggle();
    });
});