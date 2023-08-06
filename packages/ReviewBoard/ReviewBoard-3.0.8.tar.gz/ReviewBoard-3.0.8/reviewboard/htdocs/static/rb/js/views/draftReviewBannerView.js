'use strict';

/**
 * A banner that represents a pending draft review.
 *
 * The banner displays at the top of the page and provides buttons for
 * editing the review, publishing, and discarding.
 *
 * The banner is a singleton. There's only ever one at a time.
 */
RB.DraftReviewBannerView = Backbone.View.extend({
    events: {
        'click #review-banner-edit': '_onEditReviewClicked',
        'click #review-banner-discard': '_onDiscardClicked'
    },

    /**
     * Render the view.
     *
     * Returns:
     *     RB.DraftReviewBannerView:
     *     This object, for chaining.
     */
    render: function render() {
        var _this = this;

        this._$buttons = this.$('input');
        this._$banner = this.$('.banner');

        var model = this.model;
        this.listenTo(model, 'saving destroying', function () {
            return _this._$buttons.prop('disabled', true);
        });
        this.listenTo(model, 'saved destroyed', function () {
            return _this._$buttons.prop('disabled', false);
        });
        this.listenTo(model, 'publishError', function (errorText) {
            return alert(errorText);
        });

        this._publishButton = new RB.SplitButtonView({
            el: $('#review-banner-publish-container'),
            text: gettext('Publish Review'),
            click: _.bind(this._onPublishClicked, this),
            id: 'review-banner-publish',
            alternatives: [{
                text: gettext('... and only e-mail the owner'),
                click: function click() {
                    return _this._onPublishClicked({
                        publishToOwnerOnly: true
                    });
                },
                id: 'review-banner-publish-submitter-only'
            }]

        });

        this._publishButton.render();

        if (!this.$el.hasClass('hidden')) {
            this.show();
        }

        this.$el.addClass('ui-ready');

        return this;
    },


    /*
     * Show the banner.
     *
     * The banner will appear to slide down from the top of the page.
     */
    show: function show() {
        var height = this._$banner.outerHeight();

        RB.scrollManager.markForUpdate(this.$el);

        this.$el.removeClass('hidden').css({
            maxHeight: height,
            height: height
        });
        RB.scrollManager.scrollYOffset += height;
        RB.scrollManager.markUpdated(this.$el);
    },


    /*
     * Hide the banner.
     *
     * The banner will slide up to the top of the page.
     */
    hide: function hide() {
        var _this2 = this;

        RB.scrollManager.markForUpdate(this.$el);

        var height = this._$banner.outerHeight();

        this.$el.addClass('hidden').css('max-height', '');

        /*
         * If we set the height immediately, the browser will appear to not
         * animate, since it can't transition heights (only max-heights). So
         * we delay for a short period after we know the transition will have
         * completed.
         */
        _.delay(function () {
            _this2.$el.css('height', '');
            RB.scrollManager.markUpdated(_this2.$el);
            RB.scrollManager.scrollYOffset -= height;
        }, 500);
    },


    /**
     * Hide the banner and reloads the page.
     *
     * XXX Remove this function when we make the pages more dynamic.
     */
    hideAndReload: function hideAndReload() {
        var _this3 = this;

        this.hide();

        /*
         * hideAndReload might have been called from within a $.funcQueue.
         * With Firefox, later async functions that are queued in the
         * $.funcQueue will not run when we change window.location, which
         * means that we might miss out on some teardown that was
         * scheduled. We defer changing the location until the next tick
         * of the event loop to let any teardown occur.
         */
        _.defer(function () {
            window.location = _this3.model.get('parentObject').get('reviewURL');
        });
    },


    /**
     * Return the height of the banner.
     *
     * Returns:
     *     number:
     *     The height of the banner.
     */
    getHeight: function getHeight() {
        return this._$banner.outerHeight();
    },


    /**
     * Remove the banner from the page.
     */
    remove: function remove() {
        if (this._publishButton) {
            this._publishButton.remove();
        }

        _super(this).remove.call(this);
    },


    /**
     * Handler for the Edit Review button.
     *
     * Displays the review editor dialog.
     *
     * Returns:
     *     boolean:
     *     false, always.
     */
    _onEditReviewClicked: function _onEditReviewClicked() {
        RB.ReviewDialogView.create({
            review: this.model,
            reviewRequestEditor: this.options.reviewRequestEditor
        });

        return false;
    },


    /**
     * Handler for the Publish button.
     *
     * Publishes the review.
     *
     * Args:
     *     options (object):
     *         Options that determine special cases for submission.
     *
     * Option Args:
     *     publishToOwnerOnly (boolean):
     *         Whether or not we should only notify the submitter of the review.
     *
     * Returns:
     *     boolean:
     *     false, always.
     */
    _onPublishClicked: function _onPublishClicked() {
        var options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};

        if (options.publishToOwnerOnly) {
            this.model.set('publishToOwnerOnly', true);
        }

        this.model.publish({
            attrs: ['public', 'publishToOwnerOnly']
        });

        return false;
    },


    /**
     * Handler for the Discard button.
     *
     * Prompts the user to confirm that they want the review discarded.
     * If they confirm, the review will be discarded.
     *
     * Returns:
     *     boolean:
     *     false, always.
     */
    _onDiscardClicked: function _onDiscardClicked() {
        var _this4 = this;

        $('<p/>').text(gettext('If you discard this review, all related comments will be permanently deleted.')).modalBox({
            title: gettext('Are you sure you want to discard this review?'),
            buttons: [$('<input type="button">').val(gettext('Cancel')), $('<input type="button">').val(gettext('Discard')).click(function () {
                return _this4.model.destroy();
            })]
        });

        return false;
    }
}, {
    instance: null,

    /**
     * Create the draft review banner singleton.
     *
     * Returns:
     *     RB.DraftReviewBannerView:
     *     The banner view.
     */
    create: function create(options) {
        if (!this.instance) {
            this.instance = new RB.DraftReviewBannerView(options);
            this.instance.render();
        }

        return this.instance;
    }
});

//# sourceMappingURL=draftReviewBannerView.js.map