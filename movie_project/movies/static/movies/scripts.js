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


const galleryImages = document.querySelectorAll('.gallery img')
galleryImages.forEach(image => {
    image.addEventListener('click', function() {
        const dataId = this.getAttribute('data-id')
        console.log(dataId)
    })
})