/**
 * This file contains initializers defined in other JS files and must
 * be imported last.
 */
$(document).ready(function() {
    // Bulma Calendar
    ['datetime', 'date', 'time'].forEach(function(item, index) {
        bulmaCalendar.attach('.calendar-'+item, {
            type: item,
            dateFormat: 'YYYY-MM-DD',
            timeFormat: 'HH:mm',
            minuteSteps: 1,
            weekStart: 1,
            displayMode: 'dialog',
            validateLabel: '<span class="icon"><i class="fas fa-check fa-lg"></i></span>',
            todayLabel: '<span class="icon"><i class="fas fa-calendar-day fa-lg"></i></span>',
            clearLabel: '<span class="icon"><i class="fas fa-eraser fa-lg"></i></span>',
            cancelLabel: '<span class="icon"><i class="fas fa-times fa-lg"></i></span>',
            onReady: function(instance) {
                // Workaround: remove submit from clear button
                var id = instance.data._id;
                var $element = $('#'+id);

                if (!$element) {
                    return;
                }

                var $button = $element.find('.datetimepicker-clear-button');
                $button.prop('type', 'button');
            }
        });
    });

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
