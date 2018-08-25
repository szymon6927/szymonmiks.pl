/* particlesJS.load(@dom-id, @path-json, @callback (optional)); */
particlesJS.load('particles-js', 'js/vendors/particles.json', function () {
  console.log('callback - particles.js config loaded');
});

window.FontAwesomeConfig = {
  searchPseudoElements: true
};

function goToByScroll(className) {
  if (!className.includes('.')) {
    className = "." + className
  }

  $('html, body').animate({
    scrollTop: $(className).offset().top - 64
  }, 1200);
}

$(document).ready(function () {
  let menuItems = $('.navbar-nav li');
  menuItems.first().addClass('active');

  menuItems.click((e) => {
    e.preventDefault();
    menuItems.removeClass('active');
    $(e.currentTarget).addClass('active');
    let className = $(e.currentTarget).data('goto');
    console.log(className);
    goToByScroll(className);
  });

  $('.go-to-top').click(() => {
    $('html, body').animate({scrollTop: 0}, 1500);
  });

  $('#back-top').hide();
  $(function () {
    $(window).scroll(function () {
      if ($(this).scrollTop() > 100) {
        $('#back-top').fadeIn();
      } else {
        $('#back-top').fadeOut();
      }
    });
    $('#back-top').click(function () {
      $('body,html').animate({
        scrollTop: 0
      }, 1500);
      return false;
    });
  });

  $('.scroll-btn').click(() => {
    goToByScroll('.about-me')
  });

  $(window).scroll(function (event) {
    let scrollTop = $(this).scrollTop();
    if (scrollTop > 600) {
      $('#nav-bar').addClass('fixed-navbar-helper');
    }
    else {
      $('#nav-bar').removeClass('fixed-navbar-helper');
    }
  });

});