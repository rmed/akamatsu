/**
 * This file contains initializers defined in other JS files and must
 * be imported last.
 */
$(document).ready(function() {
    // Toggle admin sidebar
    $('#admin-sidebar-toggle').click(toggleBurger);

    // EasyMDE
    loadEasyMDE();
});
