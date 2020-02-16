/**
 * This file contains initializers defined in other JS files and must
 * be imported last.
 */
$(document).ready(function() {
    // Toggle burger
    $('.navbar-burger').click(toggleBurger);

    // Dropdown toggling
    $(document).click(closeDropdowns);
    $('.dropdown-trigger').click(toggleDropdown);
});
