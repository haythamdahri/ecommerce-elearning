$(document).ready(function(){

    //$(".product-thumbnail").find('img').attr({'height':250, 'width':232})
    $("#more_brands").click(function(){
        $(".hidden_brands").slideDown(320);
        $(this).hide();
    });

    $('#loading-image').bind('ajaxStart', function(){
        $(this).show();
    }).bind('ajaxStop', function(){
        $(this).hide();
    });



});

    function showMoreShortDescription(more_desc_btn, short_description_id){
        $(".more-short-description"+short_description_id+" li").slideDown(320);
        $(more_desc_btn).hide();
    }
