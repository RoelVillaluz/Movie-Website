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

let currentIndex = 0;
let allImages = Array.from(clickablePics).map(pic => ({
    url: pic.dataset.image,
    name: pic.dataset.name
}))

clickablePics.forEach((pic, index) => {
    pic.addEventListener('click', function() {
        currentIndex = index;
        openModalWithImage()
    })
})

leftArrow.addEventListener('click', function() {
    if (currentIndex === 0) {
        currentIndex = allImages.length - 1; 
    } else {
        currentIndex--;
    }
    openModalWithImage();
})

rightArrow.addEventListener('click', function() {
    if (currentIndex < allImages.length - 1) {
        currentIndex++;
    } else if (currentIndex === allImages.length - 1) {
        currentIndex = 0
    }
    openModalWithImage()
})

function openModalWithImage() {
    const imageUrl = allImages[currentIndex].url;
    const name = allImages[currentIndex].name;

    if (!imageModalContainer.classList.contains('visible')) {
        toggleModal();
    }

    // Update the image source and count.
    modalImage.src = imageUrl;
    imageCountSpan.textContent = `${currentIndex + 1} of ${allImages.length}`;

    fetch('/api/movie-images/')
        .then(response => response.json())
        .then(data => {
            const imageData = data.find(item => item.image_url === imageUrl);

            if (imageData) {
                const imageHeader = document.querySelector('.image-header');
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

                const peopleContainer = document.querySelector('.people-in-image');
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

function toggleModal() {
    const isVisible = imageModalContainer.classList.contains('visible')
    imageModalContainer.classList.toggle('visible', !isVisible)
    document.body.classList.toggle('blurry', !isVisible);

    const nav = document.querySelector('nav');
    nav.style.display = (nav.style.display === 'none') ? 'flex': 'none';
}