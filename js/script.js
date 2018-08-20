/* particlesJS.load(@dom-id, @path-json, @callback (optional)); */
particlesJS.load('particles-js', 'js/vendors/particles.json', function() {
  console.log('callback - particles.js config loaded');
});

$(document).ready(function () {
  let menuItems = $('.navbar-nav li');
  menuItems.first().addClass('active');

  menuItems.click((e) => {
    menuItems.removeClass('active');

    $(e.currentTarget).addClass('active');
  })
});