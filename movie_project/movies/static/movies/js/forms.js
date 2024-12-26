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


document.addEventListener('DOMContentLoaded', function() {
    // Function to toggle the textarea visibility and handle the UI changes
    function toggleTextArea(btn) {
        // Reset all buttons, textareas, and associated elements to their default state
        const editListBtns = document.querySelectorAll('#edit-list-btn');
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
        const wrapper = btn.closest('.wrapper');
        const textareaWrapper = wrapper.querySelector('#textarea-wrapper');
        const listName = wrapper.querySelector('h1#list-name');
        const listDesc = wrapper.querySelector('p#list-desc');
    
        if (textareaWrapper) textareaWrapper.style.display = 'flex';
        if (listName) listName.style.display = 'none';
        if (listDesc) listDesc.style.display = 'none';
    
        const cancelBtn = wrapper.querySelector('button[type="button"]');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                textareaWrapper.style.display = 'none';
                if (listName) listName.style.display = 'block';
                if (listDesc) listDesc.style.display = 'block';
                // Don't hide the edit button here, leave it visible
                btn.style.display = 'block';
            });
        }
    }
    

    // Attach the toggleTextArea function to each edit button
    const editListBtns = document.querySelectorAll('#edit-list-btn');
    editListBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            toggleTextArea(btn);
        });
    });

    // Handle privacy button selection
    const privacyBtns = document.querySelectorAll('#privacy-btn');
    privacyBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            privacyBtns.forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');
            btn.querySelector('input[type="radio"]').checked = true;
        });
    });

    const submitBtns = document.querySelectorAll('button[type="submit"]');
    submitBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            toggleTextArea(btn)
        })
    })
});
