'use strict';

var _slicedToArray = function () { function sliceIterator(arr, i) { var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"]) _i["return"](); } finally { if (_d) throw _e; } } return _arr; } return function (arr, i) { if (Array.isArray(arr)) { return arr; } else if (Symbol.iterator in Object(arr)) { return sliceIterator(arr, i); } else { throw new TypeError("Invalid attempt to destructure non-iterable instance"); } }; }();

/**
 * A Review UI for file types which otherwise do not have one.
 *
 * Normally, file types that do not have a Review UI are not linked to one.
 * However, in the case of a file attachment with multiple revisions, if one of
 * those revisions is a non-reviewable type, the user can still navigate to
 * that page. This Review UI is used as a placeholder in that case--it shows
 * the header (with revision selector) and a message saying that this file type
 * cannot be shown.
 */
RB.DummyReviewableView = RB.FileAttachmentReviewableView.extend({
    commentBlockView: RB.AbstractCommentBlockView,

    captionTableTemplate: _.template('<table><tr><%= items %></tr></table>'),

    captionItemTemplate: _.template('<td>\n <h1 class="caption"><%- caption %></h1>\n</td>'),

    /**
     * Render the view.
     */
    renderContent: function renderContent() {
        var $header = $('<div/>').addClass('review-ui-header').prependTo(this.$el);

        if (this.model.get('numRevisions') > 1) {
            var $revisionLabel = $('<div id="revision_label"/>').appendTo($header);

            this._revisionLabelView = new RB.FileAttachmentRevisionLabelView({
                el: $revisionLabel,
                model: this.model
            });
            this._revisionLabelView.render();
            this.listenTo(this._revisionLabelView, 'revisionSelected', this._onRevisionSelected);

            var $revisionSelector = $('<div id="attachment_revision_selector" />').appendTo($header);
            this._revisionSelectorView = new RB.FileAttachmentRevisionSelectorView({
                el: $revisionSelector,
                model: this.model
            });
            this._revisionSelectorView.render();
            this.listenTo(this._revisionSelectorView, 'revisionSelected', this._onRevisionSelected);

            var captionItems = [];

            captionItems.push(this.captionItemTemplate({
                caption: interpolate(gettext('%(caption)s (revision %(revision)s)'), {
                    caption: this.model.get('caption'),
                    revision: this.model.get('fileRevision')
                }, true)
            }));

            if (this.model.get('diffAgainstFileAttachmentID') !== null) {
                captionItems.push(this.captionItemTemplate({
                    caption: interpolate(gettext('%(caption)s (revision %(revision)s)'), {
                        caption: this.model.get('diffCaption'),
                        revision: this.model.get('diffRevision')
                    }, true)
                }));
            }

            $header.append(this.captionTableTemplate({
                items: captionItems.join('')
            }));
        } else {
            $('<h1 class="caption file-attachment-single-revision">').text(this.model.get('caption')).appendTo($header);
        }
    },


    /**
     * Callback for when a new file revision is selected.
     *
     * This supports single revisions and diffs. If 'base' is 0, a
     * single revision is selected, If not, the diff between `base` and
     * `tip` will be shown.
     *
     * Args:
     *     revisions (array of number):
     *         An array with two elements, representing the range of revisions
     *         to display.
     */
    _onRevisionSelected: function _onRevisionSelected(revisions) {
        var _revisions = _slicedToArray(revisions, 2),
            base = _revisions[0],
            tip = _revisions[1];

        // Ignore clicks on No Diff Label.


        if (tip === 0) {
            return;
        }

        var revisionIDs = this.model.get('attachmentRevisionIDs');
        var revisionTip = revisionIDs[tip - 1];

        /*
         * Eventually these hard redirects will use a router
         * (see diffViewerPageView.js for example)
         * this.router.navigate(base + '-' + tip + '/', {trigger: true});
         */
        var redirectURL = void 0;

        if (base === 0) {
            redirectURL = '../' + revisionTip + '/';
        } else {
            var revisionBase = revisionIDs[base - 1];
            redirectURL = '../' + revisionBase + '-' + revisionTip + '/';
        }

        window.location.replace(redirectURL);
    }
});

//# sourceMappingURL=dummyReviewableView.js.map