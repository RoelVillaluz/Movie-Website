const clickablePics = document.querySelectorAll('.clickable-pic');
const imageModalContainer = document.querySelector('.image-modal-container');
const modalImage = document.querySelector('.image-modal img');
const leftArrow = document.querySelector('.fa-chevron-left');
const rightArrow = document.querySelector('.fa-chevron-right');
const imageCountSpan = document.querySelector('.image-count');
const imageHeader = document.querySelector('.image-header');
const peopleContainer = document.querySelector('.people-in-image');
const closeImageModalBtn = document.querySelector('.image-modal .fa-solid.fa-xmark');

let currentIndex = 0;
let allImages = Array.from(clickablePics).map(pic => ({
    url: pic.dataset.image,
    name: pic.dataset.name
}))

clickablePics.forEach((pic, index) => {
    pic.addEventListener('click', function() {
        // Check if the clicked image has the 'last' class
        if (pic.classList.contains('last')) {
            // Get the URL from the data attribute and navigate to it
            const url = pic.getAttribute('data-url');
            window.location.href = url; // Navigate directly to the URL
        } else {
            currentIndex = index; // Update current index for other images
            openModalWithImage(); // Open modal for other images
        }
    });
});

if (leftArrow) {
    leftArrow.addEventListener('click', function() {
        prevImage()
    })
}

if (rightArrow) {
    rightArrow.addEventListener('click', function() {
    nextImage()
    })
}

if (closeImageModalBtn) {
    closeImageModalBtn.addEventListener('click', function() {
        toggleModal(imageModalContainer, true)
    })
}

document.addEventListener('keyup', function(event) {
    const modalElement = document.querySelector('.image-modal-container'); 
    const isModalVisible = modalElement.classList.contains('visible');
    
    if (isModalVisible) {
        switch(event.key) {
            case "ArrowLeft":
                prevImage();
                break;
            case "ArrowRight":
                nextImage();
                break;
        }
    }
});

function prevImage() {
    if (currentIndex === 0) {
        currentIndex = allImages.length - 1; 
    } else {
        currentIndex--;
    }
    imageHeader.innerHTML = ''
    peopleContainer.innerHTML = ''
    openModalWithImage();
}

function nextImage() {
    if (currentIndex < allImages.length - 1) {
        currentIndex++;
    } else if (currentIndex === allImages.length - 1) {
        currentIndex = 0
    }
    imageHeader.innerHTML = ''
    peopleContainer.innerHTML = ''
    openModalWithImage()
}

function openModalWithImage() {
    const imageUrl = allImages[currentIndex].url;
    const name = allImages[currentIndex].name;

    if (!imageModalContainer.classList.contains('visible')) {
        toggleModal(imageModalContainer);
    }

    // Update the image source and count.
    modalImage.src = imageUrl;
    imageCountSpan.textContent = `${currentIndex + 1} of ${allImages.length}`;

    fetch('/api/movie-images/')
    .then(response => response.json())
    .then(data => {
        const imageData = data.find(item => item.image_url === imageUrl);

        if (imageData) {
            const headerLink = document.createElement('a');
            imageHeader.innerHTML = '';

            if (imageData.type === 'movie') {
                headerLink.textContent = imageData.movie;
                headerLink.href = `/movies/${imageData.movie_id}`;
                const movieYear = document.createElement('span');
                movieYear.textContent = ` (${imageData.year})`;
                imageHeader.appendChild(headerLink);
                headerLink.insertAdjacentElement('afterend', movieYear);
            } else if (imageData.type === 'actor') {
                headerLink.textContent = imageData.name;
                headerLink.href = `/actors/${encodeURIComponent(imageData.person_id)}`;
                imageHeader.appendChild(headerLink);
            } else if (imageData.type === 'director') {
                headerLink.textContent = imageData.name;
                headerLink.href = `/directors/${encodeURIComponent(imageData.person_id)}`;
                imageHeader.appendChild(headerLink);
            }

            peopleContainer.innerHTML = '';

            imageData.people.forEach((person, index) => {
                const link = document.createElement('a');
                if (person.type === 'actor') {
                    link.href = `/people/actors/${encodeURIComponent(person.id)}`;
                } else if (person.type === 'director') {
                    link.href = `/people/directors/${encodeURIComponent(person.id)}`;
                }
                link.textContent = person.name;
                peopleContainer.appendChild(link);

                if (index < imageData.people.length - 1) {
                    const comma = document.createElement('span');
                    comma.textContent = ', ';
                    peopleContainer.appendChild(comma);
                }
            });

            // Add the edit link using the image's id
            const editLink = document.getElementById('edit-image-link')
            if (imageData.type === 'actor') {
                editLink.href =  `/people/actors/edit_image/${imageData.id}`
            } else if (imageData.type === 'directors') {
                editLink.href =  `/people/directors/edit_image/${imageData.id}`
            } else {
                editLink.href = `/movies/edit_image/${imageData.id}`
            }     

        } else {
            console.error('Image data not found for the given URL:', imageUrl);
        }
    })
    .catch(error => console.error('Error fetching image data:', error));
}

