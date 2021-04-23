var xmlr = new XMLHttpRequest();

$(function(){
    $('.add-to-cart').click(function() {
        var nombre = $('h2.title').text();
        var precio = $('span.price:nth-child(3) > span:nth-child(1)').text();
        var cantidad = $('input').val();
        var producto_id = $('id').text();
        dict = {
           "nombre": nombre,
           "cantidad": cantidad,
           "precio": precio,
           "producto_id": producto_id,
        };
        $.ajax({
            url:"/addCarrito",
            type:"GET",
            data: dict,
            success: function(response){
                console.log(response);
                reloadCarrito()
            },
            error: function(error){
                console.log(error);
            },
        })
        })

    $(document).on('click', '.cart-delete', function() {
//    $('.cart-delete').click(function() {
        $(this).parents('.cart-info')
        dict = {
           "nombre": $(this).parents('.cart-info').find('h5').text()
        };
        $.ajax({
            url:"/delCarrito",
            type:"GET",
            data: dict,
            success: function(response){
                console.log(response);
                reloadCarrito()
            },
            error: function(error){
                console.log(error);
            },
        })


    })


})

function reloadCarrito(){
//    window.location.reload();
    $('.cart-toggle > span:nth-child(2)').load(window.location.href + ' .cart-toggle > span:nth-child(2)')
    $('.all-cart-product').load(window.location.href + ' .all-cart-product')
//    $('.mini-cart-brief').load(window.location.href + ' .mini-cart-brief')

//    $('#lenCarrito').load(window.location.href + ' #lenCarrito')
//    $('.header-cart .float-left').load(window.location.href + ' .header-cart .float-left');
//    $('.all-cart-product .clearfix').load(window.location.href + ' .all-cart-product .clearfix');
//
//    $('a.cart-toggle span')[0].innerText = carrito.len;
//    $('.cart-items p span')[0].innerHTML = carrito.len + " Productos";
//
//    for (var i = 0; i < $('.all-cart-product .clearfix').length; i++) {
//      var a = $('.all-cart-product .clearfix')[i]
//     console.log(a);
     // more statements


}