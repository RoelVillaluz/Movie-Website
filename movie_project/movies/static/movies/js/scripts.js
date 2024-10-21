const menuBars = document.querySelector('.menu-bars');
const sidebar = document.querySelector('.sidebar');
const mainContent = document.querySelector('.main-content');

function toggleSidebar() {
    sidebar.classList.toggle('extended');
    mainContent.classList.toggle('blurred', sidebar.classList.contains('extended'));
}

menuBars.addEventListener('click', function(event) {
    event.stopPropagation();
    toggleSidebar();
});

document.addEventListener('click', function() {
    if (sidebar.classList.contains('extended')) {
        toggleSidebar();
    }
});

sidebar.addEventListener('click', function(event) {
    event.stopPropagation();
});


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
    if (currentIndex > 0) {
        currentIndex--;
        openModalWithImage()
    }
})

rightArrow.addEventListener('click', function() {
    if (currentIndex < allImages.length - 1) {
        currentIndex++;
        openModalWithImage()
    }
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

// Close modal when clicking outside of it
// document.addEventListener('click', function(event) {
//     const modal = document.querySelector('.image-modal')
//     if (imageModalContainer.classList.contains('visible') && 
//         !modal.contains(event.target) && 
//         !Array.from(clickablePics).includes(event.target)) {
//         toggleModal();
//     }
// });


const profileMenu = document.querySelector('.profile-menu');
const dropdownList = document.querySelector('.dropdown-list');

profileMenu.addEventListener('click', function() {
    dropdownList.style.display = dropdownList.style.display === 'block' ? 'none' : 'block';
})

document.addEventListener('click', function(e) {
    if (!profileMenu.contains(e.target)) {
        dropdownList.style.display = 'none';
    }
})


// bookmark watchlist button
document.querySelectorAll('.watchlist-btn').forEach(btn => {
    btn.onclick = function() {
        addToWatchlist(btn);
    }
});

// text and plus icon watchlist button
document.querySelectorAll('.add-watchlist-btn').forEach(btn => {
    btn.onclick = function() {
        addToWatchlist(btn, true);
    }
});

document.querySelectorAll('#like-btn').forEach(btn => {
    btn.onclick = function() {
        likeReview(btn)
    }
})

function addToWatchlist(element, containsText = false) {
    fetch(`/add_to_watchlist/${element.dataset.id}/`)
        .then(response => response.json())
        .then(data => {
            if (data.watchlisted) {
                element.classList.add('watchlisted');
                if (containsText) {
                    element.querySelector('span').textContent = 'Remove from Watchlist';
                    element.querySelector('button').textContent = '-';
                }
            showNotification('1 Item Added', data.movie_image);
            } else {
                element.classList.remove('watchlisted');
                if (containsText) {
                    element.querySelector('span').textContent = 'Add to Watchlist';
                    element.querySelector('button').textContent = '+';
                }
            showNotification('1 Item Removed', data.movie_image);   
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function likeReview(element) {
    fetch(`/like_review/${element.dataset.id}/`)
    .then(response => response.json())
    .then(data => {
        if (data.liked) {
            element.classList.add('liked')
        } else {
            element.classList.remove('liked')
        }
        const likeCountSpan = element.closest('.like-count').querySelector('span');
        likeCountSpan.textContent = `${data.like_count} likes`;
    })
    .catch(error => console.error("Error:", error));
}

const starContainer = document.querySelectorAll('.stars');
starContainer.forEach(container => {
    const rating = parseFloat(container.getAttribute('data-id'));

    for (let i = 0; i < rating; i++) {  // Change '>' to '<'
        const star = document.createElement('div');
        star.classList.add('star');
        container.insertBefore(star, container.querySelector('h4'));
    }
})


function showNotification(message, imageUrl) {
    let notification = document.querySelector('.notification');

    // Create the notification element if it doesn't exist
    if (!notification) {
        notification = document.createElement('div');
        notification.className = 'notification';
        document.body.appendChild(notification);
    }

    // Set the inner HTML for the notification content
    notification.innerHTML = `
        <div class="notification-content">
            <img src="${imageUrl}" alt="Movie Image" class="notification-image">
            <div class="notification-message">${message}</div>
        </div>
    `;

    // Display the notification
    notification.style.display = 'block';

    // Hide the notification after 3 seconds
    setTimeout(() => {
        notification.style.display = 'none';
    }, 3000);
}

const angleIcons = document.querySelectorAll('.filter-sidebar i');

angleIcons.forEach(icon => {
    icon.addEventListener('click', function() {
        const filterButtonList = this.parentElement.nextElementSibling;
        filterButtonList.classList.toggle('hidden');
        
        if (filterButtonList.classList.contains('hidden')) {
            this.className = 'fa-solid fa-plus';
        } else {
            this.className = 'fa-solid fa-minus';
        }
    });
});


const searchInput = document.querySelector('input[name="query"]');
const suggestionsBox = document.getElementById('suggestions-box');
const link = '/search_results/?query='

    searchInput.addEventListener('input', function() {
        const query = this.value;
        if (query.length > 1) {
            fetch(`/search-suggestions/?query=${query}`)
            .then(response => response.json())
            .then(data => {
                suggestionsBox.innerHTML = ''

                // Create header for movie search suggestions
                createCategoryHeader('Movies', data.movie_count, 'movies', query);

                // for movie suggestion item
                data.movies.forEach(movie => {
                    const movieSuggestion = createSuggestionItem('movie', movie) 
                    suggestionsBox.appendChild(movieSuggestion);
                });

                // Create header for actor search suggestions
                createCategoryHeader('Actors', data.actor_count, 'actors', query);

                // for actor suggestion item
                data.actors.forEach(actor => {
                    const actorSuggestion = createSuggestionItem('actor', actor) 
                    suggestionsBox.appendChild(actorSuggestion)
                });

                // Create header for director search suggestions
                createCategoryHeader('Directors', data.director_count, 'directors', query);

                // for actor suggestion item
                data.directors.forEach(director => {
                    const directorSuggestion = createSuggestionItem('director', director)
                    suggestionsBox.appendChild(directorSuggestion)
                })


                // footer for the suggestion box
                const SuggestionsBoxFooter =  document.createElement('div')
                SuggestionsBoxFooter.classList.add('suggestion-box-footer')
                SuggestionsBoxFooter.innerHTML = `
                    <a href="${link}${query}">See All Results for <span>"${query}"</span></a>
                `
                suggestionsBox.appendChild(SuggestionsBoxFooter)
            })
            suggestionsBox.style.display = 'block';
        } else {
            suggestionsBox.style.display = 'none'
        }
    });

    function createCategoryHeader(category, itemCount, filter, query) {
        const header = document.createElement('div');
        header.classList.add('suggestions-header');
        header.innerHTML = 
        `<div style="display:flex; align-items:center;">
            <p>${category}</p>
            <span class="count">${itemCount}</span>
        </div>
        <div style="display:flex; align-items:center;">
            <a href="${link}${query}&filter=${filter}" class="view-all">View All</a>
            <i class="fa-solid fa-angle-right"></i>
        </div>
        `
        suggestionsBox.appendChild(header);
    }

    function createSuggestionItem(type, item) {
        const suggestionDiv = document.createElement('div');
        suggestionDiv.classList.add('suggestion-item');
    
        let itemContent = '';
    
        if (type === 'movie') {
            itemContent = `
                <a href="/movies/${item.id}">
                    <div class="image movie-image">
                        <img src="${item.poster_path}" alt="${item.title}">
                    </div>
                    <div class="details">
                        <h3>${item.title}</h3>
                        <p>${item.year}</p>
                        <div class="tags">
                            <div class="genre-tag">${item.genre}</div>
                            <div class="rating-tag">
                                <i class="fa-solid fa-star"></i>
                                ${item.avg_rating.toFixed(2)}
                            </div>
                        </div>
                    </div>
                </a>
            `;
        } else if (type === 'actor') {
            itemContent = `
                <a href="/actors/${item.id}">
                    <div class="image actor-image">
                        <img src="${item.image}" alt="${item.name}">
                    </div>
                    <div class="details">
                        <h3>${item.name}</h3>
                        <h4>${item.most_popular_movie}</h4>
                    </div>
                </a>
            `;
        } else if (type === 'director') {
            itemContent = `
                <a href="/directors/${item.id}">
                    <div class="image actor-image">
                        <img src="${item.image}" alt="${item.name}">
                    </div>
                    <div class="details">
                        <h3>${item.name}</h3>
                        <h4>${item.most_popular_movie}</h4>
                    </div>
                </a>
            `;
        }
    
        suggestionDiv.innerHTML = itemContent;
        return suggestionDiv;
    }

    document.addEventListener('click', function(event) {
        if (!searchInput.contains(event.target) && !suggestionsBox.contains(event.target)) {
            suggestionsBox.style.display = 'none';
        }
    });

document.addEventListener('DOMContentLoaded', () => {
    const layoutButtons = document.querySelectorAll('.layout-buttons i');

    layoutButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const viewMode = btn.getAttribute('data-view');
            const urlParams = new URLSearchParams(window.location.search);

            // Set or update the view parameter
            urlParams.set('view', viewMode);

            // Keep existing filter parameters
            document.querySelectorAll('.filter-checkbox').forEach(cb => {
                if (cb.checked) {
                    urlParams.append(cb.name, cb.value);
                }
            });

            // Redirect to the new URL with updated view and filters
            window.location.search = urlParams.toString();
        });
    });
});
      
document.addEventListener('DOMContentLoaded', () => {
    // Radio button event listener
    const radioBtns = document.querySelectorAll('input[type="radio"]');
    radioBtns.forEach(btn => {
        btn.addEventListener('change', function() {
            this.form.submit()
        });
    });

    // Sorting form submission
    const sortForm = document.querySelector('.sort-form');
    const sortSelect = document.querySelector('.sort-form select');

    if (sortForm && sortSelect) {
        sortSelect.addEventListener('change', function() {
            sortForm.submit();
        });
    }

    // Checkbox event listener
    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    
    checkboxes.forEach(box => {
        box.addEventListener('click', function(event) {
            // Only prevent default behavior for specific cases
            if (this.checked) {
                event.preventDefault(); // Prevent default checkbox behavior
            }
            const parentForm = this.closest('form');
            if (parentForm) {
                parentForm.submit();
            }
        });
    });
});

document.getElementById('list-view-btn').addEventListener('click', function() {
    console.log("List view button clicked");
    window.location.search = '?view=list';
});

document.getElementById('grid-view-btn').addEventListener('click', function() {
    console.log("Grid view button clicked");
    window.location.search = '?view=grid';
});

window.onload = function() {
    const params = new URLSearchParams(window.location.search);
    const viewMode = params.get('view') || 'list';

    const watchlist = document.querySelector('.watchlist-container ol')

    console.log("Current view mode:", viewMode);

    if (viewMode === 'grid') {
        document.getElementById('grid-view-btn').classList.add('active');
        watchlist.classList.add('grid')
    } else {
        document.getElementById('list-view-btn').classList.add('active');
        watchlist.classList.remove('grid')
    }
};