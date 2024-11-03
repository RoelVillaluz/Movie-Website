
document.addEventListener('DOMContentLoaded', () => {
    // add movieData[clips] later
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

    const imgElement = document.querySelector('.featured-movie img');
    const titleElement = document.getElementById('movie-title');
    const subTitleElement = document.getElementById('movie-subtitle');
    const linkElement = document.getElementById('movie-link');

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

});

document.addEventListener('DOMContentLoaded', function() {
    const movieContainer = document.querySelector('.movie');
    const movieBackdrop = document.querySelector('.movie-backdrop');
    const movieTitle = document.querySelector('.movie-title');
    const moviePoster = document.querySelector('.movie-poster');
    const genres = document.querySelectorAll('.movie-genre'); 

    movieBackdrop.addEventListener('animationend', function() {
        movieTitle.classList.add('animate');
    });

    // document.body.classList.add('no-scroll');

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
});
document.addEventListener('DOMContentLoaded', () => {
    // Intersection Observer setup
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

    const observer = new IntersectionObserver(observerCallback, observerOptions);

    // Observe hidden and skeleton elements
    const elementsToObserve = document.querySelectorAll('.hidden, .skeleton');
    elementsToObserve.forEach(element => observer.observe(element));

    // Animation handling for genre cards
    const genreCards = document.querySelectorAll('.genre-card.hidden');
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

    // Function to apply animation delay to a set of elements
    const applyAnimationDelay = (elements, delay) => {
        elements.forEach((element, index) => {
            element.style.animationDelay = `${index * delay}s`;
        });
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
});

function applyAnimationDelay(elements, delay) {
    elements.forEach((element, index) => {
        element.style.animationDelay = `${index * delay}s`;
    });
}

window.addEventListener('load', () => {
    pageHasLoaded = true;
});