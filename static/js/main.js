document.addEventListener("DOMContentLoaded", function () {
  const menuBtn = document.getElementById("menu-btn");
  const navLinks = document.getElementById("nav-links");

  menuBtn.addEventListener("click", function () {
    navLinks.classList.toggle("show");
  });
});

window.sr = ScrollReveal();

sr.reveal('.hero__content', {
  duration: 1000,
  origin: 'left',
  distance: '50px',
});

sr.reveal('.hero__image', {
  duration: 1000,
  origin: 'right',
  distance: '50px',
});

sr.reveal('.steps__card, .service__image, .service__content, .experience__card, .experience__image, .download__grid', {
  duration: 1000,
  origin: 'bottom',
  distance: '50px',
  interval: 200,
});

document.getElementById("menu-btn").addEventListener("click", function() {
  document.getElementById("nav-links").classList.toggle("show-menu");
});