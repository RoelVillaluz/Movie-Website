var swiper = new Swiper(".mySwiper", {
    slidesPerView: 8,
    spaceBetween: 10,
    loop: true, 
    pagination: {
      clickable: true,
    },
    breakpoints: {
      320: {
        slidesPerView: 2,
      },
      480: {
        slidesPerView: 3,
      },
      768: {
        slidesPerView: 4,
      },
      991: {
        slidesPerView: 5,
      },
      1024: {
        slidesPerView: 6,
      },
      1200: {
        slidesPerView: 8,
      }
    }
  });

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
          title: 'Minions',
          subtitle: 'The Rise of Gru',
          image: 'media/media/backdrop_VJeYqoT.jpg',
          link: 'movies/179'
      },
      {
          title: 'Dune: Part Two',
          image: 'media/media/backdrop_1NjmW80.jpg',
          link: 'movies/131'
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
    const hiddenElements = document.querySelectorAll('.hidden');
    const observerOptions = {
        root: null, // Use the viewport as the root
        rootMargin: '0px',
        threshold: 0.5 // Trigger when at least 50% of the element is visible
    };

    const observerCallback = (entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('show');
                observer.unobserve(entry.target); // Stop observing once the element is in view
            } else {
                entry.target.classList.remove('show');
            }
        });
    };

    const observer = new IntersectionObserver(observerCallback, observerOptions);

    hiddenElements.forEach(element => {
        observer.observe(element);
    });

    const genreCards = document.querySelectorAll('.genre-card.hidden');
    let animationEndCount = 0;

    function allAnimationsEnded() {
        if (animationEndCount === genreCards.length) {
            genreCards.forEach(card => {
                card.style.pointerEvents = 'auto';
            });
        }
    }

    genreCards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.25}s`;

        card.addEventListener('animationend', function() {
            animationEndCount++;
            allAnimationsEnded();
        });
    });


    const actorCards = document.querySelectorAll('.cast-actor.hidden')
    actorCards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.15}s`
    })

    const relatedDirectorMovies = document.querySelectorAll('.movie-director-movies .card.hidden')
    relatedDirectorMovies.forEach((movie,index) => {
        movie.style.animationDelay = `${index * 0.15}s`
    });
});

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

const cursor = document.querySelector('.cursor')
document.addEventListener('mousemove', e => {
    cursor.setAttribute('style', `top: ${e.pageY}px; left: ${e.pageX}px;`)
})