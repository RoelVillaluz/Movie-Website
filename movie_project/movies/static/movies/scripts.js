var swiper = new Swiper(".mySwiper", {
  slidesPerView: 8,
  spaceBetween: 10,
  loop: true, 
  pagination: {
    clickable: true,
  },
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
    const movieBackdropAnimation = document.querySelector('.movie-backdrop');
    const movieTitle = document.querySelector('.movie-title');
    const moviePoster = document.querySelector('.movie-poster');
    const genres = document.querySelectorAll('.movie-genre'); 

    movieBackdropAnimation.addEventListener('animationend', function() {
        movieTitle.classList.add('animate');
    });

    document.body.classList.add('no-scroll');

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