document.addEventListener('DOMContentLoaded', function() {
    const hideBtn = document.querySelector('.fa-angle-down');
    const detailsBtn = document.querySelector('.fa-solid.fa-circle-info');
    const overlay = document.querySelector('.overlay');

    function toggleOverlay() {
        if (overlay) {
            overlay.classList.toggle('hidden');

            // Toggle the visibility of the details button
            if (overlay.classList.contains('hidden')) {
                detailsBtn.classList.remove('hidden');
            } else {
                detailsBtn.classList.add('hidden');
            }
        }
    }

    if (hideBtn) {
        hideBtn.addEventListener('click', toggleOverlay);
    }

    if (detailsBtn) {
        detailsBtn.addEventListener('click', toggleOverlay);
    }
});

export function toggleModal(modalElement, closeOther = false) {
    // close other models once another is opened
    if (closeOther) {
        const otherModals = [document.querySelector('.image-modal-container')];
        otherModals.forEach(modal => {
            if (modal && modal !== modalElement) {
                modal.classList.remove('visible')
            }
        })
    }

    const isVisible = modalElement.classList.contains('visible')
    modalElement.classList.toggle('visible', !isVisible)

    // check if any modal is currently visible
    const anyModalVisible = document.querySelector('.image-form.visible') || 
                            document.querySelector('.image-modal-container.visible') ||
                            document.querySelector('.delete-image-form.visible') ||
                            document.querySelector('.form-modal.visible') ||
                            document.querySelector('.add-to-list-form.visible') ||
                            document.querySelector('.add-review-form.visible');

    document.body.classList.toggle('blurry', !!anyModalVisible);

    const nav = document.querySelector('nav');
    nav.style.display = anyModalVisible ? 'none' : 'flex';
}


