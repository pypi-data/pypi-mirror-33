'use strict';

(function () {

    var ParentView = RB.ReviewRequestPage.BaseStatusUpdatesEntryView;

    /**
     * Displays the "Review request changed" entry on the review request page.
     *
     * This handles any rendering needed for special contents in the box,
     * such as the diff complexity icons and the file attachment thumbnails.
     */
    RB.ReviewRequestPage.ChangeEntryView = ParentView.extend({
        /**
         * Initialize the view.
         *
         * Args:
         *     options (object):
         *          Options for the view.
         *
         * Option Args:
         *     reviewRequestEditorView (RB.ReviewRequestEditorView):
         *         The review request editor.
         */
        initialize: function initialize(options) {
            ParentView.prototype.initialize.apply(this, arguments);

            var reviewRequestEditor = this.model.get('reviewRequestEditor');

            this.reviewRequest = reviewRequestEditor.get('reviewRequest');
            this.reviewRequestEditorView = options.reviewRequestEditorView;

            this._$boxStatus = null;
            this._$fixItLabel = null;
        },


        /**
         * Render the view.
         *
         * Returns:
         *     RB.ReviewRequestPage.ChangeEntryView:
         *     This object, for chaining.
         */
        render: function render() {
            var _this = this;

            ParentView.prototype.render.call(this);

            this._$boxStatus = this.$('.box-status');
            this._$fixItLabel = $('<label class="fix-it-label">').hide().appendTo(this.$('.labels-container'));

            RB.formatText(this.$('.changedesc-text'), {
                bugTrackerURL: this.reviewRequest.get('bugTrackerURL'),
                isHTMLEncoded: true
            });

            this._updateLabels();

            _.each(this.$('.diff-index tr'), function (rowEl) {
                var $row = $(rowEl);
                var iconView = new RB.DiffComplexityIconView({
                    numInserts: $row.data('insert-count'),
                    numDeletes: $row.data('delete-count'),
                    numReplaces: $row.data('replace-count'),
                    totalLines: $row.data('total-line-count')
                });

                $row.find('.diff-file-icon').empty().append(iconView.$el);

                iconView.render();
            });

            _.each(this.$('.file-container'), function (thumbnailEl) {
                var $thumbnail = $(thumbnailEl);
                var $caption = $thumbnail.find('.file-caption .edit');
                var model = _this.reviewRequest.draft.createFileAttachment({
                    id: $thumbnail.data('file-id')
                });

                if (!$caption.hasClass('empty-caption')) {
                    model.set('caption', $caption.text());
                }

                _this.reviewRequestEditorView.buildFileAttachmentThumbnail(model, null, {
                    $el: $thumbnail,
                    canEdit: false
                });
            });

            return this;
        },


        /**
         * Set up a review view.
         *
         * This will begin listening for changes to the issue counts and
         * update the labels on the box.
         *
         * Args:
         *     view (RB.ReviewRequestPage.ReviewView):
         *         The review view being set up.
         */
        setupReviewView: function setupReviewView(view) {
            this.listenTo(view, 'openIssuesChanged', this._updateLabels);
        },


        /**
         * Update the "Fix It" label based on the open issue counts.
         *
         * If there are open issues, there will be a "Fix it!" label.
         */
        _updateLabels: function _updateLabels() {
            if (this._reviewViews.some(function (view) {
                return view.hasOpenIssues();
            })) {
                var openIssueCount = this._reviewViews.reduce(function (sum, view) {
                    return sum + view.getOpenIssueCount();
                }, 0);

                this._$boxStatus.addClass('has-issues');
                this._$fixItLabel.empty().append($('<span class="open-issue-count">').text(interpolate(gettext('%s failed'), [openIssueCount]))).append(document.createTextNode(gettext('Fix it!'))).show().css({
                    opacity: 1,
                    left: 0
                });
            } else {
                this._$fixItLabel.css({
                    opacity: 0,
                    left: '-100px'
                });
                this._$boxStatus.removeClass('has-issues');
            }
        }
    });
})();

//# sourceMappingURL=changeEntryView.js.map