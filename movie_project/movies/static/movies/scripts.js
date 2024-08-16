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

function addToWatchlist(element, containsText = false) {
    fetch(`/add_to_watchlist/${element.dataset.id}/`)
        .then(response => response.json())
        .then(data => {
            if (data.watchlisted) {
                element.classList.add('watchlisted');
                if (containsText) {
                    element.querySelector('span').textContent = 'Remove from Watchlist';
                    element.querySelector('button').textContent = '-';
                    showNotification("Movie added to watchlist");
                }
            } else {
                element.classList.remove('watchlisted');
                if (containsText) {
                    element.querySelector('span').textContent = 'Add to Watchlist';
                    element.querySelector('button').textContent = '+';
                    showNotification("Movie removed from watchlist");
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
}

function showNotification(message) {
    let notification = document.querySelector('.notification');
    
    if (!notification) {
        notification = document.createElement('div');
        notification.className = 'notification';
        document.body.appendChild(notification);
    }

    notification.textContent = message;
    notification.style.display = 'block';

    setTimeout(() => {
        notification.style.display = 'none';
    }, 3000);
}