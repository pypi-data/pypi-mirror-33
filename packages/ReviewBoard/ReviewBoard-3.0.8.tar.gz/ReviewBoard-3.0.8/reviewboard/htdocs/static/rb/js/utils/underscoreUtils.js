'use strict';

var _slicedToArray = function () { function sliceIterator(arr, i) { var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"]) _i["return"](); } finally { if (_d) throw _e; } } return _arr; } return function (arr, i) { if (Array.isArray(arr)) { return arr; } else if (Symbol.iterator in Object(arr)) { return sliceIterator(arr, i); } else { throw new TypeError("Invalid attempt to destructure non-iterable instance"); } }; }();

/**
 * Bind callbacks to a context.
 *
 * Backbone.js's various ajax-related functions don't take a context
 * with their callbacks. This allows us to wrap these callbacks to ensure
 * we always have a desired context.
 *
 * Args:
 *     callbacks (object):
 *         An object which potentially includes callback functions.
 *
 *     context (any type):
 *         The context to bind to the callbacks.
 *
 *     methodNames (Array of string):
 *         An array of method names within ``callbacks`` to bind.
 *
 * Returns:
 *     object:
 *     A copy of the ``callbacks`` object, with the given ``methodNames`` bound
 *     to ``context``.
 */
_.bindCallbacks = function (callbacks, context) {
    var methodNames = arguments.length > 2 && arguments[2] !== undefined ? arguments[2] : ['success', 'error', 'complete'];

    if (!context) {
        return callbacks;
    }

    var wrappedCallbacks = {};

    var _iteratorNormalCompletion = true;
    var _didIteratorError = false;
    var _iteratorError = undefined;

    try {
        for (var _iterator = Object.entries(callbacks)[Symbol.iterator](), _step; !(_iteratorNormalCompletion = (_step = _iterator.next()).done); _iteratorNormalCompletion = true) {
            var _step$value = _slicedToArray(_step.value, 2),
                key = _step$value[0],
                value = _step$value[1];

            if (methodNames.includes(key) && _.isFunction(value)) {
                wrappedCallbacks[key] = _.bind(value, context);
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

    return _.defaults(wrappedCallbacks, callbacks);
};

/**
 * Return a function that will be called when the call stack has unwound.
 *
 * This will return a function that calls the provided function using
 * :js:func:`_.defer`.
 *
 * Args:
 *     func (function):
 *         The function to call.
 *
 * Returns:
 *     function:
 *     The wrapper function.
 */
_.deferred = function (func) {
    return function () {
        _.defer(func);
    };
};

/**
 * Return a function suitable for efficiently handling page layout.
 *
 * The returned function will use :js:func:`window.requestAnimationFrame` to
 * schedule the layout call. Once this function called, any subsequent calls
 * will be ignored until the first call has finished the layout work.
 *
 * Optionally, this can also defer layout work until the call stack has unwound.
 *
 * This is intended to be used as a resize event handler.
 *
 * Args:
 *     layoutFunc (function):
 *         The function to call to perform layout.
 *
 *     options (object):
 *         Options for the layout callback.
 *
 * Option Args:
 *     defer (boolean):
 *         If ``true``, the layout function will be called when the call stack
 *         has unwound after the next scheduled layout call.
 */
_.throttleLayout = function (layoutFunc) {
    var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

    var handlingLayout = false;

    /*
     * We don't want to use a fat arrow function here, since we need the
     * caller's context to be preserved.
     */
    return function () {
        if (handlingLayout) {
            return;
        }

        var context = this;
        var args = arguments;

        handlingLayout = true;

        var cb = function cb() {
            layoutFunc.apply(context, args);
            handlingLayout = false;
        };

        if (options.defer) {
            cb = _.deferred(cb);
        }

        requestAnimationFrame(cb);
    };
};

/*
 * Return the parent prototype for an object.
 *
 * Args:
 *     obj (object):
 *         An object.
 *
 * Returns:
 *     object:
 *     The object which is the parent prototype for the given ``obj``. This is
 *     roughly equivalent to what you'd get from ES6's ``super``.
 */
window._super = function (obj) {
    return Object.getPrototypeOf(Object.getPrototypeOf(obj));
};

//# sourceMappingURL=underscoreUtils.js.map