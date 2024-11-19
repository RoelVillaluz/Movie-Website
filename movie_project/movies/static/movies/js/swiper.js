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
        slidesPerView: 4,
      },
      768: {
        slidesPerView: 5,
      },
      1024: {
        slidesPerView: 6,
      },
      1200: {
        slidesPerView: 8,
      },
      1440: {
        slidesPerView: 10,
      },
      1920: {
        slidesPerView: 12,
      },
    }
  });

var gallerySwiper = new Swiper(".gallery-swiper", {
  slidesPerView: 4,
  spaceBetween: 5, 
  loop: true,
  pagination: {
    clickable: true,
  },
  slideClass: 'gallery-slide',
});