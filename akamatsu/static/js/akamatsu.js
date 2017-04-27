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

/**
 * Modal for displaying full size images
 */
function toggleImageModal(image) {
    // Delete any previous modal
    $('#aka-modal').remove();

    var $modal = $('<div>', {id: 'aka-modal'});

    // Close button
    var $close = $('<span>', {id: 'aka-modal-close'});
    $close.append('<i class="fa fa-times-circle"></i>');

    $close.on('click', function(e) {
        $modal.remove();
    });

    // Image
    var $image = $('<img>', {id: 'aka-modal-image'});
    $image.attr('src', image.attr('src'));
    $image.attr('alt', image.attr('alt'));

    // Caption
    var $caption = $('<div>', {id: 'aka-modal-caption'});
    $caption.html(image.attr('alt'));


    $modal.append($close, $image, $caption);
    $modal.appendTo(document.body);
}

$(function() {
    // Sticky navigation bar
    toggleStickyNav();

    // Clicked menu button, toggle classes
    $('#aka-navmenu').on('click', function(e) {
        $('.navitem').toggleClass('shown');
    });

    // Clicked image, show in modal
    var images = $('.aka-page img').add('.aka-post img').add('img.scale');
    images.on('click', function(e) {
        toggleImageModal($(e.target));
    });
});

