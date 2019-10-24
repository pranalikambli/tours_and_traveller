$(document).ready(function(){

    selected_star = $('#guide_rating').val();
    for (i = 1; i <= selected_star; i++) {
        $('li[data-id='+i+']').addClass('selected');
    }

    /* 1. Visualizing things on Hover - See next part for action on click */
    $('#stars li').on('mouseover', function(){
        var onStar = parseInt($(this).data('id'), 10); // The star currently mouse on

    // Now highlight all the stars that's not after the current hovered star
    $(this).parent().children('li.star').each(function(e){
        if (e < onStar) {
            $(this).addClass('hover');
        }
        else {
            $(this).removeClass('hover');
        }
    });

    }).on('mouseout', function(){
        $(this).parent().children('li.star').each(function(e){
            $(this).removeClass('hover');
        });
    });


    /* 2. Action to perform on click */
    $('#stars li').on('click', function(){
        var onStar = parseInt($(this).data('id'), 10); // The star currently selected
        var stars = $(this).parent().children('li.star');

        for (i = 0; i < stars.length; i++) {
            $(stars[i]).removeClass('selected');
        }

        for (i = 0; i < onStar; i++) {
            $(stars[i]).addClass('selected');
        }

    var ratingValue = parseInt($('#stars li.selected').last().data('id'), 10);
    var guideId = parseInt($('#stars li.selected').last().data('value'), 10);
    var msg = "";
    url = '/guide-rating';
        $.ajax({
            url: url,
            data: { ratingValue: ratingValue, guideId: guideId },
            dataType: "json",
            type: "GET",
            beforeSend: function () {
                // add loader
            },
            success: function (data) {
                //hide loader
            },
            error: function (data) { // if error occurred
                 alert("Error occurred.please try again");
            }
        });
});

    var modal = {};
    modal.hide = function () {
        $('.modal').fadeOut();
        $("html, body").removeClass("hid-body");
    };
    $('.make-msg-modal').on("click", function (e) {
        $('.modal').show();
        $("html, body").addClass("hid-body");
    });
    $('.close-modal').on("click", function () {
        $('.modal').hide();
    });

});

function make_message_ajax() {
    $('#make-msg').parsley()

    var form = $('#make-msg');
    showLoader('show');
    jQuery.ajax({
        url : form.attr('action'),
        data:form.serialize(),
        dataType:'json',
        type:'post',
        success:function (data) {
           showLoader('hide');
           if (data.error == 0) {
                location.reload();
           } else {
               $('.make_msg_modal').html(data.html);
           }
        }
    });
}