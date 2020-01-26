/**
 * Toggle admin sidebar.
 */
function toggleAdminSidebar(e) {
    e.preventDefault();

    var $target = $('#' + $(this).data('target'));

    if (!$target) {
        return;
    }

    $(this).toggleClass('is-active');
    $target.toggleClass('is-active');
}


/**
 * Loads EasyMDE editor in the relevant textarea
 */
function loadEasyMDE() {
    var $textarea = $('#content, #personal_bio');

    if ($textarea.length == 0) {
        return;
    }

    var easyMDE = new EasyMDE({
        autoDownloadFontAwesome: false,
        element: $textarea[0],
        spellChecker: false,
        previewClass: ['editor-preview', 'content'],
        forceSync: true,
        tabSize: 4,
        toolbar: [
            'bold',
            'italic',
            'heading',
            '|',
            'code',
            'quote',
            'unordered-list',
            'ordered-list',
            '|',
            'link',
            'image',
            'table',
            'horizontal-rule',
            {
                name: 'break',
                action: function insertBreak(editor) {
                    var cm = editor.codemirror;
                    var start = cm.getCursor('start');
                    var end = cm.getCursor('end');

                    cm.setSelection(start, end);
                    cm.replaceSelection('<!--aka-break-->');
                    cm.focus();
                },
                className: 'fas fa-level-down-alt',
                title: 'Break'
            },
            '|',
            'preview',
            'side-by-side',
            'fullscreen',
            'guide'
        ]
    });
}


/**
 * Sort a listing by the specified parameter.
 *
 * In practice, this will fetch the page from the server and update both the
 * view and the URL.
 *
 * @param $container container element for the page
 * @param query query parameters object
 * @param handlers function to call in order to reattach handlers after loading
 */
function sortListing($container, query, handlers) {
    if ($container.length === 0) {
        showNotification('error', 'ERROR');
        console.log('[ERROR] Cannot find page container');
    }

    // Replace parameters
    var urlParams = document.location.search;

    if (urlParams) {
        for (var [k, v] of Object.entries(query)) {
            var paramRegex = new RegExp('([\?&])' + k + '[^&]*');
            var normalizedParam = k + '=' + v;

            // Update if the param exists
            if (urlParams.match(paramRegex) !== null) {
                urlParams = urlParams.replace(paramRegex, '$1' + normalizedParam);

            } else {
                urlParams = urlParams + '&' + normalizedParam;
            }
        }

    } else {
        var normalizedParams = [];
        for (var pair of Object.entries(query)) {
            normalizedParams.push(pair.join('='));
        }

        var normalizedParams = normalizedParams.join('&');
        urlParams = urlParams + '?' + normalizedParams;
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


function setSortOrder() {
    var $container = $(this).closest('.page-items');
    var sortAttribute = $(this).data('sort');
    var orderAttribute = $(this).data('order');

    var handlers = function() {
        $container.find('.pagination-previous').click(handlePagination);
        $container.find('.pagination-next').click(handlePagination);
        $container.find('.pagination-link').click(handlePagination);
        $container.find('.dropdown-trigger').click(toggleDropdown);
        $container.find('.sortable-header').click(setSortOrder);
        $container.find('.delete-item').on(
            'click',
            {func: confirmItemDeletion},
            showConfirmationModal
        );
    };

    var query = {
        'sort': sortAttribute,
    };

    // Invert order
    if (orderAttribute === 'asc') {
        query['order'] = 'desc';

    } else if (orderAttribute === 'desc') {
        query['order'] = 'asc';
    }

    sortListing($container, query, handlers);
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
            $container.find('.sortable-header').click(setSortOrder);
            $container.find('.delete-item').on(
                'click',
                {func: confirmItemDeletion},
                showConfirmationModal
            );
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
            $container.find('.delete-item').on(
                'click',
                {func: confirmItemDeletion},
                showConfirmationModal
            );
        },
        error: function(xhr, textStatus, errorThrown) {
            console.log('[ERROR] ' + xhr.responseText);
            showNotification('error', 'ERROR');
        }
    });
}


/**
 * Base confirmation modal.
 *
 * This method first makes a GET request to get the contents of the modal and
 * then, if the .modal-confirm button is pressed, it makes a POST request
 * to its specified link.
 */
function showConfirmationModal(e) {
    // Prevent page reloads
    e.preventDefault();

    var func = e.data.func;
    var link = $(this).attr('href');

    if (!link) {
        // Assume that the link was disabled
        return;
    }

    var $modal = $('#global-modal');
    var $modalContent = $('#global-modal-content');

    // Event handlers
    var close = function() {
        $modalContent.html('');
        $modal.removeClass('is-active');
    }

    var confirmAction = function(e) {
        func(e, $(this));
        close();
    }

    // Get modal content
    $.ajax({
        url: link,
        type: 'GET',
        success: function(data) {
            // Update page
            $modalContent.html(data);

            $modalContent.find('.delete').click(close);
            $modalContent.find('.cancel-action').click(close);
            $modalContent.find('.confirm-action').click(confirmAction);

            $modal.addClass('is-active');
        },
        error: function(xhr, textStatus, errorThrown) {
            console.log('[ERROR] ' + xhr.responseText);
            showNotification('error', 'ERROR');
        }
    });
}


/**
 * Confirm item deletion.
 *
 * This is called after the user has confirmed the deletion through the
 * appropriate modal.
 */
function confirmItemDeletion(e, $item) {
    // Prevent page reloads
    e.preventDefault();

    var link = $item.attr('href');

    if (!link) {
        console.log('[ERROR] Cannot find deletion link');
        showNotification('error', 'ERROR');
        return;
    }

    // Delete recipe
    $.ajax({
        url: link,
        type: 'POST',
        success: function(data) {
            // Recipe was deleted, should have received redirect
            var redirectLink = data['redirect'];

            if (!redirectLink) {
                console.log('[ERROR] Did not get redirect from server');
                showNotification('error', 'ERROR');
                return;
            }

            // Redirect to the specified URL
            window.location.replace(redirectLink);
        },
        error: function(xhr, textStatus, errorThrown) {
            console.log('[ERROR] ' + xhr.responseText);
            showNotification('error', 'ERROR');
        }
    });
}

