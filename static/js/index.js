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

    // check if the left arrow key is pressed
    if (event.code === 'ArrowLeft') {
        event.preventDefault(); // prevents default left arrow behavior (scrolling)
        closeAllCards(); // close all flipped cards
        const prevButton = document.querySelector('.carousel-control-prev');
        if (prevButton) {
            prevButton.click(); // navigate to the previous card
        }
    }

    // check if the right arrow key is pressed
    if (event.code === 'ArrowRight') {
        event.preventDefault(); // prevents default right arrow behavior (scrolling)
        closeAllCards(); // close all flipped cards
        const nextButton = document.querySelector('.carousel-control-next');
        if (nextButton) {
            nextButton.click(); // navigate to the next card
        }
    }

    // function to close all flipped cards
    function closeAllCards() {
        document.querySelectorAll('.card.flipped').forEach(function (card) {
            card.classList.remove('flipped'); // remove the 'flipped' class
        });
    }

    // close flipped cards when carousel navigation occurs
    document.querySelectorAll('.carousel-control-prev, .carousel-control-next').forEach(function (control) {
        control.addEventListener('click', function () {
            closeAllCards(); // Close all flipped cards
        });
    });
});
