document.addEventListener('DOMContentLoaded', () => {
    // Wrap everything inside a single DOMContentLoaded event listener

    // Check if featured movie elements exist before accessing them
    const imgElement = document.querySelector('.featured-movie img');
    const titleElement = document.getElementById('movie-title');
    const subTitleElement = document.getElementById('movie-subtitle');
    const linkElement = document.getElementById('movie-link');
    
    if (imgElement && titleElement && subTitleElement && linkElement) {
        const movieData = [
            {
                title: 'Spider-Man',
                subtitle: 'Across the Spiderverse',
                image: 'media/media/backdrop_VyAOcwH.jpg',
                link: 'movies/155'
            },
            {
                title: 'The Batman',
                subtitle: '',
                image: 'media/media/the_batman_2022_backdrop.jpg',
                link: 'movies/180'
            },
            {
                title: 'The Wild Robot',
                subtitle: '',
                image: 'media/media/The_Wild_Robot_backdrop_JlYwjfE.jpg',
                link: 'movies/515'
            },
            {
                title: 'Barbie',
                image: 'media/media/backdrop_47Z00ZJ.jpg',
                link: 'movies/172'
            }
        ];

        let currentIndex = 0;

        function updateMovie() {
            currentIndex = (currentIndex + 1) % movieData.length;
            const movie = movieData[currentIndex];
            
            imgElement.classList.remove('animate-img');
            titleElement.classList.remove('animate-title');
            subTitleElement.classList.remove('animate-subtitle');
            
            // Trigger reflow to restart animations
            void imgElement.offsetWidth; // Trigger reflow
            void titleElement.offsetWidth; // Trigger reflow
            void subTitleElement.offsetWidth; // Trigger reflow

            imgElement.classList.add('animate-img');
            titleElement.classList.add('animate-title');
            subTitleElement.classList.add('animate-subtitle');
            
            imgElement.src = movie.image;
            titleElement.textContent = movie.title;
            subTitleElement.textContent = movie.subtitle;
            linkElement.href = movie.link;
        }

        function startMovieRotation() {
            imgElement.classList.add('animate-img');
            titleElement.classList.add('animate-title');
            subTitleElement.classList.add('animate-subtitle');
            imgElement.addEventListener('animationend', updateMovie);
        }

        startMovieRotation();
    }

    // Check if movie elements exist
    const movieContainer = document.querySelector('.movie');
    const movieBackdrop = document.querySelector('.movie-backdrop');
    const movieTitle = document.querySelector('.movie-title');
    const moviePoster = document.querySelector('.movie-poster');
    const genres = document.querySelectorAll('.movie-genre');

    if (movieBackdrop && movieTitle) {
        movieBackdrop.addEventListener('animationend', function() {
            movieTitle.classList.add('animate');
        });

        movieTitle.addEventListener('animationend', function() {
            genres.forEach((genre, index) => {
                genre.style.animationDelay = `${index * 0.2}s`;
                setTimeout(() => {
                    genre.classList.add('animate');
                }, 100); // Slight delay to ensure animation starts correctly
            });

            genres[genres.length - 1].addEventListener('animationend', function() {
                // Enable scrolling after the last genre animation ends
                document.body.classList.remove('no-scroll');
            }, { once: true }); // Ensure this only triggers once
        });
    }

    // Intersection Observer setup
    // Observer callback
    const observerOptions = {
        root: null, // Use the viewport as the root
        rootMargin: '0px',
        threshold: 0.5 // Trigger when at least 50% of the element is visible
    };

    const observerCallback = (entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('show');
                entry.target.classList.remove('skeleton'); // Remove the skeleton class
                observer.unobserve(entry.target); // Stop observing once the element is in view
            } else {
                entry.target.classList.remove('show');
            }
        });
    };

    // Initialize the observer
    const observer = new IntersectionObserver(observerCallback, observerOptions);

    // Function to start observing new content after HTMX swaps
    function initializeObserver() {
        // Observe newly added elements (those with .hidden or .skeleton class)
        const elementsToObserve = document.querySelectorAll('.hidden, .skeleton');
        elementsToObserve.forEach(element => observer.observe(element));
    }

    // Listen for HTMX events and reinitialize the observer for new content
    document.body.addEventListener('htmx:afterSwap', (event) => {
        initializeObserver();  // Reinitialize the observer after content swap
    });

    // Initial observer setup for any pre-existing elements
    initializeObserver();
    
    // Apply animation delay to genre cards
    const genreCards = document.querySelectorAll('.genre-card.hidden');
    if (genreCards.length > 0) {
        let animationEndCount = 0;
        genreCards.forEach((card, index) => {
            card.style.animationDelay = `${index * 0.25}s`;

            card.addEventListener('animationend', () => {
                animationEndCount++;
                if (animationEndCount === genreCards.length) {
                    genreCards.forEach(card => {
                        card.classList.add('animation-complete');
                        card.style.pointerEvents = 'auto';
                    });
                }
            });
        });
    }

    // Function to apply animation delay to a set of elements
    const applyAnimationDelay = (elements, delay) => {
        if (elements.length > 0) {
            elements.forEach((element, index) => {
                element.style.animationDelay = `${index * delay}s`;
            });
        }
    };

    // Apply animation delays to various element groups
    const actorCards = document.querySelectorAll('.cast-actor.hidden');
    applyAnimationDelay(actorCards, 0.15);

    const relatedDirectorMovies = document.querySelectorAll('.movie-director-movies .card.hidden');
    applyAnimationDelay(relatedDirectorMovies, 0.15);

    const topReviewCards = document.querySelectorAll('.top-review.hidden');
    applyAnimationDelay(topReviewCards, 0.25);

    const popularActorImages = document.querySelectorAll('.popular-actors-list .item');
    applyAnimationDelay(popularActorImages, 0.15);

    const cards = document.querySelectorAll('.card');
    applyAnimationDelay(cards, 0.15);

    window.addEventListener('load', () => {
        pageHasLoaded = true;
    });

    const genreLinks = document.querySelectorAll('.genre-names a');
    const genreImage = document.getElementById('genre-image');
    const genreList = document.querySelector('.genre-names');
    const scrollIcon = document.querySelector('.scroll-icon');

    // Apply transition effect initially
    genreImage.style.transition = 'opacity 0.3s ease';

    genreLinks.forEach(link => {
        link.addEventListener('mouseenter', () => {
            const backdropPath = link.getAttribute('data-backdrop');
            if (backdropPath) {
                // Fade out the image
                genreImage.style.opacity = '0';

                // Wait for the fade-out transition, then change the image and fade in
                setTimeout(() => {
                    genreImage.src = backdropPath;
                    genreImage.style.opacity = '1';
                }, 200); 
            }
            scrollIcon.innerHTML = '<i class="fa-solid fa-hand-pointer"></i>'
            scrollIcon.querySelector('i').style.opacity = '1';
        });
        link.addEventListener('mouseleave', () => {
            scrollIcon.innerHTML = `
                <i class="fa-solid fa-angle-up"></i>
                <i class="fa-solid fa-angle-down"></i>
            `
        })
    });

    genreList.addEventListener('mouseenter', () => {
        scrollIcon.style.opacity = '0.5';  
    });

    genreList.addEventListener('mouseleave', () => {
        scrollIcon.style.opacity = '0'; 
    });

    genreList.addEventListener('mousemove', (e) => {
        const mouseX = e.clientX;
        const mouseY = e.clientY;

        const rect = genreList.getBoundingClientRect();  
        const scrollTop = genreList.scrollTop;  

        scrollIcon.style.left = `${mouseX - rect.left}px`;  
        scrollIcon.style.top = `${mouseY - rect.top + scrollTop}px`;  
    });

    genreList.style.cursor = 'none';

    const genreMovie = document.querySelector('.genre-movie');

    // Sync scroll between genre image and genre list
    genreMovie.addEventListener('wheel', (event) => {
        const scrollDelta = event.deltaY; 
        genreList.scrollTop += scrollDelta; 

        event.preventDefault();
    });
});