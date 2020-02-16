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

    // EasyMDE
    loadEasyMDE();

    // Confirmation modals
    $('.delete-item').on(
        'click',
        {func: confirmItemDeletion},
        showConfirmationModal
    );

    // File uploads
    $('input[type=file]').change(updateUploadFilename);
});


/**
 * Configure AJAX requests
 */
$(document).on('ajaxBeforeSend', function(e, xhr, options) {
    // Add custom header to detect AJAX requests
    xhr.setRequestHeader('x-akamatsu-partial', 'true');

    // Handle CSRF protection in specific AJAX requests.
    // The tag needs to be enabled in the template.
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
