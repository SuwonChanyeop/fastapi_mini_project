window.addEventListener("scroll", revealCards);

function revealCards() {
    const cards = document.querySelectorAll('.card');
    const triggerBottom = window.innerHeight * 0.85;

    cards.forEach(card => {
        const boxTop = card.getBoundingClientRect().top;

        if (boxTop < triggerBottom) {
            card.classList.add('show');
        }
    });
}

document.addEventListener("DOMContentLoaded", revealCards);
