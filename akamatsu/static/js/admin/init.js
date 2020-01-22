/**
 * This file contains initializers defined in other JS files and must
 * be imported last.
 */
$(document).ready(function() {
    // Bulma TagsInput
    bulmaTagsinput.attach();

    // Toggle admin sidebar
    $('#admin-sidebar-toggle').click(toggleBurger);

    // Pagination
    $('.pagination-previous').click(handlePagination);
    $('.pagination-next').click(handlePagination);
    $('.pagination-link').click(handlePagination);

    // Table sorting
    $('.sortable-header').click(setSortOrder);

    // Listing sorting
    // $('.sort-attribute').click(setOrderingAttribute);
    // $('.sort-order').click(setOrderingOrder);

    // EasyMDE
    loadEasyMDE();
});
