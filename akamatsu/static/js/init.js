/**
 * This file contains initializers defined in other JS files and must
 * be imported last.
 */
$(document).ready(function() {
    // Bulma TagsInput
    bulmaTagsinput.attach();

    // Toggle burger
    $('.navbar-burger').click(toggleBurger);

    // Pagination
    $('.pagination-previous').click(handlePagination);
    $('.pagination-next').click(handlePagination);
    $('.pagination-link').click(handlePagination);

    // Table sorting
    $('.sortable-header').click(handleTableSorting);

    // Dropdown toggling
    $(document).click(closeDropdowns);
    $('.dropdown-trigger').click(toggleDropdown);

    // Listing sorting
    $('.sort-attribute').click(setOrderingAttribute);
    $('.sort-order').click(setOrderingOrder);
});


/**
 * Handle CSRF protection in specific AJAX requests.
 *
 * The tag needs to be enabled in the template.
 */
$(document).on('ajaxBeforeSend', function(e, xhr, options) {
    if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(options.type) && !this.crossDomain) {
        var $csrf = $('meta[name=csrf-token]');

        if ($csrf.length === 0) {
            // Missing CSRF token
            console.log('[ERROR] Missing CSRF meta tag');
            showNotification('error', 'ERROR - CSRF');

        } else {
            xhr.setRequestHeader('X-CSRFToken', $csrf.attr('content'));
        }
    }
});
