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

    // Watchlist buttons
    document.querySelectorAll('.watchlist-btn').forEach(btn => {
        btn.onclick = function() {
            addToWatchlist(btn);
        };
    });

    // Text and plus icon watchlist button
    document.querySelectorAll('.add-watchlist-btn').forEach(btn => {
        btn.onclick = function() {
            addToWatchlist(btn, true);
        };
    });

    // Like button
    document.querySelectorAll('#like-btn').forEach(btn => {
        btn.onclick = function() {
            likeReview(btn);
        };
    });

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
                    element.classList.add('liked');
                } else {
                    element.classList.remove('liked');
                }
                const likeCountSpan = element.closest('.like-count').querySelector('span');
                likeCountSpan.textContent = `${data.like_count} likes`;
            })
            .catch(error => console.error("Error:", error));
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

    const radioBtns = document.querySelectorAll('.search-filters input[type="radio"]');
    if (radioBtns) {
        radioBtns.forEach(btn => {
            btn.addEventListener('change', function() {
                this.form.submit()
            });
        });
    }

    // Sorting form submission
    const sortForm = document.querySelector('.sort-form');
    const sortSelect = document.querySelector('.sort-form select');

    if (sortForm && sortSelect) {
        sortSelect.addEventListener('change', function() {
            sortForm.submit();
        });
    }

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
    
        const watchlist = document.querySelector('.watchlist-container ol')
    
        console.log("Current view mode:", viewMode);
    
        if (viewMode === 'grid') {
            gridViewBtn.classList.add('active');
            watchlist.classList.add('grid')
        } else {
            listViewBtn.classList.add('active');
            watchlist.classList.remove('grid')
        }
    };
});