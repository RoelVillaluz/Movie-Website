$(document).ready(function () {
    $('#id_movies').select2({
        placeholder: "Select movies",
        allowClear: true,
        containerCssClass: 'custom-select2-container', // Custom class for container
        dropdownCssClass: 'custom-select2-dropdown',   // Custom class for dropdown
        selectionCssClass: 'custom-select2-selection', // Custom class for selection
        templateResult: function (data) {
            if (!data.id) { return data.text; } // Return plain text if no id
            var imgUrl = $(data.element).data('poster');
            var $container = $(
                '<span class="custom-select2-item"><img src="' + imgUrl + '" class="custom-select2-poster" />' + data.text + '</span>'
            );
            return $container;
        },
        templateSelection: function (data) {
            return data.text; // Display movie title in the selection box
        }
    });
});

