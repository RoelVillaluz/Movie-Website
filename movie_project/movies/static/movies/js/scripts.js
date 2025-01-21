import { toggleModal } from "./imageGallery.js";

document.addEventListener('DOMContentLoaded', () => {
    // Menu toggle
    const menuBars = document.querySelector('.menu-bars');
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    if (menuBars && sidebar && mainContent) {
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
    }

    // Profile menu dropdown
    const profileMenu = document.querySelector('.profile-menu');
    const dropdownList = document.querySelector('.dropdown-list');
    if (profileMenu && dropdownList) {
        profileMenu.addEventListener('click', function() {
            dropdownList.style.display = dropdownList.style.display === 'block' ? 'none' : 'block';
        });

        document.addEventListener('click', function(e) {
            if (!profileMenu.contains(e.target)) {
                dropdownList.style.display = 'none';
            }
        });
    }

    function initializeActions() {
        // Watchlist buttons
        document.querySelectorAll('#watchlist-btn').forEach(btn => {
            btn.addEventListener('click', () => addToWatchlist(btn)) 
        });

        // Text and plus icon watchlist button
        document.querySelectorAll('.add-watchlist-btn').forEach(btn => {
            btn.addEventListener('click', () => addToWatchlist(btn, true))
        });

        // Like button
        document.querySelectorAll('#like-btn').forEach(btn => {
            btn.addEventListener('click', () => likeReview(btn))
        });

        // add to watched movies button
        document.querySelectorAll('#watched-movie-btn').forEach(btn => {
            btn.addEventListener('click', () => addToWatchedMovies(btn))
        })

        // toggle visibility for other card actions
        document.querySelectorAll('#other-actions-btn').forEach(btn => {
            btn.addEventListener('click', () => showOtherActions(btn))
        })
        
        // add titles to favorites
        document.querySelectorAll('#add-to-favorites-btn').forEach(btn => {
            btn.addEventListener('click', () => addToFavorites(btn))
        });

        // follow and unfollow
        document.querySelectorAll('.follow-btn').forEach(btn => {
            btn.addEventListener('click', () => toggleFollow(btn))
        })

        // create a review
        document.querySelectorAll('#add-review-btn').forEach(btn => {
            btn.addEventListener('click', () => addReview(btn ))
        })

        // add titles to list
        const cardFormButtons = document.querySelectorAll("#add-to-list-btn, #add-review-btn");
        const addToListForm = document.querySelector('.add-to-list-form');
        const addReviewForm = document.querySelector('.add-review-form');

        cardFormButtons.forEach(button => {
            button.addEventListener('click', function () {
                const card = button.closest('.card');
                const movieId = card.dataset.id;
                const movieTitle = card.dataset.title;
                const movieYear = card.dataset.year;

                if (button.id === 'add-to-list-btn') {
                    // Handle "Add to List" logic
                    const movieToAddElement = addToListForm.querySelector('p');
                    movieToAddElement.textContent = `${movieTitle} (${movieYear})`;

                    const hiddenMovieIdInput = addToListForm.querySelector('#movie-id-input');
                    hiddenMovieIdInput.value = movieId;

                    const moviePosterElement = card.querySelector('.image img');
                    const modalPosterElement = addToListForm.querySelector('.poster');
                    modalPosterElement.src = moviePosterElement.src;

                    const listItems = addToListForm.querySelectorAll('li');
                    listItems.forEach(item => {
                        const listItemIds = Array.from(item.querySelectorAll('[data-id]')).map(el => el.dataset.id);
                        const checkbox = item.querySelector('input[type="checkbox"]');

                        if (listItemIds.includes(movieId)) {
                            checkbox.checked = true;
                            checkbox.dataset.currentlyInList = "true";
                        } else {
                            checkbox.checked = false;
                            checkbox.dataset.currentlyInList = "false";
                        }
                    });

                    // Open "Add to List" modal
                    toggleModal(addToListForm, true);
                } else if (button.id === 'add-review-btn') {
                    // Handle "Add Review" logic
                    const movieToReviewElement = addReviewForm.querySelector('p');
                    movieToReviewElement.textContent = `${movieTitle} (${movieYear})`;

                    const hiddenMovieIdInput = addReviewForm.querySelector('#movie-id-input');
                    hiddenMovieIdInput.value = movieId;

                    const moviePosterElement = card.querySelector('.image img');
                    const modalPosterElement = addReviewForm.querySelector('.poster');
                    modalPosterElement.src = moviePosterElement.src;

                    // Open "Add Review" modal
                    toggleModal(addReviewForm, true);
                }
            });
        });

        if (addToListForm) {
            addToListForm.addEventListener("submit", function (event) {
                event.preventDefault();
            
                const movieId = addToListForm.querySelector("#movie-id-input").value;
            
                // Get selected list checkboxes
                const listCheckBoxes = document.querySelectorAll(
                    ".choose-list-section input[type='checkbox']"
                );
    
                const addListIds = Array.from(listCheckBoxes)
                    .filter((checkbox) => checkbox.checked && checkbox.dataset.currentlyInList === "false")
                    .map((checkbox) => checkbox.dataset.id)
    
                const removeListIds = Array.from(listCheckBoxes)
                    .filter((checkbox) => !checkbox.checked && checkbox.dataset.currentlyInList === "true")
                    .map((checkbox) => checkbox.dataset.id)
            
                // Add this movie to these lists
                addOrRemoveFromList(movieId, addListIds, "add");
    
                // remove this movie from these lists
                addOrRemoveFromList(movieId, removeListIds, "remove")
            
                // Close the modal after submission
                toggleModal(addToListForm, false);                
            });
        }

        if (addReviewForm) {
            addReviewForm.addEventListener('submit', function(event) {
                event.preventDefault();
                const movieId = addReviewForm.querySelector("#movie-id-input");
                movieId.dataset.id = movieId.value;
                
                addReview(movieId)
                toggleModal(addReviewForm, false)
            })
        }

    }

    initializeActions()

    // ensure event listeners for card actions are reinitialized after DOM is updated
    document.addEventListener('htmx:afterSwap', function() {
        initializeActions()
    })

    function addToWatchlist(element, containsText = false) {
        const card = element.closest('.card');
        fetch(`/add_to_watchlist/${element.dataset.id}/`)
            .then(response => response.json())
            .then(data => {
                if (data.watchlisted) {
                    element.classList.add('watchlisted');
                    if (containsText) {
                        element.querySelector('span').textContent = 'Remove from Watchlist';
                        element.querySelector('button').textContent = '-';
                    }
                    showNotification('Added to watchlist', data.movie_image);
                } else {
                    element.classList.remove('watchlisted');
                    if (containsText) {
                        element.querySelector('span').textContent = 'Add to Watchlist';
                        element.querySelector('button').textContent = '+';
                    }
                    showNotification('Removed from watchlist', data.movie_image);
                }
   
                const watchedBtn = card.querySelector('.fa-eye')
                if (data.watched) {
                    watchedBtn.classList.add('watched');
                } else {
                    watchedBtn.classList.remove('watched');
                }
            })
            .catch(error => {
                console.error('Error:', error);
            });
   }
   

    function addToWatchedMovies(element) {
        const card = element.closest('.card')
        fetch(`/users/add_to_watched_movies/${element.dataset.id}/`)
        .then(response => response.json())
        .then(data => {
            if (data.watched) {
                element.classList.add('watched');
                showNotification('Added to watched movies', data.movie_image);
            } else {
                element.classList.remove('watched');
                showNotification('Removed from watched movies', data.movie_image);
            }

            const watchlistBtn = card.querySelector('.fa-bookmark')
            if (data.watchlisted) {
                watchlistBtn.classList.add('watchlisted')
            } else {
                watchlistBtn.classList.remove('watchlisted')
            }
        });
    }

    function showOtherActions(element) {
        const card = element.closest('.card')
        const actions = card.querySelector('.actions')
        const otherActions = card.querySelector('.other-actions')
        
        otherActions.style.display = 'flex';
        actions.style.display = 'none';

        document.addEventListener('click', function(event) {
            if (!card.contains(event.target)) {
                otherActions.style.display = 'none';
                actions.style.display = 'flex';
            }
        })
    }

    function likeReview(element) {
        fetch(`/like_review/${element.dataset.id}/`)
            .then(response => response.json())
            .then(data => {
                if (data.liked) {
                    element.classList.add('liked');
                } else {
                    element.classList.remove('liked');
                }
                const likeCountSpan = element.closest('.like-count').querySelector('span');
                likeCountSpan.textContent = `${data.like_count} likes`;
            })
            .catch(error => console.error("Error:", error));
    }

    function addToFavorites(element) {
        fetch(`${window.location.origin}/users/add_to_favorites/${element.dataset.model}/${element.dataset.id}`)
        .then(response => response.json())
        .then(data => {
            if (data.favorited) {
                element.textContent = 'Remove from favorites';
                showNotification('Added to favorites', data.image)
            } else {
                element.textContent = 'Add to favorites';
                showNotification('Removed from favorites', data.image)
            }
        })
        .catch(error => console.error("Error: ", error));
    }

    function toggleFollow(element) {
        fetch(`/users/follow/${element.dataset.person_type}/${element.dataset.id}`)
            .then(response => response.json())
            .then(data => {
                const status = element.querySelector('span');
                const followIcon = element.querySelector('i')
                const followerCountText = document.getElementById('follower-count');
                const currentCount = parseInt(followerCountText.textContent, 10);
                
                if (data.followed) {
                    status.textContent = 'Unfollow';
                    followIcon.className = 'fa-solid fa-minus'
                    followerCountText.textContent = currentCount + 1;
                } else {
                    status.textContent = 'Follow';
                    followIcon.className = 'fa-solid fa-plus'
                    followerCountText.textContent = currentCount - 1;
                }
            })
            .catch(error => console.error("Error: ", error));
    }

    // Function to add or remove movies from lists
    function addOrRemoveFromList(movieId, listIds, action) {
        const fetchPromises = listIds.map((listId) => {
            const url = `/users/add_to_list/${listId}/${movieId}/`;
            return fetch(url, {
                method: "POST",
                headers: {
                    "X-CSRFToken": csrftoken,
                    "Content-Type": "application/json",
                },
            })
                .then((response) => {
                    if (!response.ok) {
                        throw new Error(`Failed to ${action} movie in list ${listId}`);
                    }
                    return response.json();
                })
                .then((data) => ({ success: true, data, listId }))
                .catch((error) => ({ success: false, error, listId }));
        });
    
        Promise.all(fetchPromises).then((results) => {
            let updatedListCount = 0;
    
            results.forEach((result) => {
                if (result.success) {
                    const { data, listId } = result;
    
                    // Target the specific list's container
                    const moviesInList = document.getElementById(`movies-in-list-${listId}`);
    
                    if (action === "add") {
                        // Add hidden input for the movie in the specific list's container
                        const newMovieInList = document.createElement("input");
                        newMovieInList.type = "hidden";
                        newMovieInList.setAttribute("data-id", data.movie.id);
                        moviesInList.appendChild(newMovieInList);
    
                        console.log(`Movie ${movieId} added to list ${listId}`);
                    } else if (action === "remove") {
                        // Remove hidden input for the movie from the specific list's container
                        const movieElements = moviesInList.querySelectorAll(`[data-id="${movieId}"]`);
                        movieElements.forEach((element) => element.remove());
    
                        console.log(`Movie ${movieId} removed from list ${listId}`);
                    }
    
                    updatedListCount++;
    
                    // Update the count for the specific list
                    const listMoviesCount = document.getElementById(`list-movies-count-${listId}`);
                    listMoviesCount.textContent = `${data.movie_count} Titles`;
                } else {
                    console.error(`Error updating list ${result.listId} for movie ${movieId}:`, result.error);
                }
            });
    
            // Show notification only for successful updates
            if (updatedListCount > 0) {
                const successfulUpdate = results.find((result) => result.success);
                showNotification(
                    `${updatedListCount} ${updatedListCount > 1 ? "lists" : "list"} changed`,
                    successfulUpdate ? successfulUpdate.data.movie.image : null
                );
            }
        });
    }

    function addReview(element) {
        const data = {
            description: document.getElementById('review-description').value,
            rating: document.querySelector('.star-container .rating-value').value
        }

        fetch(`/add_review/${element.dataset.id}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify(data)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Response was not ok')
            }
            return response.json()
        })
        .then(data => {
            console.log('success', data)
            showNotification(`Review created for ${data.movie.title}: ${data.rating} Stars`, data.movie.image)
        })
        .catch(error => {
            console.error('Error', error)
        })
    }

    const starContainer = document.querySelectorAll('.stars');
    starContainer.forEach(container => {
        const rating = parseFloat(container.getAttribute('data-id'));

        for (let i = 0; i < rating; i++) {
            const star = document.createElement('div');
            star.classList.add('star');
            container.insertBefore(star, container.querySelector('h4'));
        }
    });

    function generateStarContainer() {
        const starContainer = document.querySelector('.star-container');
        const starSpan = document.querySelector('.star-container span')

        for (let i = 0; i < 10; i++) {
            const star = document.createElement('i');
            star.classList.add('fa-regular', 'fa-star');
            star.dataset.index = i;

    
            if (starContainer && starSpan) {
                starContainer.insertBefore(star, starSpan);
            }
        }
    
        const stars = document.querySelectorAll('.star-container i');
        let isClicked = false; // Flag to check if a star has been clicked
    
        stars.forEach(star => {
            star.addEventListener('mouseover', () => {
                if (!isClicked) { // Only change on hover if no star has been clicked yet
                    const index = parseInt(star.dataset.index, 10);
                    stars.forEach((s, idx) => {
                        if (idx <= index) {
                            s.classList.remove('fa-regular');
                            s.classList.add('fa-solid');
                        } else {
                            s.classList.remove('fa-solid');
                            s.classList.add('fa-regular');
                        }
                    });
                }
            });
    
            star.addEventListener('click', () => {
                isClicked = true; // Set flag to true when clicked
                const index = parseInt(star.dataset.index, 10);
                stars.forEach((s, idx) => {
                    if (idx <= index) {
                        s.classList.remove('fa-regular');
                        s.classList.add('fa-solid');
                    } else {
                        s.classList.remove('fa-solid');
                        s.classList.add('fa-regular');
                    }
                });
                // add the value of the rating to the container to pass it to the form
                const ratingValue = starContainer.querySelector('.rating-value');
                ratingValue.value = index + 1;

                // update value of span to show your rating
                starSpan.textContent = ratingValue.value;
            });
        });
    }

    generateStarContainer()

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

    // Filter sidebar angle icons
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

    // Search input and suggestions
    const searchInput = document.querySelector('input[name="query"]');
    const suggestionsBox = document.getElementById('suggestions-box');
    const link = '/search_results/?query=';
    if (searchInput && suggestionsBox) {
        searchInput.addEventListener('input', function() {
            const query = this.value;
            if (query.length > 1) {
                fetch(`/search-suggestions/?query=${query}`)
                    .then(response => response.json())
                    .then(data => {
                        suggestionsBox.innerHTML = '';

                        // Create header for movie search suggestions
                        createCategoryHeader('Movies', data.movie_count, 'movies', query);

                        // for movie suggestion item
                        data.movies.forEach(movie => {
                            const movieSuggestion = createSuggestionItem('movie', movie);
                            suggestionsBox.appendChild(movieSuggestion);
                        });

                        // Create header for actor search suggestions
                        createCategoryHeader('Actors', data.actor_count, 'actors', query);

                        // for actor suggestion item
                        data.actors.forEach(actor => {
                            const actorSuggestion = createSuggestionItem('actor', actor);
                            suggestionsBox.appendChild(actorSuggestion);
                        });

                        // Create header for director search suggestions
                        createCategoryHeader('Directors', data.director_count, 'directors', query);

                        // for actor suggestion item
                        data.directors.forEach(director => {
                            const directorSuggestion = createSuggestionItem('director', director);
                            suggestionsBox.appendChild(directorSuggestion);
                        });

                        // footer for the suggestion box
                        const SuggestionsBoxFooter = document.createElement('div');
                        SuggestionsBoxFooter.classList.add('suggestion-box-footer');
                        SuggestionsBoxFooter.innerHTML = `
                            <a href="${link}${query}">See All Results for <span>"${query}"</span></a>
                        `;
                        suggestionsBox.appendChild(SuggestionsBoxFooter);
                    });
                suggestionsBox.style.display = 'block';
            } else {
                suggestionsBox.style.display = 'none';
            }
        });

        function createCategoryHeader(category, itemCount, filter, query) {
            const header = document.createElement('div');
            header.classList.add('suggestions-header');
            header.innerHTML = `
                <div style="display:flex; align-items:center;">
                    <p>${category}</p>
                    <span class="count">${itemCount}</span>
                </div>
                <div style="display:flex; align-items:center;">
                    <a href="${link}${query}&filter=${filter}" class="view-all">View All</a>
                    <i class="fa-solid fa-angle-right"></i>
                </div>
            `;
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
                    <a href="/people/actors/${item.id}">
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
                    <a href="/people/directors/${item.id}">
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

        document.addEventListener('click', function() {
            suggestionsBox.style.display = 'none';
        });
    }

    const layoutButtons = document.querySelectorAll('.layout-buttons i');
    if (layoutButtons) {
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
    }

    const toggleSliders = document.querySelectorAll('.slider-track');
    if (toggleSliders) {
        toggleSliders.forEach(slider => {
            slider.addEventListener('click', (event) => {
                const form = event.target.closest('form')
    
                if (!form) return; // Ensure the form exists
            
                const parentToggleSlider = slider.closest('.toggle-slider')
    
                const checkbox = parentToggleSlider.querySelector('input[type="checkbox"]')
                checkbox.checked = !checkbox.checked
         
                parentToggleSlider.classList.toggle('active', checkbox.checked)
        
                form.submit()
            })
        })
    }

    const radioBtns = document.querySelectorAll('.search-filters input[type="radio"]');
    if (radioBtns) {
        radioBtns.forEach(btn => {
            btn.addEventListener('change', function() {
                this.form.submit()
            });
        });
    }
});

// Sorting form submission
const sortForm = document.querySelector('.sort-form');
const sortSelect = document.querySelector('.sort-form select');

if (sortForm && sortSelect) {
    sortSelect.addEventListener('change', function() {
        sortForm.submit();
    });
}

const listViewBtn = document.getElementById('list-view-btn');
if (listViewBtn) {
    listViewBtn.addEventListener('click', function() {
        console.log("List view button clicked");
        window.location.search = '?view=list';
    });
}

const gridViewBtn = document.getElementById('grid-view-btn');
if (gridViewBtn) {
    gridViewBtn.addEventListener('click', function() {
        console.log("Grid view button clicked");
        window.location.search = '?view=grid';
    });
}

window.onload = function() {
    const params = new URLSearchParams(window.location.search);
    const viewMode = params.get('view') || 'list';

    const watchlist = document.querySelector('.list-container ol')

    console.log("Current view mode:", viewMode);

    if (viewMode === 'grid') {
        gridViewBtn.classList.add('active');
        watchlist.classList.add('grid')
    } else {
        listViewBtn.classList.add('active');
        watchlist.classList.remove('grid')
    }
};

const checkboxes = document.querySelectorAll('.filter-button-list input[type="checkbox"]');
    if (checkboxes) {
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
    }

    function getCSRFToken() {
        const cookies = document.cookie.split(';');
        for (const cookie of cookies) {
            const [key, value] = cookie.trim().split('=');
            if (key === 'csrftoken') {
                return value;
            }
        }
        return null;
    }

    const csrftoken = getCSRFToken();