// handle the card flip on click inside the carousel
document.querySelectorAll('.card').forEach(function (card) {
    card.addEventListener('click', function () {
        this.classList.toggle('flipped');
    });
});

// handle the card flip when the spacebar is pressed
document.addEventListener('keydown', function (event) {
    // check if the event is a spacebar press and if the active element is not an input
    if (event.code === 'Space' && document.activeElement.tagName !== 'INPUT') {
        event.preventDefault(); // prevents default spacebar behavior like scrolling

        // identify the active card in the carousel
        const activeCard = document.querySelector('.carousel-item.active .card');
        if (activeCard) {
            activeCard.classList.toggle('flipped');
        }
    }
});
