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
            // Reset all buttons, textareas, and associated elements to their default state
            editListBtns.forEach(otherBtn => {
                otherBtn.style.display = 'block';

                const otherWrapper = otherBtn.closest('.wrapper');
                const otherTextareaWrapper = otherWrapper.querySelector('#textarea-wrapper');
                const otherListName = otherWrapper.querySelector('h1#list-name');
                const otherListDesc = otherWrapper.querySelector('p#list-desc');

                if (otherTextareaWrapper) otherTextareaWrapper.style.display = 'none';
                if (otherListName) otherListName.style.display = 'block';
                if (otherListDesc) otherListDesc.style.display = 'block';
            });

            // Set the current button and associated elements
            btn.style.display = 'none';

            const wrapper = btn.closest('.wrapper');
            const textareaWrapper = wrapper.querySelector('#textarea-wrapper');
            const listName = wrapper.querySelector('h1#list-name');
            const listDesc = wrapper.querySelector('p#list-desc');

            if (textareaWrapper) textareaWrapper.style.display = 'flex';
            if (listName) listName.style.display = 'none';
            if (listDesc) listDesc.style.display = 'none';
        });
    });
})