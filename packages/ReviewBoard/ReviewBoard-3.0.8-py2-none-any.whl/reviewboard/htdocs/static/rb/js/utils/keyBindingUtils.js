'use strict';

/**
 * A mixin for views that provides key binding functionality.
 *
 * Views using this mixin can provide a keyBindings map that maps a set of
 * key characters to a function.
 */
RB.KeyBindingsMixin = {
    /**
     * Enable key bindings for the view.
     *
     * Begins listening for any key bindings registered in the view's
     * keyBindings map, and calls the appropriate function.
     *
     * By default, this is called automatically when setting up the view,
     * by way of delegateEvents.
     */
    delegateKeyBindings: function delegateKeyBindings() {
        this.$el.on('keypress.keybindings.' + this.cid, _.bind(function (evt) {
            if (evt.altKey || evt.ctrlKey || evt.metaKey || evt.target.tagName === 'INPUT' || evt.target.tagName === 'TEXTAREA' || evt.target.isContentEditable) {
                /* These are all unsupported, and things we want to ignore. */
                return;
            }

            var keyChar = String.fromCharCode(evt.which);

            var _iteratorNormalCompletion = true;
            var _didIteratorError = false;
            var _iteratorError = undefined;

            try {
                for (var _iterator = Object.keys(this.keyBindings)[Symbol.iterator](), _step; !(_iteratorNormalCompletion = (_step = _iterator.next()).done); _iteratorNormalCompletion = true) {
                    var keys = _step.value;

                    if (keys.indexOf(keyChar) !== -1) {
                        evt.stopPropagation();
                        evt.preventDefault();

                        var func = this.keyBindings[keys];

                        if (!_.isFunction(func)) {
                            func = this[func];
                        }

                        func.call(this, evt);
                    }
                }
            } catch (err) {
                _didIteratorError = true;
                _iteratorError = err;
            } finally {
                try {
                    if (!_iteratorNormalCompletion && _iterator.return) {
                        _iterator.return();
                    }
                } finally {
                    if (_didIteratorError) {
                        throw _iteratorError;
                    }
                }
            }
        }, this));
    },


    /**
     * Disable key bindings for the view.
     *
     * By default, this is called automatically when calling undelegateEvents.
     */
    undelegateKeyBindings: function undelegateKeyBindings() {
        this.$el.off('keypress.keybindings.' + this.cid);
    },


    /**
     * Delegate both DOM events and key binding events.
     *
     * This overrides the default Backbone.View.delegateEvents to automatically
     * call delegateKeyBindings.
     */
    delegateEvents: function delegateEvents(events) {
        var result = Backbone.View.prototype.delegateEvents.call(this, events);

        this.delegateKeyBindings();

        return result;
    },


    /**
     * Undelegate both DOM events and key binding events.
     *
     * This overrides the default Backbone.View.undelegateEvents to
     * automatically call undelegateKeyBindings.
     */
    undelegateEvents: function undelegateEvents() {
        var result = Backbone.View.prototype.undelegateEvents.call(this);

        this.undelegateKeyBindings();

        return result;
    }
};

//# sourceMappingURL=keyBindingUtils.js.map