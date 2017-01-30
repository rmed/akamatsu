/**
 * Dashboard specific javascript functions.
 */

/**
 * Update a field with the current date and time.
 *
 * Uses `date_field` attribute to determine the id of the field to update.
 *
 * Datetime is in format "YYYY-MM-DD hh:mm:ss".
 */
function onSetTodayClick() {
    var now = new Date();

	// Numbers must be padded
	var pad = function(num) {
		var val = num.toString();

		return '00'.substring(val.length) + val
	};

    var datetime = ''.concat(
		now.getFullYear(), '-', pad((now.getMonth()+1)), '-', pad(now.getDate()), ' ',
		pad(now.getHours()), ':', pad(now.getMinutes()), ':', pad(now.getSeconds())
	);

	// Update specified field
	var fieldId = $(this).attr('date_field');

	$('#'+fieldId).val(datetime);
}

/**
 * Show the edition form for an element in the dashboard.
 *
 * Works with Posts and Pages by extracting the `page_item` or `post_item`
 * attribute values from an element with `.aka-listitem` class.
 */
function onListItemClick() {
    var editUrl = '/dashboard';

    if ($(this)[0].hasAttribute('page_id')) {
        // Is a page
        editUrl = editUrl.concat('/pages/edit/', $(this).attr('page_id'));

    } else if ($(this)[0].hasAttribute('post_id')) {
        // Is a post
        editUrl = editUrl.concat('/blog/edit/', $(this).attr('post_id'));

    } else if ($(this)[0].hasAttribute('user_id')) {
        // Is an user
        editUrl = editUrl.concat('/users/edit/', $(this).attr('user_id'));

    } else if ($(this)[0].hasAttribute('file_id')) {
        // Is an uploaded file
        editUrl = editUrl.concat('/files/view/', $(this).attr('file_id'));

    } else {
        // What is this?
        return null;
    }

    // Redirect
    window.location.assign(editUrl);
}

/**
 * Change ordering in a dashboard list.
 *
 * Uses `ordered` and `order` attributes from elements with `.aka-listcolumn`
 * class.
 */
function onListColumnClick() {
    var current = window.location.pathname;
    var params = {orderby: 'date', order: 'desc'};

    // Get order key
    if ($(this)[0].hasAttribute('order-key'))
        params.orderby = $(this).attr('order-key');

    // Invert current order
    if ($(this)[0].hasAttribute('order')) {
        if ($(this).attr('order') === 'desc') {
            params.order = 'asc';

        } else {
            params.order = 'desc';
        }
    }

    // Redirect
    window.location.assign(current.concat('?', $.param(params)));
}

/**
 * Loads SimpleMDE editor in the relevant textarea
 */
function loadSimpleMDE() {
    var textarea = $('#content, #personal_bio');

    if (textarea.length) {
        var simplemde = new SimpleMDE({
            element: textarea[0],
            spellChecker: false,
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
                '|',
                'preview',
                'side-by-side',
                'fullscreen',
                'guide'
            ]
        });
    }
}


// Add event handlers and initializers
$(function() {
    $('.aka-listitem').on('click', onListItemClick);
    $('.aka-listcolumn').on('click', onListColumnClick);
    $('.aka-setnow').on('click', onSetTodayClick);

    loadSimpleMDE();
});
