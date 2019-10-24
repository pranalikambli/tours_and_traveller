$(function(){

    function fetchaccessroleData(url, params) {
            // Call the backend
        $.get(url, params).done(function(data){
            // Put the data into target div
            $(".admin").attr("disabled", false);
             $.each(data, function(k, v) {
                $.each(v, function(k1, v1) {
                    var d = k1+'_'+v1
                    if ( params.user == params.admin_id )
                    {
                        if (d == 'access_rights_1')
                        {
                            $("#"+d).prop("checked", true);
                            $("#"+d).attr("disabled", true);
                            $(".admin").attr("disabled", true);
                        }
                        else
                        {
                            $("#"+d).prop("checked", true);
                        }
                    }
                    else
                    {
                        $("#"+d).prop("checked", true);
                    }
                });
            });
        });
    };

    var user = $('#role_id').val();
    var url = '/get-role-json'; // Backend url
    var admin_id = $('#admin_id').val();
    var params = {'user': user,'admin_id':admin_id}; // is_assigned value
    fetchaccessroleData(url, params); // Backend call for filtered data
});