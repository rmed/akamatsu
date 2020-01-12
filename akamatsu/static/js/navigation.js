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


/**
 * Sort a listing by the specified parameter.
 *
 * In practice, this will fetch the page from the server and update both the
 * view and the URL.
 *
 * @param $container container element for the page
 * @param paramName parameter name
 * @param paramValue parameter value
 * @param handlers function to call in order to reattach handlers after loading
 */
function sortListing($container, paramName, paramValue, handlers) {
    if ($container.length === 0) {
        showNotification('error', 'ERROR');
        console.log('[ERROR] Cannot find page container');
    }

    var normalizedParam = paramName + '=' + paramValue;

    // Replace parameters
    var urlParams = document.location.search;

    if (urlParams) {
        var paramRegex = new RegExp('([\?&])' + paramName + '[^&]*');

        // Update if the param exists
        if (urlParams.match(paramRegex) !== null) {
            urlParams = urlParams.replace(paramRegex, '$1' + normalizedParam);

        } else {
            urlParams = urlParams + '&' + normalizedParam;
        }

    } else {
        urlParams = urlParams + '?' + normalizedParam;
    }

    var link = window.location.pathname + urlParams;

    // Get sorted page
    $.ajax({
        url: link,
        type: 'GET',
        success: function(data) {
            // Update page
            $container.html(data);

            // Change URL
            window.history.pushState('', '', link);

            // Reattach events
            handlers();
        },
        error: function(xhr, textStatus, errorThrown) {
            console.log('[ERROR] ' + xhr.responseText);
            showNotification('error', 'ERROR');
        }
    });
}


/**
 * Set the ordering attribute in a list.
 */
function setOrderingAttribute() {
    var attribute = $(this).data('sort');
    var $container = $(this).closest('.page-items');

    var handlers = function() {
        $container.find('.pagination-previous').click(handlePagination);
        $container.find('.pagination-next').click(handlePagination);
        $container.find('.pagination-link').click(handlePagination);
        $container.find('.dropdown-trigger').click(toggleDropdown);
        $container.find('.sort-attribute').click(setOrderingAttribute);
        $container.find('.sort-order').click(setOrderingOrder);
    };

    sortListing($container, 'sort', attribute, handlers);
}


/**
 * Set the ordering in a list.
 */
function setOrderingOrder() {
    var order = $(this).data('order');
    var $container = $(this).closest('.page-items');

    var handlers = function() {
        $container.find('.pagination-previous').click(handlePagination);
        $container.find('.pagination-next').click(handlePagination);
        $container.find('.pagination-link').click(handlePagination);
        $container.find('.dropdown-trigger').click(toggleDropdown);
        $container.find('.sort-attribute').click(setOrderingAttribute);
        $container.find('.sort-order').click(setOrderingOrder);
    };

    sortListing($container, 'order', order, handlers);
}


/**
 * Handle pagination with AJAX.
 */
function handlePagination(e) {
    // Prevent reload
    e.preventDefault();

    var $container = $(this).closest('.page-items');

    if ($container.length === 0) {
        console.log('[ERROR] Cannot find page container');
        return;
    }

    var link = $(this).attr('href');

    if (!link) {
        return;
    }

    // Update content
    $.ajax({
        url: link,
        type: 'GET',
        success: function(data) {
            // Update page
            $container.html(data);

            // Change URL
            window.history.pushState('', '', link);

            // Reattach events
            $container.find('.pagination-previous').click(handlePagination);
            $container.find('.pagination-next').click(handlePagination);
            $container.find('.pagination-link').click(handlePagination);
            $container.find('.dropdown-trigger').click(toggleDropdown);
            $container.find('.sort-attribute').click(setOrderingAttribute);
            $container.find('.sort-order').click(setOrderingOrder);
            $container.find('.sortable-header').click(handleTableSorting);
        },
        error: function(xhr, textStatus, errorThrown) {
            console.log('[ERROR] ' + xhr.responseText);
            showNotification('error', 'ERROR');
        }
    });
}


/**
 * Handle table sorting with AJAX.
 *
 * In practice, this is the same as loading a new page with other filters.
 */
function handleTableSorting(e) {
    // Prevent reload
    e.preventDefault();

    var $container = $(this).closest('.page-items');

    if ($container.length === 0) {
        console.log('[ERROR] Cannot find page container');
        return;
    }

    var link = $(this).attr('href');

    if (!link) {
        return;
    }

    // Update content
    $.ajax({
        url: link,
        type: 'GET',
        success: function(data) {
            // Update page
            $container.html(data);

            // Change URL
            window.history.pushState('', '', link);

            // Reattach events
            $container.find('.pagination-previous').click(handlePagination);
            $container.find('.pagination-next').click(handlePagination);
            $container.find('.pagination-link').click(handlePagination);
            $container.find('.dropdown-trigger').click(toggleDropdown);
            $container.find('.sort-attribute').click(setOrderingAttribute);
            $container.find('.sort-order').click(setOrderingOrder);
            $container.find('.sortable-header').click(handleTableSorting);
        },
        error: function(xhr, textStatus, errorThrown) {
            console.log('[ERROR] ' + xhr.responseText);
            showNotification('error', 'ERROR');
        }
    });
}
