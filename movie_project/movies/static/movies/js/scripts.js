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

document.addEventListener('DOMContentLoaded', function() {
    const thumbnail = document.querySelector('.main-video-container .thumbnail');
    const video = document.querySelector('.main-video-container video');

    thumbnail.addEventListener('click', function() {
        thumbnail.style.display = 'none';  
        video.style.display = 'block';     
        video.play();                      
    });

    video.style.display = 'none'; // Start with the video hidden
});


const galleryImages = document.querySelectorAll('.gallery img')
galleryImages.forEach(image => {
    image.addEventListener('click', function() {
        const dataId = this.getAttribute('data-id')
        console.log(dataId)
    })
})

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

                // footer for the suggestion box
                const SuggestionsBoxFooter =  document.createElement('div')
                SuggestionsBoxFooter.classList.add('suggestion-box-footer')
                SuggestionsBoxFooter.innerHTML = `
                    <a href="${link}${query}">See All Results for <span>"${query}"</span></a>
                `
                suggestionsBox.appendChild(SuggestionsBoxFooter)
            })
            suggestionsBox.style.display = 'block';
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
        }
    
        suggestionDiv.innerHTML = itemContent;
        return suggestionDiv;
    }

    document.addEventListener('click', function(event) {
        if (!searchInput.contains(event.target) && !suggestionsBox.contains(event.target)) {
            suggestionsBox.style.display = 'none';
        }
    });