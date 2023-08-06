'use strict';

/**
 * A view which ensures that the specified elements are vertically centered.
 */
RB.CenteredElementManager = Backbone.View.extend({
    /**
     * Initialize the view.
     *
     * Args:
     *     options (object):
     *         Options passed to this view.
     *
     * Option Args:
     *     elements (Array, optional):
     *         An initial array of elements to center.
     */
    initialize: function initialize() {
        var _this = this;

        var options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};

        this._elements = options.elements || new Map();
        this._$window = $(window);

        this._updatePositionThrottled = _.throttle(function () {
            return _this.updatePosition();
        }, 10);

        this._$window.on('resize', this._updatePositionThrottled);
        this._$window.on('scroll', this._updatePositionThrottled);
    },


    /**
     * Remove the CenteredElementManager.
     *
     * This will result in the event handlers being removed.
     */
    remove: function remove() {
        Backbone.View.prototype.remove.call(this);

        this._$window.off('resize', this._updatePositionThrottled);
        this._$window.off('scroll', this._updatePositionThrottled);
    },


    /**
     * Set the elements and their containers.
     *
     * Args:
     *     elements (Map<Element, Element or jQuery>):
     *         The elements to center within their respective containers.
     */
    setElements: function setElements(elements) {
        this._elements = elements;
    },


    /**
     * Update the position of the elements.
     *
     * This should only be done when the set of elements changed, as the view
     * will handle updating on window resizing and scrolling.
     */
    updatePosition: function updatePosition() {
        if (this._elements.size === 0) {
            return;
        }

        var windowTop = this._$window.scrollTop();
        var windowHeight = this._$window.height();
        var windowBottom = windowTop + windowHeight;

        this._elements.forEach(function (containers, el) {
            var $el = $(el);
            var $topContainer = containers.$top;
            var $bottomContainer = containers.$bottom || $topContainer;
            var containerTop = $topContainer.offset().top;
            var containerBottom = $bottomContainer.offset().top + $bottomContainer.height();

            /*
             * We don't have to vertically center the element when its
             * container is not on screen.
             */
            if (containerTop < windowBottom && containerBottom > windowTop) {
                /*
                 * When a container takes up the entire viewport, we can switch
                 * the CSS to use position: fixed. This way, we do not have to
                 * re-compute its position.
                 */
                if (windowTop >= containerTop && windowBottom <= containerBottom) {
                    if ($el.css('position') !== 'fixed') {
                        $el.css({
                            position: 'fixed',
                            left: $el.offset().left,
                            top: Math.round((windowHeight - $el.outerHeight()) / 2)
                        });
                    }
                } else {
                    var top = Math.max(windowTop, containerTop);
                    var bottom = Math.min(windowBottom, containerBottom);
                    var elTop = top - containerTop + Math.round((bottom - top - $el.outerHeight()) / 2);

                    $el.css({
                        position: 'absolute',
                        left: '',
                        top: elTop
                    });
                }
            }
        });
    }
});

//# sourceMappingURL=centeredElementManager.js.map