'use strict';

/**
 * Handles interaction for a review on the review request page. These can be
 * contained within the main review entries, but also for status updates in
 * change description entries or the initial status updates entry.
 */
RB.ReviewRequestPage.ReviewView = Backbone.View.extend({
    /**
     * Initialize the view.
     */
    initialize: function initialize(options) {
        var _this = this;

        this.options = options;
        this.entryModel = options.entryModel;

        this._bannerView = null;
        this._draftBannerShown = false;
        this._openIssueCount = 0;
        this._reviewReply = null;
        this._replyEditors = [];
        this._replyEditorViews = [];
        this._replyDraftsCount = 0;
        this._diffFragmentViews = [];

        this._$reviewComments = null;
        this._$bodyTop = null;
        this._$bodyBottom = null;

        this.model.set('includeTextTypes', 'html,raw,markdown');

        this._setupNewReply();

        this.listenTo(this.entryModel, 'change:collapsed', function () {
            if (!_this.entryModel.get('collapsed')) {
                _this._diffFragmentViews.forEach(function (view) {
                    return view.hideControls(false);
                });
            }
        });
    },


    /**
     * Render the view.
     *
     * Returns:
     *     RB.ReviewRequestPage.ReviewView:
     *     This object, for chaining.
     */
    render: function render() {
        var _this2 = this;

        var reviewRequestEditor = this.entryModel.get('reviewRequestEditor');

        this._$reviewComments = this.$('.review-comments');

        var $comment = this._$reviewComments.find('.review-comment-details .review-comment');
        this._$bodyTop = $comment.find('.body_top');
        this._$bodyBottom = $comment.find('.body_bottom');

        this._replyDraftsCount = 0;

        this.on('hasDraftChanged', function (hasDraft) {
            if (hasDraft) {
                _this2._showReplyDraftBanner();
            } else {
                _this2._hideReplyDraftBanner();
            }
        });

        _.each(this._$reviewComments.find('.issue-indicator'), function (el) {
            var $issueState = $('.issue-state', el);

            /*
             * Not all issue-indicator divs have an issue-state div for the
             * issue bar.
             */
            if ($issueState.length > 0) {
                var issueStatus = $issueState.data('issue-status');

                if (RB.BaseComment.isStateOpen(issueStatus)) {
                    _this2._openIssueCount++;
                }

                var issueBar = new RB.CommentIssueBarView({
                    el: el,
                    reviewID: _this2.model.id,
                    canVerify: $issueState.data('can-verify'),
                    commentID: $issueState.data('comment-id'),
                    commentType: $issueState.data('comment-type'),
                    interactive: $issueState.data('interactive'),
                    issueStatus: issueStatus
                });

                issueBar.render();

                _this2.listenTo(issueBar, 'statusChanged', function (oldStatus, newStatus) {
                    var oldOpen = RB.BaseComment.isStateOpen(oldStatus);
                    var newOpen = RB.BaseComment.isStateOpen(newStatus);

                    if (oldOpen !== newOpen) {
                        if (newOpen) {
                            _this2._openIssueCount++;
                        } else {
                            _this2._openIssueCount--;
                        }
                    }

                    _this2.trigger('openIssuesChanged');
                });
            }
        });

        _.each(this.$('.comment-section'), function (el) {
            var $el = $(el);
            var editor = new RB.ReviewRequestPage.ReviewReplyEditor({
                contextID: $el.data('context-id'),
                contextType: $el.data('context-type'),
                review: _this2.model,
                reviewReply: _this2._reviewReply
            });

            var view = new RB.ReviewRequestPage.ReviewReplyEditorView({
                el: el,
                model: editor,
                reviewRequestEditor: reviewRequestEditor
            });
            view.render();

            _this2.listenTo(editor, 'change:hasDraft', function (model, hasDraft) {
                if (hasDraft) {
                    _this2._replyDraftsCount++;
                    _this2.trigger('hasDraftChanged', true);
                } else {
                    _this2._replyDraftsCount--;

                    if (_this2._replyDraftsCount === 0) {
                        _this2.trigger('hasDraftChanged', false);
                    }
                }
            });

            _this2._replyEditors.push(editor);
            _this2._replyEditorViews.push(view);

            if (editor.get('hasDraft')) {
                _this2._replyDraftsCount++;
            }
        });

        if (this._replyDraftsCount > 0) {
            this.trigger('hasDraftChanged', true);
        }

        /*
         * Load any diff fragments for comments made on this review. Each
         * will be queued up and loaded when the page is rendered.
         */
        this._diffFragmentViews = [];

        var page = RB.PageManager.getPage();
        var diffCommentsData = this.entryModel.get('diffCommentsData');

        for (var i = 0; i < diffCommentsData.length; i++) {
            var diffCommentData = diffCommentsData[i];

            page.queueLoadDiff(diffCommentData[0], diffCommentData[1], function (view) {
                return _this2._diffFragmentViews.push(view);
            });
        }

        /*
         * Do this last, after ReviewReplyEditorView has already set up the
         * inline editors.
         */
        var reviewRequest = this.model.get('parentObject');
        var bugTrackerURL = reviewRequest.get('bugTrackerURL');
        _.each(this.$('pre.reviewtext'), function (el) {
            RB.formatText($(el), { bugTrackerURL: bugTrackerURL });
        });

        this.listenTo(this.model, 'change:bodyTop', this._onBodyTopChanged);
        this.listenTo(this.model, 'change:bodyBottom', this._onBodyBottomChanged);
        this.listenTo(this.model, 'change:bodyTopRichText', this._onBodyTopRichTextChanged);
        this.listenTo(this.model, 'change:bodyBottomRichText', this._onBodyBottomRichTextChanged);

        return this;
    },


    /**
     * Handler for when the Body Top field of a review changes.
     *
     * Updates the HTML for the field to show the new content.
     */
    _onBodyTopChanged: function _onBodyTopChanged() {
        this._$bodyTop.html(this.model.get('htmlTextFields').bodyTop);
    },


    /**
     * Handler for when the Body Top's Rich Text field of a review changes.
     *
     * Updates the class on the field to reflect the Rich Text state.
     */
    _onBodyTopRichTextChanged: function _onBodyTopRichTextChanged() {
        if (this.model.get('bodyTopRichText')) {
            this._$bodyTop.addClass('rich-text');
        } else {
            this._$bodyTop.removeClass('rich-text');
        }
    },


    /**
     * Handler for when the Body Bottom field of a review changes.
     *
     * Updates the HTML for the field to show the new content. The visibility
     * of the body section will also be dependent on whether there is any
     * content (mimicking the logic used when rendering the page).
     */
    _onBodyBottomChanged: function _onBodyBottomChanged() {
        var html = this.model.get('htmlTextFields').bodyBottom;

        this._$bodyBottom.html(html).closest('li').setVisible(html && html.length > 0);
    },


    /**
     * Handler for when the Body Bottom's Rich Text field of a review changes.
     *
     * Updates the class on the field to reflect the Rich Text state.
     */
    _onBodyBottomRichTextChanged: function _onBodyBottomRichTextChanged() {
        if (this.model.get('bodyBottomRichText')) {
            this._$bodyBottom.addClass('rich-text');
        } else {
            this._$bodyBottom.removeClass('rich-text');
        }
    },


    /**
     * Return whether there are any open issues in the review.
     *
     * Returns:
     *     boolean:
     *     true if there are any open issues.
     */
    hasOpenIssues: function hasOpenIssues() {
        return this._openIssueCount > 0;
    },


    /**
     * Return the number of open issues in the review.
     *
     * Returns:
     *     number:
     *     The number of open issues.
     */
    getOpenIssueCount: function getOpenIssueCount() {
        return this._openIssueCount;
    },


    /**
     * Return the ReviewReplyEditorView with the given context type and ID.
     *
     * Args:
     *     contextType (string):
     *         The type of object being replied to (such as ``body_top`` or
     *         ``diff_comments``)
     *
     *     contextID (number, optional):
     *         The ID of the comment being replied to, if appropriate.
     *
     * Returns:
     *     RB.ReviewRequestPage.ReviewReplyEditorView:
     *     The matching editor view.
     */
    getReviewReplyEditorView: function getReviewReplyEditorView(contextType, contextID) {
        if (contextID === undefined) {
            contextID = null;
        }

        return _.find(this._replyEditorViews, function (view) {
            var editor = view.model;
            return editor.get('contextID') === contextID && editor.get('contextType') === contextType;
        });
    },


    /**
     * Return the active reply.
     *
     * Returns:
     *     RB.ReviewReply:
     *     The active draft reply, or null if none exists.
     */
    getReviewReply: function getReviewReply() {
        return this._reviewReply;
    },


    /**
     * Set up a new ReviewReply for the editors.
     *
     * The new ReviewReply will be used for any new comments made on this
     * review.
     *
     * A ReviewReply is set until it's either destroyed or published, at
     * which point a new one is set.
     *
     * Args:
     *     reviewReply (RB.ReviewReply, optional):
     *         The reply object. If this is ``null``, a new ``RB.ReviewReply``
     *         will be created. Note that this argument is only expected to be
     *         used for unit testing.
     */
    _setupNewReply: function _setupNewReply(reviewReply) {
        var _this3 = this;

        if (!reviewReply) {
            reviewReply = this.model.createReply();
        }

        if (this._reviewReply !== null) {
            this.stopListening(this._reviewReply);

            // Update all the existing editors to point to the new object.
            this._replyEditors.forEach(function (editor) {
                return editor.set('reviewReply', reviewReply);
            });

            this.trigger('hasDraftChanged', false);
        }

        this.listenTo(reviewReply, 'destroyed published', function () {
            return _this3._setupNewReply();
        });

        this._reviewReply = reviewReply;
    },


    /**
     * Show the reply draft banner.
     *
     * This will be called in response to any new replies made on a review,
     * or if there are pending replies that already exist on the review.
     */
    _showReplyDraftBanner: function _showReplyDraftBanner() {
        if (!this._draftBannerShown) {
            this._bannerView = new RB.ReviewRequestPage.ReviewReplyDraftBannerView({
                model: this._reviewReply,
                $floatContainer: this.options.$bannerFloatContainer,
                noFloatContainerClass: this.options.bannerNoFloatContainerClass,
                reviewRequestEditor: this.entryModel.get('reviewRequestEditor')
            });

            this._bannerView.render();
            this._bannerView.$el.appendTo(this.options.$bannerParent);
            this._draftBannerShown = true;
        }
    },


    /**
     * Hide the reply draft banner.
     */
    _hideReplyDraftBanner: function _hideReplyDraftBanner() {
        if (this._draftBannerShown) {
            this._bannerView.remove();
            this._bannerView = null;
            this._draftBannerShown = false;
        }
    }
});

//# sourceMappingURL=reviewView.js.map