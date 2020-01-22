/**
 * Show a floating notification on screen.
 *
 * Default timeout is 10 seconds.
 *
 * @param type message type (success, warning, etc.)
 * @param message message to show
 * @param timeout timeout for the message in milliseconds
 */
function showNotification(type, message, timeout) {
    if (typeof timeout === 'undefined') {
        timeout = 10000;
    }

    var params = {
        type: type,
        text: message,
        timeout: timeout
    };

    new Noty(params).show();
}


/**
 * Close all dropdowns (when clicking anywhere on the page).
 */
function closeDropdowns() {
    $('.dropdown').removeClass('is-active');
}


/**
 * Toggle a dropdown menu.
 */
function toggleDropdown(e) {
    e.stopPropagation();

    var $dropdown = $(this).closest('.dropdown');
    var wasActive = $dropdown.hasClass('is-active');

    // Clear all dropdowns
    $('.dropdown').removeClass('is-active');

    if (!wasActive) {
        $(this).closest('.dropdown').addClass('is-active');
    }
}


/**
 * Toggle navbar burger in mobile.
 */
function toggleBurger(e) {
    e.preventDefault();

    var $target = $('#' + $(this).data('target'));

    if (!$target) {
        return;
    }

    $(this).toggleClass('is-active');
    $target.toggleClass('is-active');
}
