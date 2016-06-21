/**
 * Toggle sticky navigation bar
 */
function toggleStickyNav() {
    var navbarTop = $('.aka-navbar').offset().top;

    $(window).scroll(function() {
        var scrollTop = $(window).scrollTop();

        if (scrollTop > navbarTop) {
            $('.aka-header').addClass('scrolling');
            $('.aka-navbar').addClass('sticky');

        } else {
            $('.aka-header').removeClass('scrolling');
            $('.aka-navbar').removeClass('sticky');
        }
    });
}

$(function() {
    // Sticky navigation bar
    toggleStickyNav();

    // Clicked menu button, toggle classes
    $('#aka-navmenu').on('click', function(e) {
        $('.navitem').toggleClass('shown');
    });

});

