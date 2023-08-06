'use strict';

/**
 * Model for the review request page.
 *
 * This manages state specific to the review request page, and handles
 * watching for server-side updates relevant to entries and UI on the page.
 */
RB.ReviewRequestPage.ReviewRequestPage = RB.ReviewablePage.extend({
    defaults: _.defaults({
        updatesURL: null
    }, RB.ReviewablePage.prototype.defaults),

    /**
     * Initialize the model.
     */
    initialize: function initialize() {
        RB.ReviewablePage.prototype.initialize.apply(this, arguments);

        this._watchedEntries = {};
        this._watchedUpdatesPeriodMS = null;
        this._watchedUpdatesTimeout = null;
        this._watchedUpdatesLastScheduleTime = null;

        this.entries = new Backbone.Collection([], {
            model: RB.ReviewRequestPage.Entry
        });
    },


    /**
     * Parse the data for the page.
     *
     * This will take data from the server and turn it into a series of
     * objects and attributes needed for parts of the page.
     *
     * Args:
     *     rsp (object):
     *         The incoming data provided for the page.
     *
     * Returns:
     *     object:
     *     The resulting attributes for the page.
     */
    parse: function parse(rsp) {
        return _.extend({
            updatesURL: rsp.updatesURL
        }, RB.ReviewablePage.prototype.parse.call(this, rsp));
    },


    /**
     * Add an entry to the page.
     *
     * The entry's ``page`` attribute will be set to this page, for reference,
     * and then the entry will be added to the ``entries`` collection.
     *
     * Args:
     *     entry (RB.ReviewRequestPage.Entry):
     *         The entry to add.
     */
    addEntry: function addEntry(entry) {
        entry.set('page', this);
        this.entries.add(entry);
    },


    /**
     * Watch for updates to an entry.
     *
     * The entry will be checked for updates at least once every ``periodMS``
     * milliseconds.
     *
     * Args:
     *     entry (RB.ReviewRequestPage.Entry):
     *         The entry being watched for updates.
     *
     *     periodMS (number):
     *         The frequency at which the updates should be polled. Updates
     *         will be checked at least this often.
     */
    watchEntryUpdates: function watchEntryUpdates(entry, periodMS) {
        /*
         * If we already have a check in progress, and this new update
         * request wants to check sooner than the current check is scheduled,
         * then disconnect the old timer so we can reconnect it with the new
         * delay.
         */
        if (this._watchedUpdatesPeriodMS === null || periodMS < this._watchedUpdatesPeriodMS) {
            /*
             * This is either the only update requested, or it's more frequent
             * than other ones. Now we just need to check if we need to cancel
             * any previous update checks that are scheduled later than the
             * new check would be.
             */
            if (this._watchedUpdatesTimeout !== null && Date.now() - this._watchedUpdatesLastScheduleTime > periodMS) {
                clearTimeout(this._watchedUpdatesTimeout);
                this._watchedUpdatesTimeout = null;
            }

            this._watchedUpdatesPeriodMS = periodMS;
        }

        this._watchedEntries[entry.id] = {
            entry: entry,
            periodMS: periodMS
        };

        this._scheduleCheckUpdates();
    },


    /**
     * Stop watching for updates to an entry.
     *
     * Args:
     *     entry (RB.ReviewRequestPage.Entry):
     *         The entry being watched for updates.
     */
    stopWatchingEntryUpdates: function stopWatchingEntryUpdates(entry) {
        if (!this._watchedEntries.hasOwnProperty(entry.id)) {
            return;
        }

        delete this._watchedEntries[entry.id];

        /*
         * We'll either be clearing this for now, or recomputing. Either way,
         * we want this null for the next steps.
         */
        this._watchedUpdatesPeriodMS = null;

        if (_.isEmpty(this._watchedEntries)) {
            /*
             * There's nothing left to watch, so cancel the timeout (if set)
             * and clear state.
             */
            if (this._watchedUpdatesTimeout !== null) {
                clearTimeout(this._watchedUpdatesTimeout);
                this._watchedUpdatesTimeout = null;
            }

            this._watchedUpdatesLastScheduleTime = null;
        } else {
            /*
             * There's still other entries being watched. We need to
             * update state accordingly.
             *
             * We'll let any current timeouts continue as-is.
             */
            for (var key in this._watchedEntries) {
                if (this._watchedEntries.hasOwnProperty(key)) {
                    var periodMS = this._watchedEntries[key].periodMS;

                    this._watchedUpdatesPeriodMS = this._watchedUpdatesPeriodMS === null ? periodMS : Math.min(this._watchedUpdatesPeriodMS, periodMS);
                }
            }
        }
    },


    /**
     * Schedule the next updates check.
     *
     * The check will only be scheduled so long as there are still entries
     * being watched. Any data returned in the check will trigger reloads
     * of parts of the page.
     */
    _scheduleCheckUpdates: function _scheduleCheckUpdates() {
        var _this = this;

        if (this._watchedUpdatesTimeout !== null || this._watchedUpdatesPeriodMS === null) {
            return;
        }

        this._watchedUpdatesLastScheduleTime = Date.now();
        this._watchedUpdatesTimeout = setTimeout(function () {
            _this._watchedUpdatesTimeout = null;
            _this._loadUpdates({
                entries: _.pluck(_this._watchedEntries, 'entry'),
                onDone: _this._scheduleCheckUpdates.bind(_this)
            });
        }, this._watchedUpdatesPeriodMS);
    },


    /**
     * Load updates from the server.
     *
     * Args:
     *     options (object, optional):
     *         Options that control the types of updates loaded from the
     *         server.
     *
     * Option Args:
     *     entries (Array):
     *         A list of entry models that need to be checked for updates.
     *
     *     onDone (function, optional):
     *         Optional function to call after everything is loaded.
     */
    _loadUpdates: function _loadUpdates() {
        var _this2 = this;

        var options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};

        var updatesURL = this.get('updatesURL');
        var allEntryIDs = {};
        var entries = options.entries || [];

        var urlQuery = [];

        if (entries.length > 0) {
            for (var i = 0; i < entries.length; i++) {
                var entry = entries[i];
                var typeID = entry.get('typeID');

                if (!allEntryIDs.hasOwnProperty(typeID)) {
                    allEntryIDs[typeID] = [];
                }

                allEntryIDs[typeID].push(entry.id);
            }

            var urlEntryTypeIDs = [];

            for (var entryTypeID in allEntryIDs) {
                if (allEntryIDs.hasOwnProperty(entryTypeID)) {
                    /*
                     * Sort the IDs numerically, so that we have a stable URL
                     * for caching.
                     */
                    allEntryIDs[entryTypeID].sort(function (a, b) {
                        return a - b;
                    });

                    var entryIDs = allEntryIDs[entryTypeID].join(',');
                    urlEntryTypeIDs.push(entryTypeID + ':' + entryIDs);
                }
            }

            urlQuery.push('entries=' + urlEntryTypeIDs.join(';'));
        }

        /*
         * Like above, sort the URL queries, so that we have a stable URL
         * for caching.
         */
        urlQuery.sort();

        var urlQueryStr = urlQuery.length > 0 ? '?' + urlQuery.join('&') : '';

        Backbone.sync('read', this, {
            url: '' + updatesURL + urlQueryStr,
            dataType: 'arraybuffer',
            noActivityIndicator: true,
            success: function success(arrayBuffer) {
                return _this2._processUpdatesFromPayload(arrayBuffer, options.onDone);
            }
        });
    },


    /**
     * Process an updates payload from the server.
     *
     * This will parse the payload and then update each of the entries
     * or other parts of the UI referenced.
     *
     * Args:
     *     arrayBuffer (ArrayBuffer):
     *         The array buffer being parsed.
     *
     *     onDone (function, optional):
     *         The function to call when all updates have been parsed and
     *         applied.
     */
    _processUpdatesFromPayload: function _processUpdatesFromPayload(arrayBuffer, onDone) {
        var _this3 = this;

        var dataView = new DataView(arrayBuffer);
        var len = dataView.byteLength;
        var pos = 0;
        var totalUpdates = 0;
        var totalApplied = 0;
        var done = false;

        var onUpdateLoaded = function onUpdateLoaded(metadata, html) {
            /*
             * Based on the update, we can now start updating the UI, if
             * we can find the matching entry or UI component.
             */
            if (metadata.type === 'entry') {
                _this3._processEntryUpdate(metadata, html);
            } else {
                _this3._reloadFromUpdate(null, metadata, html);
            }

            totalApplied++;

            if (done && totalApplied === totalUpdates) {
                _this3.trigger('updatesProcessed');

                if (_.isFunction(onDone)) {
                    onDone();
                }
            }
        };

        while (!done) {
            var parsed = this._processUpdateFromPayload(arrayBuffer, dataView, pos);

            totalUpdates++;
            pos = parsed.pos;
            done = pos >= len;

            parsed.load(onUpdateLoaded);
        }
    },


    /**
     * Process a single update from the updates payload.
     *
     * This will parse out the details for one update, loading in the metadata
     * and HTML, and then apply that update.
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
     *         A function for loading the update content. This takes a
     *         callback function as an argument containing ``metadata`` and
     *         ``html`` arguments.
     */
    _processUpdateFromPayload: function _processUpdateFromPayload(arrayBuffer, dataView, pos) {
        /* Read the length of the metadata. */
        var metadataLen = dataView.getUint32(pos, true);
        pos += 4;

        /* Read the start position of the metadata content for later. */
        var metadataStart = pos;
        pos += metadataLen;

        /* Read the length of the HTML content. */
        var htmlLen = dataView.getUint32(pos, true);
        pos += 4;

        /* Read the start position of the HTML content for later. */
        var htmlStart = pos;
        pos += htmlLen;

        return {
            pos: pos,
            load: function load(cb) {
                var metadataBlob = new Blob([arrayBuffer.slice(metadataStart, metadataStart + metadataLen)]);
                var htmlBlob = new Blob([arrayBuffer.slice(htmlStart, htmlStart + htmlLen)]);

                RB.DataUtils.readManyBlobsAsStrings([metadataBlob, htmlBlob], function (metadata, html) {
                    return cb(JSON.parse(metadata), html);
                });
            }
        };
    },


    /**
     * Process the update to an entry.
     *
     * This will locate the existing entry on the page, check if it needs
     * updating, and then update the entry's attributes and HTML.
     *
     * Args:
     *     metadata (object):
     *         The metadata for the entry update.
     *
     *     html (string):
     *         The new HTML for the entry.
     */
    _processEntryUpdate: function _processEntryUpdate(metadata, html) {
        /*
         * TODO: We'll eventually want to handle new entries we don't
         *       know about. This would be part of a larger dynamic
         *       page updates change.
         */
        var entry = this.entries.get(metadata.entryID);

        if (!entry) {
            return;
        }

        console.assert(entry.get('typeID') === metadata.entryType);

        /* Only reload this entry if its updated timestamp has changed. */
        var newTimestamp = new Date(metadata.updatedTimestamp);

        if (newTimestamp <= entry.get('updatedTimestamp')) {
            return;
        }

        this._reloadFromUpdate(entry, metadata, html);
    },


    /**
     * Reload a component's attributes and HTML based on an update.
     *
     * This will update the attributes for a model, notifying listeners of
     * each stage of the update so that models and views can react
     * appropriately.
     *
     * If the model has ``beforeApplyUpdate`` and/or ``afterApplyUpdate``
     * methods, they'll be called before and after any updates are made,
     * respectively.
     *
     * Args:
     *     model (Backbone.Model):
     *         The model to update.
     *
     *     metadata (object):
     *         The metadata for the update.
     *
     *     html (string):
     *         The new HTML for the view.
     */
    _reloadFromUpdate: function _reloadFromUpdate(model, metadata, html) {
        this.trigger('applyingUpdate:' + metadata.type, metadata, html);

        if (model) {
            this.trigger('applyingUpdate:' + metadata.type + ':' + model.id, metadata, html);

            if (_.isFunction(model.beforeApplyUpdate)) {
                model.beforeApplyUpdate(metadata);
            }

            if (metadata.modelData) {
                model.set(model.parse(_.extend({}, model.attributes, metadata.modelData)));
            }

            this.trigger('appliedModelUpdate:' + metadata.type + ':' + model.id, metadata, html);

            if (_.isFunction(model.afterApplyUpdate)) {
                model.afterApplyUpdate(metadata);
            }

            this.trigger('appliedUpdate:' + metadata.type + ':' + model.id, metadata, html);
        }

        this.trigger('appliedUpdate:' + metadata.type, metadata, html);
    }
});

//# sourceMappingURL=reviewRequestPageModel.js.map