document.addEventListener("DOMContentLoaded", function() {
    const imageResetBtn = document.querySelector('.form-actions button[type="reset"]');
    const imageNameDisplay = document.getElementById('image-name');
    const imagePreview = document.getElementById('image-preview');
    const uploadIcon = document.querySelector('.fa-solid.fa-upload');
    const imageFormModal = document.querySelector('.image-form');

    const addPhotoBtn = document.querySelector('.add-photo-btn');
    if (addPhotoBtn) {
        addPhotoBtn.addEventListener('click', function() {
            toggleModal(imageFormModal, true);
        });
    }

    const editProfilePhotoBtn = document.getElementById('edit-profile-photo-btn');
    if (editProfilePhotoBtn) {
        editProfilePhotoBtn.addEventListener('click', function () {
            toggleModal(imageFormModal, true);
        });
    }

    const closeFormButtons = document.querySelectorAll('#close-form-btn');
    if (closeFormButtons.length > 0) {
        closeFormButtons.forEach(closeButton => {
            closeButton.addEventListener('click', function() {
                const modalElement = closeButton.closest('.image-form') ||
                                     closeButton.closest('.add-to-list-form') ||
                                     closeButton.closest('.add-review-form');
                toggleModal(modalElement, true);
            });
        });
    }

    const closeImageModalBtn = document.querySelector('.close-modal-btn');
   if (closeImageModalBtn) {
        closeImageModalBtn.addEventListener('click', () => {
            toggleModal(imageModalContainer, true)
        })
   }

    const imageBox = document.querySelector('.image-box');
    if (imageBox) {
        imageBox.addEventListener('click', function() {
            const fileInput = document.querySelector('.upload-image input[type="file"]');
            if (fileInput) {
                fileInput.click();
            }
        });
    }

    const fileInput = document.querySelector('.upload-image input[type="file"]');
    if (fileInput) {
        fileInput.addEventListener('change', function(event) {
            const file = event.target.files[0];
            
            if (file) {
                const fileName = file.name;
                imageNameDisplay.textContent = `Image chosen: ${fileName}`;
                imageNameDisplay.style.display = 'block';
            
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.src = e.target.result;
                    imagePreview.style.display = 'block';
                };
                reader.readAsDataURL(file);
            
                uploadIcon.style.display = 'none';
            } else {
                resetImageForm(); // Reset UI if no file is chosen
            }
        });
    }

    if (imageResetBtn) {
        imageResetBtn.addEventListener('click', resetImageForm);
    }

    if (imageFormModal) {
        imageFormModal.addEventListener('submit', function() {
            setTimeout(() => {
                resetImageForm(); 
                toggleModal(imageFormModal); 
            }, 0);
        });
    }

    function resetImageForm() {
        if (fileInput) fileInput.value = ''; // Clear the file input

        if (imageNameDisplay) {
            imageNameDisplay.textContent = 'Upload an Image';
        }
        
        if (imagePreview) {
            imagePreview.src = ''; // Clear the preview image
            imagePreview.style.display = 'none';
        }
        if (uploadIcon) {
            uploadIcon.style.display = 'block';
        }        
    }

    const addPersonBtn = document.querySelector('.add-person-btn');
    const people = document.querySelector('.image-form .people');
    const backBtn = document.querySelector('.back-btn');
    const formHeader = document.querySelector('.image-form .header h2');
    const addPeopleSection = document.querySelector('.add-people-section');
    const imgEditPreview = document.querySelector('.image-form .image-container');

    if (addPersonBtn) {
        addPersonBtn.addEventListener('click', function() {
            if (imageBox) {
                imageBox.style.display = 'none';
            }
    
            if (people) {
                people.style.display = 'none'
            }
    
            if (addPeopleSection) {
                addPeopleSection.style.display = 'block'
            }
    
            if (imgEditPreview) {
                imgEditPreview.style.display = 'none';
            }       
             
            // update form header depending on whether add image or edit image form is visible
            if (formHeader.textContent === 'Edit Image') {
                formHeader.textContent = 'Edit people in image';
            } else {
                formHeader.textContent = 'Add people to image';
            }
        })
    
        backBtn.addEventListener('click', function() {
            if (imageBox) {
                imageBox.style.display = 'flex';
            }
    
            if (people) {
                people.style.display = 'flex'
            }
    
            if (addPeopleSection) {
                addPeopleSection.style.display = 'none'
            }
    
            if (imgEditPreview) {
                imgEditPreview.style.display = 'block';
            }  
    
            // update form header depending on whether add image or edit image form is visible
            if (formHeader.textContent === 'Edit people in image') {
                formHeader.textContent = 'Edit Image';
            } else {
                formHeader.textContent = 'Add Image';
            }
        })
    }

    

    const formListItems = document.querySelectorAll('.add-people-section li, .choose-list-section li');
    let checkedCount = document.querySelectorAll(
        '.add-people-section input[type="checkbox"]:checked').length;

    formListItems.forEach((listItem) => {
        const checkbox = listItem.querySelector('input[type="checkbox"]');

        checkbox.addEventListener('click', function (event) {
            event.stopPropagation();
            if (checkbox.checked) {
                checkedCount++;
            } else {
                checkedCount--;
            }
            updateCheckedCount();
        });

        listItem.addEventListener('click', function (event) {
            if (event.target.tagName !== 'INPUT') {
                if (checkbox) {
                    checkbox.checked = !checkbox.checked;
                    if (checkbox.checked) {
                        checkedCount++;
                    } else {
                        checkedCount--;
                    }
                }
                updateCheckedCount();
            }
        });
    });

    function updateCheckedCount() {
        const addPersonHeader = document.querySelector('.add-people-section h3');
        if (addPersonHeader) {
            if (checkedCount === 0) {
                if (addPersonHeader) addPersonHeader.textContent = `Select from cast and crew`;
            } else {
                if (addPersonHeader) addPersonHeader.textContent = `Select from cast and crew (${checkedCount})`;
            }
        }
    }

    // Initial call to update the checked count
    updateCheckedCount();


    // didn't use the toggleModal() function for these since i want the navbar to still appear for these ones
    const deleteImageBtn = document.getElementById('delete-image-btn');
    const deleteImageForm = document.querySelector('.image-form.delete');
    const cancelDeleteBtn = document.getElementById('cancel-delete-btn')
    deleteImageBtn?.addEventListener('click', () => {

        deleteImageForm.style.display = 'block'
        document.querySelector('.image-form.edit').style.display = 'none'
    })

    cancelDeleteBtn?.addEventListener('click', () => {
        deleteImageForm.style.display = 'none'
        document.querySelector('.image-form.edit').style.display = 'block'
    })
});