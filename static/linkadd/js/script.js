$(document).ready(function(){

    function resetBtnClick(){
        $('#ajax-res-success').hide();
        $('#ajax-res-error').hide();
        $('#add_to_wl').hide();
    }



    $(document).ajaxStart(function(){
        $('#loading').show();
        $(":button").attr("disabled",true);
    });
    $(document).ajaxStop(function(){
        $('#loading').hide();
        $(":button").attr("disabled",false);
    });
    $('#reset-btn').click(resetBtnClick);
    
    $('#url_form').submit(function(e){
        e.preventDefault();
        var serialisedData = $(this).serialize();
        $('#ajax-res-error').hide();
        $('#ajax-res-success').hide();
        $.ajax({
            type: 'POST',
            url: "add_link",
            data: serialisedData,
            success: function(data,status,xhr){
                var domain = data['domain'];
                var product_name = data['product_name'];
                var pic_url = data['product_pic_url'];
                var price = data['price_th'];
                var availability = data['availability'];
                var exists = data['exists'];
                $('#add_to_wl').show();
                $('#ajax-res-success').show();
                $('#ajax-res-error').hide();
                $('#product_img').attr("src",pic_url);
                $('.product-name').text(product_name);
                $('#product-availability').text(availability);
                if (exists){
                    $("#add_to_wl").hide();
                    $("#item-exists").show();
                }
                else{
                    $("#add_to_wl").show();
                    $("#item-exists").hide();
                }
                if (availability == 'In stock'){
                    $('#product-availability').attr("class","product-availability-instock");
                }
                else{
                    $('#product-availability').attr("class","product-availability-stock-out");
                }
                
                $('.product-price').html('&#8377;'+price);
            },
            error: function(response){
                console.log(response)
                var err = response;
                $('#ajax-res-error').show();
                $('#ajax-res-success').hide();

                $('.error-ajax').text(err.responseJSON['msg']);
            }
        })
    });
});