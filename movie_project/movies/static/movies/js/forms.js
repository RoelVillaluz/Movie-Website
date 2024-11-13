$(document).ready(function() {
    $('#id_movies').select2({
        placeholder: "Select movies",
        allowClear: true,
        templateResult: function(data) {
            if (!data.id) { return data.text; } // Return plain text if no id
            var imgUrl = $(data.element).data('poster');
            var $container = $(
                '<span><img src="' + imgUrl + '" style="height: 60px; margin-right: 10px;" />' + data.text + '</span>'
            );
            return $container;
        },
        templateSelection: function(data) {
            return data.text; // Display movie title in the selection box
        }
    });
});


const privacyBtns = document.querySelectorAll('#privacy-btn');

privacyBtns.forEach(btn => {
    btn.addEventListener('click', function() {
        privacyBtns.forEach(b => b.classList.remove('selected'));

        btn.classList.add('selected');

        btn.querySelector('input[type="radio"]').checked = true;
    })
})