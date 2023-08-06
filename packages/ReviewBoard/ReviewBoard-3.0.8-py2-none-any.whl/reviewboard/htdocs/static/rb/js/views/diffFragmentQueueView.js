'use strict';

/**
 * Queues loading of diff fragments from a page.
 *
 * This is used to load diff fragments one-by-one, and to intelligently
 * batch the loads to only fetch at most one set of fragments per file.
 */
RB.DiffFragmentQueueView = Backbone.View.extend({
    /**
     * Initialize the queue.
     *
     * Args:
     *     options (object):
     *         Options passed to this view.
     *
     * Returns:
     *     containerPrefix (string):
     *         The prefix to prepend to diff comment IDs when forming
     *         container element IDs.
     *
     *     diffFragmentViewOptions (object, optional):
     *         Options to pass to each :js:class:`RB.DiffFragmentView` that's
     *         created.
     *
     *     reviewRequestPath (string):
     *         The URL for the review request that diff fragments will be
     *         loaded from.
     *
     *     queueName (string):
     *         The name of the diff loading queue.
     */
    initialize: function initialize(options) {
        this._containerPrefix = options.containerPrefix;
        this._diffFragmentViewOptions = options.diffFragmentViewOptions;
        this._fragmentsBasePath = options.reviewRequestPath + '_fragments/diff-comments/';
        this._queueName = options.queueName;

        this._queue = {};
        this._saved = {};
    },


    /**
     * Queue the load of a diff fragment from the server.
     *
     * This will be added to a list, which will fetch the comments in batches
     * based on file IDs.
     *
     * Args:
     *     commentID (string):
     *         The ID of the comment to queue.
     *
     *     key (string):
     *         The key for the queue. Each comment with the same key will be
     *         loaded in a batch. This will generally be the ID of a file.
     *
     *     onFragmentRendered (function, optional):
     *         Optional callback for when the view for the fragment has
     *         rendered. Contains the view as a parameter.
     */
    queueLoad: function queueLoad(commentID, key, onFragmentRendered) {
        var queue = this._queue;

        if (!queue[key]) {
            queue[key] = [];
        }

        queue[key].push({
            commentID: commentID,
            onFragmentRendered: onFragmentRendered || null
        });
    },


    /**
     * Save a comment's loaded diff fragment for the next load operation.
     *
     * If the comment's diff fragment was already loaded, it will be
     * temporarily stored until the next load operation involving that
     * comment. Instead of loading the fragment from the server, the saved
     * fragment's HTML will be used instead.
     *
     * Args:
     *     commentID (string):
     *         The ID of the comment to save.
     */
    saveFragment: function saveFragment(commentID) {
        var $el = this._getCommentContainer(commentID);

        if ($el.length === 1 && $el.data('diff-fragment-view')) {
            this._saved[commentID] = $el.html();
        }
    },


    /**
     * Load all queued diff fragments.
     *
     * The diff fragments for each keyed set in the queue will be loaded as
     * a batch. The resulting fragments will be injected into the DOM.
     *
     * Any existing fragments that were saved will be loaded from the cache
     * without requesting them from the server.
     *
     * Args:
     *     onDone (function, optional):
     *         Callback for when all fragments have been loaded.
     */
    loadFragments: function loadFragments(onDone) {
        var _this = this;

        if (_.isEmpty(this._queue) && _.isEmpty(this._saved)) {
            if (_.isFunction(onDone)) {
                onDone();
            }

            return;
        }

        var queueName = this._queueName;

        _.each(this._queue, function (queuedLoads) {
            $.funcQueue(queueName).add(function () {
                var pendingCommentIDs = [];
                var onFragmentRenderedFuncs = {};

                /*
                 * Check if there are any comment IDs that have been saved.
                 * We don't need to reload these from the server.
                 */
                for (var i = 0; i < queuedLoads.length; i++) {
                    var queuedLoad = queuedLoads[i];
                    var commentID = queuedLoad.commentID;
                    var onFragmentRendered = _.isFunction(queuedLoad.onFragmentRendered) ? queuedLoad.onFragmentRendered : null;

                    if (_this._saved.hasOwnProperty(commentID)) {
                        var html = _this._saved[commentID];

                        var container = _this._getCommentContainer(commentID);
                        console.assert(container);

                        var view = container.data('diff-fragment-view');

                        if (view) {
                            view.$el.html(html);
                            view.render();
                        } else {
                            view = _this._renderFragment(container, commentID, html);
                        }

                        if (onFragmentRendered) {
                            onFragmentRendered(view);
                        }

                        delete _this._saved[commentID];
                    } else {
                        pendingCommentIDs.push(commentID);
                        onFragmentRenderedFuncs[commentID] = onFragmentRendered;
                    }
                }

                if (pendingCommentIDs.length > 0) {
                    /*
                     * There are some comment IDs we don't have. Load these
                     * from the server.
                     *
                     * Once these are loaded, they'll call next() on the queue
                     * to process the next batch.
                     */
                    _this._loadDiff(pendingCommentIDs.join(','), {
                        queueName: queueName,
                        onFragmentRendered: function onFragmentRendered(commentID, view) {
                            if (onFragmentRenderedFuncs[commentID]) {
                                onFragmentRenderedFuncs[commentID](view);
                            }
                        },
                        onDone: function onDone() {
                            return $.funcQueue(queueName).next();
                        }
                    });
                } else {
                    /*
                     * We processed all we need to process above. Go to the
                     * next queue.
                     */
                    $.funcQueue(queueName).next();
                }
            });
        });

        if (_.isFunction(onDone)) {
            $.funcQueue(queueName).add(function () {
                onDone();
                $.funcQueue(queueName).next();
            });
        }

        // Clear the list.
        this._queue = {};

        $.funcQueue(queueName).start();
    },


    /**
     * Return the container for a particular comment.
     *
     * Args:
     *     commentID (string):
     *         The ID of the comment.
     *
     * Returns:
     *     jQuery:
     *     The comment container, wrapped in a jQuery element. The caller
     *     may want to check the length to be sure the container was found.
     */
    _getCommentContainer: function _getCommentContainer(commentID) {
        return $('#' + this._containerPrefix + '_' + commentID);
    },


    /**
     * Load a diff fragment for the given comment IDs and options.
     *
     * This will construct the URL for the relevant diff fragment and load
     * it from the server.
     *
     * Args:
     *     commentIDs (string):
     *         A string of comment IDs to load fragments for.
     *
     *     options (object, optional):
     *         Options for the loaded diff fragments.
     *
     * Option Args:
     *     linesOfContext (string):
     *         The lines of context to load for the diff. This is a string
     *         containing a comma-separated set of line counts in the form
     *         of ``numLinesBefore,numLinesAfter``.
     *
     *     onDone (function):
     *         A function to call after the diff has been loaded.
     *
     *     queueName (string):
     *         The name of the load queue. This is used to load batches of
     *         fragments sequentially.
     */
    _loadDiff: function _loadDiff(commentIDs) {
        var _this2 = this;

        var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

        var containerPrefix = this._containerPrefix;
        var queryArgs = [];
        var onFragmentRendered = _.isFunction(options.onFragmentRendered) ? options.onFragmentRendered : null;

        if (options.linesOfContext !== undefined) {
            queryArgs.push('lines_of_context=' + options.linesOfContext);
        }

        if (!containerPrefix.includes('draft')) {
            queryArgs.push('allow_expansion=1');
        }

        queryArgs.push(TEMPLATE_SERIAL);

        RB.apiCall({
            url: '' + this._fragmentsBasePath + commentIDs + '/',
            data: queryArgs.join('&'),
            dataType: 'arraybuffer',
            type: 'GET',
            success: function success(arrayBuffer) {
                var dataView = new DataView(arrayBuffer);
                var len = dataView.byteLength;
                var pos = 0;
                var totalFragments = 0;
                var totalRenders = 0;
                var done = false;

                var onFragmentLoaded = function onFragmentLoaded(commentID, html) {
                    /* Set the HTML in the container. */
                    var containerID = '#' + containerPrefix + '_' + commentID;
                    var $container = $(containerID);

                    if ($container.length === 0) {
                        /*
                         * This doesn't actually exist. We may be dealing with
                         * inconsistent state due to something missing in the
                         * database. We don't want to break the page if this
                         * happens, so log and skip the entry.
                         */
                        console.error('Unable to find container %s for ' + 'comment ID %s. There may be missing ' + 'state in the database.', containerID, commentID);
                    } else {
                        var view = _this2._renderFragment($('#' + containerPrefix + '_' + commentID), commentID, html);

                        if (onFragmentRendered) {
                            onFragmentRendered(commentID, view);
                        }
                    }

                    totalRenders++;

                    if (done && totalRenders === totalFragments && _.isFunction(options.onDone)) {
                        /*
                         * We've parsed and rendered all fragments, so we're
                         * officially done.
                         */
                        options.onDone();
                    }
                };

                while (!done) {
                    var parsed = _this2._parseDiffFragmentFromPayload(arrayBuffer, dataView, pos);

                    totalFragments++;
                    pos = parsed.pos;
                    done = pos >= len;

                    parsed.load(onFragmentLoaded);
                }
            }
        });
    },


    /**
     * Parse a single diff fragment from the payload.
     *
     * This will parse out information about the fragment (the comment ID and
     * HTML) and return a response containing the new position and a function
     * to call in order to load the parsed fragment.
     *
     * Args:
     *     arrayBuffer (ArrayBuffer):
     *         The array buffer being parsed.
     *
     *     dataView (DataView):
     *         The data view on top of the array buffer, used to extract
     *         information.
     *
     *     pos (number):
     *         The current position within the array buffer.
     *
     * Returns:
     *     object:
     *     An object with two keys:
     *
     *     ``pos``:
     *         The next position to parse.
     *
     *     ``load``:
     *         A function for loading the fragment content. This takes a
     *         callback function as an argument containing ``commentID`` and
     *         ``html`` arguments.
     */
    _parseDiffFragmentFromPayload: function _parseDiffFragmentFromPayload(arrayBuffer, dataView, pos) {
        /* Read the comment ID. */
        var commentID = dataView.getUint32(pos, true);
        pos += 4;

        /* Read the length of the HTML. */
        var htmlLen = dataView.getUint32(pos, true);
        pos += 4;

        /* Read the HTML position for later. */
        var htmlStart = pos;
        pos += htmlLen;

        return {
            pos: pos,
            load: function load(cb) {
                RB.DataUtils.readBlobAsString(new Blob([arrayBuffer.slice(htmlStart, htmlStart + htmlLen)]), function (html) {
                    return cb(commentID, html);
                });
            }
        };
    },


    /**
     * Render a diff fragment on the page.
     *
     * This will set up a view for the diff fragment, if one is not already
     * created, and render it on the page.
     *
     * It will also mark the fragment for updates with the scroll manager
     * so that if the user is scrolled to a location past the fragment, the
     * resulting size change for the fragment won't cause the page to jump.
     *
     * Args:
     *     $container (jQuery):
     *         The container element where the fragment will be injected.
     *
     *     commentID (number):
     *         The ID of the comment.
     *
     *     html (string):
     *         The HTML contents of the fragment.
     */
    _renderFragment: function _renderFragment($container, commentID, html) {
        var _this3 = this;

        RB.scrollManager.markForUpdate($container);

        $container.html(html);

        var view = $container.data('diff-fragment-view');

        if (!view) {
            view = new RB.DiffFragmentView(_.defaults({
                el: $container,
                loadDiff: function loadDiff(options) {
                    RB.setActivityIndicator(true, { type: 'GET' });

                    _this3._loadDiff(commentID, _.defaults({
                        onDone: function onDone() {
                            RB.setActivityIndicator(false, {});

                            if (options.onDone) {
                                options.onDone();
                            }
                        }
                    }, options));
                }
            }, this._diffFragmentViewOptions));
            $container.data('diff-fragment-view', view);
        }

        view.render();

        RB.scrollManager.markUpdated($container);

        return view;
    }
});

//# sourceMappingURL=diffFragmentQueueView.js.map