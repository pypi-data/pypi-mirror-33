'use strict';

/**
 * Manages the registration, display, and interaction of infoboxes.
 *
 * This view is responsible for tracking the various forms of infoboxes needed
 * on a page and handling their display when hovering over a target. It can
 * also create jQuery functions for registering elements with particular
 * infoboxes.
 *
 * There's only one instance used per page, accessed via
 * :js:func:`RB.InfoboxManagerView.getInstance`.
 */
RB.InfoboxManagerView = Backbone.View.extend({
    /** The delay after hovering over a target before displaying an infobox. */
    POPUP_DELAY_MS: 700,

    /** The delay after leaving a target before hiding an infobox. */
    HIDE_DELAY_MS: 400,

    /** The animation time for fading in an infobox. */
    FADE_IN_MS: 200,

    /** The animation time for fading out an infobox. */
    FADE_OUT_MS: 150,

    /**
     * Initialize the manager.
     */
    initialize: function initialize() {
        this._infoboxViews = {};
        this._activeInfoboxView = null;
        this._cache = {};
        this._showTimeout = null;
        this._hideTimeout = null;
    },


    /**
     * Remove the manager's infoboxes from the DOM.
     */
    remove: function remove() {
        Backbone.View.prototype.remove.call(this);

        for (var key in this._infoboxViews) {
            if (this._infoboxViews.hasOwnProperty(key)) {
                this._infoboxViews[key].remove();
            }
        }

        this._infoboxViews = {};
        this._cache = {};
        this._activeInfoboxView = null;
    },


    /**
     * Add one or more targets for a particular type of infobox.
     *
     * These targets will trigger the specified infobox when hovering over
     * them.
     *
     * Args:
     *     infoboxViewType (prototype):
     *         The type of infobox to register with. This must be a subclass
     *         of :js:class:`RB.BaseInfoboxView`.
     *
     *     $targets (jQuery):
     *         A set of jQuery targets to register with the infobox.
     */
    addTargets: function addTargets(infoboxViewType, $targets) {
        var _this = this;

        $targets.each(function (idx, target) {
            var $target = $(target);

            if (!$target.data('has-infobox')) {
                /*
                 * Note that we're wanting to bind the functions instead of
                 * using fat arrow functions in order to avoid having two
                 * new anonymous functions per target, which is wasteful and
                 * unnecessary.
                 */
                $target.data('has-infobox', true).on('mouseenter', _this._onTargetMouseEnter.bind(_this, $target, infoboxViewType)).on('mouseleave', _this._onMouseLeave.bind(_this));
            }
        });
    },


    /**
     * Set the positioning for a particular type of infobox.
     *
     * This is used to control how an infobox would be positioned on the
     * page, relative to the target element. It completely overrides the
     * default positioning for that type of infobox.
     *
     * Args:
     *     infoboxViewType (prototype):
     *         The type of infobox to alter the position for.
     *
     *     positioning (object):
     *         The positioning information. This must be a value compatible
     *         with :js:func:`$.fn.positionToSide`.
     */
    setPositioning: function setPositioning(infoboxViewType, positioning) {
        this.getOrCreateInfobox(infoboxViewType).positioning = positioning;
    },


    /**
     * Return an instance of a particular type of infobox.
     *
     * If the instance doesn't yet exist, it will be created and registered
     * with the manager.
     *
     * Args:
     *     InfoboxViewType (prototype):
     *         The type of infobox to return.
     *
     * Returns:
     *     RB.BaseInfoboxView:
     *     The resulting infobox instance.
     */
    getOrCreateInfobox: function getOrCreateInfobox(InfoboxViewType) {
        var infoboxID = InfoboxViewType.prototype.infoboxID;
        console.assert(infoboxID, 'RB.BaseInfoboxView subclasses must have an ' + 'infoboxID defined.');

        var view = this._infoboxViews[infoboxID];

        if (view) {
            return view;
        }

        view = new InfoboxViewType();
        view.$el.hide().on('mouseenter', this._onInfoboxMouseEnter.bind(this)).on('mouseleave', this._onMouseLeave.bind(this)).appendTo(document.body);

        this._infoboxViews[infoboxID] = view;

        return view;
    },


    /**
     * Load the contents for an infobox and display it.
     *
     * This will perform a HTTP GET on the infobox URL for the given target
     * and then show the infobox with those contents. If the URL has already
     * been fetched, the infobox will be displayed immediately and then the
     * contents replaced once fetched.
     *
     * Args:
     *     $target (jQuery):
     *         The jQuery target element the infobox is being shown for.
     *
     *     infoboxView (RB.BaseInfoboxView):
     *         The infobox view that will contain the HTML contents.
     */
    _loadInfobox: function _loadInfobox($target, infoboxView) {
        var _this2 = this;

        console.assert($target.length === 1, 'Too many targets matched when fetching infobox contents');

        var url = infoboxView.getURLForTarget($target);
        var cachedData = this._cache[url];

        if (cachedData !== undefined) {
            /*
             * If we have cached data, show that immediately and update once we
             * have the result from the server.
             */
            infoboxView.setContents(cachedData);
            this._showInfobox(infoboxView, $target);
        }

        this._fetchInfoboxContents(url, function (html) {
            _this2._cache[url] = html;
            infoboxView.setContents(html);

            if (cachedData === undefined) {
                _this2._showInfobox(infoboxView, $target);
            }
        });
    },


    /**
     * Fetch the contents for an infobox from the given URL.
     *
     * Args:
     *     url (string):
     *         The URL containing the infobox HTML.
     *
     *     onDone (function):
     *         The handler to call when the infobox HTML has been fetched.
     */
    _fetchInfoboxContents: function _fetchInfoboxContents(url, onDone) {
        $.ajax(url, {
            ifModified: true
        }).done(onDone);
    },


    /**
     * Display an infobox alongside the given target.
     *
     * Args:
     *     infoboxView (RB.BaseInfoboxView):
     *         The infobox instance to use.
     *
     *     $target (jQuery):
     *         The jQuery element to position the infobox beside.
     */
    _showInfobox: function _showInfobox(infoboxView, $target) {
        infoboxView.$el.positionToSide($target, _.defaults(infoboxView.positioning, {
            fitOnScreen: true
        })).fadeIn(this.FADE_IN_MS);

        this._activeInfoboxView = infoboxView;
    },


    /**
     * Hide the active infobox.
     */
    _hideInfobox: function _hideInfobox() {
        var _this3 = this;

        if (this._activeInfoboxView) {
            var curInfoboxView = this._activeInfoboxView;

            this._activeInfoboxView.$el.fadeOut(this.FADE_OUT_MS, function () {
                /*
                 * Only clear the active infobox if it hasn't been
                 * replaced with a new one.
                 */
                if (curInfoboxView === _this3._activeInfoboxView) {
                    _this3._activeInfoboxView = null;
                }
            });
        }
    },


    /**
     * Handler for when the mouse enters the infobox.
     *
     * This will prevent the infobox from being hidden after having left the
     * target.
     */
    _onInfoboxMouseEnter: function _onInfoboxMouseEnter() {
        clearTimeout(this._hideTimeout);
        this._hideTimeout = null;
    },


    /**
     * Handler for when the mouse enters a target.
     *
     * This will wait a small amount of time (in case the user is simply
     * temporarily mousing over the element) and then show the infobox.
     *
     * Args:
     *     $target (jQuery):
     *         The jQuery target element.
     *
     *     InfoboxViewType (prototype):
     *         The type of infobox to show.
     */
    _onTargetMouseEnter: function _onTargetMouseEnter($target, InfoboxViewType) {
        var _this4 = this;

        clearTimeout(this._hideTimeout);
        this._hideTimeout = null;

        this._showTimeout = setTimeout(function () {
            _this4._showTimeout = null;
            _this4._loadInfobox($target, _this4.getOrCreateInfobox(InfoboxViewType));
        }, this.POPUP_DELAY_MS);
    },


    /**
     * Handler for when the mouse leaves a target or infobox.
     *
     * If an existing infobox is currently on-screen, it will be faded
     * out after a brief delay (allowing time to move the mouse onto the
     * infobox or back onto the target).
     */
    _onMouseLeave: function _onMouseLeave() {
        var _this5 = this;

        // If we were going to show an infobox, cancel that.
        clearTimeout(this._showTimeout);
        this._showTimeout = null;

        // Check if we need to hide any current infobox.
        if (this._activeInfoboxView) {
            /*
             * We have an infobox on the screen, and the mouse is
             * leaving it. Since there's no other infobox queued up,
             * begin the process of fading it out, after a delay.
             */
            clearTimeout(this._hideTimeout);

            this._hideTimeout = setTimeout(function () {
                _this5._hideInfobox();
                _this5._hideTimeout = null;
            }, this.HIDE_DELAY_MS);
        }
    }
}, {
    _instance: null,

    /**
     * Return an instance of the infobox manager.
     *
     * If one does not already exist, it will be created.
     *
     * Callers should always use this instead of creating an instance
     * manually.
     *
     * Returns:
     *     RB.InfoboxManagerView:
     *     The infobox manager instance.
     */
    getInstance: function getInstance() {
        var instance = RB.InfoboxManagerView._instance;

        if (!instance) {
            instance = new RB.InfoboxManagerView();
            this._instance = instance;
        }

        return instance;
    },


    /**
     * Create a jQuery function for registering elements with an infobox.
     *
     * This is used to create ``$.fn.`` functions that will register all
     * matching elements as targets for a particular type of infobox.
     *
     * Args:
     *     infoboxViewType (prototype):
     *         The type of infobox to use for these elements.
     *
     * Returns:
     *     function:
     *     The resulting function. This should be assigned to a ``$.fn.``
     *     function.
     */
    createJQueryFn: function createJQueryFn(infoboxViewType) {
        return function () {
            RB.InfoboxManagerView.getInstance().addTargets(infoboxViewType, this);

            return this;
        };
    }
});

//# sourceMappingURL=infoboxManagerView.js.map