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
