const galleryImages = document.querySelectorAll('.gallery img')
galleryImages.forEach(image => {
    image.addEventListener('click', function() {
        const dataId = this.getAttribute('data-id')
        console.log(dataId)
    })
})

const clickablePics = document.querySelectorAll('.clickable-pic');
const imageModalContainer = document.querySelector('.image-modal-container');
const modalImage = document.querySelector('.image-modal img');
const leftArrow = document.querySelector('.fa-chevron-left');
const rightArrow = document.querySelector('.fa-chevron-right');
const imageCountSpan = document.querySelector('.image-count');
const imageHeader = document.querySelector('.image-header');
const peopleContainer = document.querySelector('.people-in-image');

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

leftArrow.addEventListener('click', function() {
    prevImage()
})

rightArrow.addEventListener('click', function() {
    nextImage()
})

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

                // Iterate over the people and create links for each if available
                imageData.people.forEach((person, index) => {
                    const link = document.createElement('a');
                    if (person.type === 'actor') {
                        link.href = `/actors/${encodeURIComponent(person.id)}`;
                    } else if (person.type === 'director') {
                        link.href = `/directors/${encodeURIComponent(person.id)}`;
                    }
                    link.textContent = person.name;
                    peopleContainer.appendChild(link);

                    // Add a comma between names except for the last one
                    if (index < imageData.people.length - 1) {
                        const comma = document.createElement('span');
                        comma.textContent = ', ';
                        peopleContainer.appendChild(comma);
                    }
                });
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

function toggleModal(modalElement) {
    const isVisible = modalElement.classList.contains('visible')
    modalElement.classList.toggle('visible', !isVisible)
    document.body.classList.toggle('blurry', !isVisible);

    const nav = document.querySelector('nav');
    nav.style.display = (nav.style.display === 'none') ? 'flex': 'none';
}

const imageFormModal = document.querySelector('.image-form')


document.querySelector('.add-photo-btn').addEventListener('click', function() {
    toggleModal(imageFormModal);
});

document.querySelector('.image-form i').addEventListener('click', function() {
    toggleModal(imageFormModal);
});


document.querySelector('.image-box').addEventListener('click', function() {
    document.querySelector('.upload-image input[type="file"]').click();
});

const imageResetBtn = document.querySelector('.form-actions button[type="reset"]');
const imageNameDisplay = document.getElementById('image-name');
const imagePreview = document.getElementById('image-preview');
const uploadIcon = document.querySelector('.fa-solid.fa-upload');

document.querySelector('.upload-image input[type="file"]').addEventListener('change', function(event) {
    const fileInput = event.target;

    if (fileInput.files.length > 0) {
        const file = fileInput.files[0];
        const fileName = file.name;
        imageNameDisplay.textContent = `Image chosen: ${fileName}`;
        imageNameDisplay.style.display = 'block'; 

        const reader = new FileReader();
        reader.onload = function(e) {
            imagePreview.src = e.target.result;
            imagePreview.style.display = 'block';
        }
        reader.readAsDataURL(file)

        uploadIcon.style.display = 'none'
    } else {
        imageNameDisplay.style.display = 'none'; 
        imagePreview.style.display = 'none'
        uploadIcon.style.display = 'block'
    }
});

imageResetBtn.addEventListener('click', function(event) {
    const fileInput = event.target;

    fileInput.value = ''
    imageNameDisplay.textContent = 'Upload an Image'; 
    imagePreview.style.display = 'none'
    uploadIcon.style.display = 'block';
})


const addPersonBtn = document.querySelector('.add-person-btn');
const people = document.querySelector('.image-form .people');
const backBtn = document.querySelector('.back-btn')
const formHeader = document.querySelector('.image-form .header h2')
const addPeopleSection = document.querySelector('.add-people-section')

addPersonBtn.addEventListener('click', function() {
    const imageBox = document.querySelector('.image-box');

    imageBox.style.display = 'none';
    people.style.display = 'none'
    addPeopleSection.style.display = 'block'

    formHeader.textContent = 'Add people to image';
})

backBtn.addEventListener('click', function() {
    const imageBox = document.querySelector('.image-box');

    imageBox.style.display = 'flex';
    people.style.display = 'flex'
    addPeopleSection.style.display = 'none'

    formHeader.textContent = 'Add Image';
})

const personListItems = document.querySelectorAll('.add-people-section li');
let checkedCount = 0;

personListItems.forEach((listItem) =>  {
    const checkbox = listItem.querySelector('input[type="checkbox"]');

    checkbox.addEventListener('click', function(event) {
        event.stopPropagation()
        if (checkbox.checked) {
            checkedCount ++;
        } else {
            checkedCount --;
        }
        updateCheckedCount()
    })

    listItem.addEventListener('click', function(event) {
        if (event.target.tagName != 'INPUT') {
            if (checkbox) {
                checkbox.checked = !checkbox.checked;
                if (checkbox.checked) {
                    checkedCount ++;
                } else {
                    checkedCount --;
                }
            }
            updateCheckedCount()
        }
    })
})

function updateCheckedCount() {
    const checkedCountHeader = document.querySelector('.add-people-section h3');
        if (checkedCount == 0) {
            checkedCountHeader.textContent = `Select from cast and crew`
        } else {
            checkedCountHeader.textContent = `Select from cast and crew (${checkedCount})`
        }
}