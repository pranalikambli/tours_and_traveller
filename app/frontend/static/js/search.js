$(function () {
	$('input.typeahead').typeahead({
	    source:  function (query, result) {
        	csrf = $("input[name=csrfmiddlewaretoken]").val();
            url = '/search-autocomplete';
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
                        return key.city + ', ' + key.state + ', '+ key.country;
                    }));
                },
            });
	    },
	    afterSelect: function (item) {
            var get_city=item.split(",");
            get_city= get_city[0];
            $('#search').val(get_city);
        }
	});
});