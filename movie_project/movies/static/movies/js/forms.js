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


document.addEventListener('DOMContentLoaded', function() {
    const privacyBtns = document.querySelectorAll('#privacy-btn');

    privacyBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            privacyBtns.forEach(b => b.classList.remove('selected'));

            btn.classList.add('selected');

            btn.querySelector('input[type="radio"]').checked = true;
        })
    })

    const editListBtns = document.querySelectorAll('#edit-list-btn');
    editListBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            btn.style.display = 'none';

            const wrapper = btn.closest('.wrapper'); // target the btn's parent wrapper
            const textareaWrapper = wrapper.querySelector('#textarea-wrapper');

            textareaWrapper.style.display = 'flex';

            // ensure only the btn doesn't toggle visibility for listDesc and listName at the same time 
            // by adding wrapper queryselector
            const listDesc = wrapper.querySelector('p#list-desc'); 
            const listName = wrapper.querySelector('h1#list-name');

            if (listName) {
                listName.style.display = 'none'
            } else if (listDesc) {
                listDesc.style.display = 'none'
            }
        })
    })
})