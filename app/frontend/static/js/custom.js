/**
 * Create User by Ajax form submit
 */
$(document).ready(function() {
    $('.notification').delay(3000).fadeOut();
    $('.errorlist').delay(3000).fadeOut();
    showLoader('hide');
    check_is_guide();
    $("input[name='is_guide']").change(function(){
        check_is_guide();
    });
    $('#change-password').parsley() //parsley field validation on change password.
    $('#update-user').parsley() //parsley field validation on update user.
});

function check_is_guide(){
    is_guide = $('input[name=is_guide]:checked').val();
    if (is_guide == 1)
        {
            $('label[for="id_city"]').show();
            $("#id_city").show();
            $(".tm-tag").show();
            var tagApi = $(".tm-input").tagsManager();
            var tags = $("#id_city_hidden").val();
            var tagStr = tags.split(',');
             $.each(tagStr, function (index, value) {
                jQuery(".tm-input").tagsManager('pushTag',value);
             });
            jQuery(".tm-input").on('tm:splicing', function(e, tag) {
                $("#id_city_hidden").val($("#id_city_hidden").val().replace(tag+',', "").replace(tag,""));
            });

            jQuery(".typeahead").typeahead({
                name: 'city',
                displayKey: 'name',
                source: function (query, result) {
                csrf = $("input[name=csrfmiddlewaretoken]").val();
                url = '/city-autocomplete';
                $.ajax({
                        url: url,
                        data: { search: query, csrfmiddlewaretoken: csrf },
                        dataType: "json",
                        type: "POST",
                        beforeSend: function () {
                            // add loader
                        },
                        success: function (data) {
                            result($.map(data, function (key, val) {
                                return key;
                            }));
                        },
                    });
                },
                afterSelect :function (item){
                    jQuery(".tm-input").on('tm:refresh', function(e, taglist) {
                        $('#id_city_hidden').val(taglist);
                    });
                    jQuery(".tm-input").on('tm:splicing', function(e, tag) {
                       $("#id_city_hidden").val($("#id_city_hidden").val().replace(tag, ""));
                    });
                }
            });
        }
        else
        {
            $('label[for="id_city"]').hide();
            $("#id_city").hide();
            $(".tm-tag").hide();
        }
}


function register_user_ajax(btn) {
    var form = $(btn).closest('form');

    if (form.parents('#sign-up-page').length > 0) {
        // If sign up page
        form.submit();
        return;
    }
    showLoader('show');
    jQuery.ajax({
        url : form.attr('action'),
        data:form.serialize(),
        type:'post',
        success:function (data) {
           showLoader('hide');
           form.find('.user-registration-form-fields').html(data);
        }
    });
}


function sign_in_user_ajax() {
    $('#user-sign-in-form').parsley()

    var form = $('#user-sign-in-form');
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
               $('.login-modal').html(data.html);
           }
        }
    });
}