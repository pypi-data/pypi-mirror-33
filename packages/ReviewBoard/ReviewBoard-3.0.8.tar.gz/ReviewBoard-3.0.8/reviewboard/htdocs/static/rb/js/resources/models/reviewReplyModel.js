'use strict';

/**
 * A review reply.
 *
 * Encapsulates replies to a top-level review.
 *
 * Model Attributes:
 *     forceTextType (string):
 *         The text type to request for text in all responses.
 *
 *     includeTextTypes (string):
 *         A comma-separated list of text types to include in responses.
 *
 *     rawTextFields (object):
 *         The contents of the raw text fields, if forceTextType is used and
 *         the caller fetches or posts with includeTextTypes=raw. The keys in
 *         this object are the field names, and the values are the raw versions
 *         of those attributes.
 *
 *     review (RB.Review):
 *         The review that this reply is replying to.
 *
 *     public (boolean):
 *         Whether this reply has been published.
 *
 *     bodyTop (string):
 *         The reply to the original review's ``bodyTop``.
 *
 *     bodyTopRichText (boolean):
 *         Whether the ``bodyTop`` field should be rendered as Markdown.
 *
 *     bodyBottom (string):
 *         The reply to the original review's ``bodyBottom``.
 *
 *     bodyBottomRichText (boolean):
 *         Whether the ``bodyBottom`` field should be rendered as Markdown.
 *
 *     timestamp (string):
 *         The timestamp of this reply.
 */
RB.ReviewReply = RB.BaseResource.extend({
    defaults: function defaults() {
        return _.defaults({
            forceTextType: null,
            includeTextTypes: null,
            rawTextFields: {},
            review: null,
            'public': false,
            bodyTop: null,
            bodyTopRichText: false,
            bodyBottom: null,
            bodyBottomRichText: false,
            timestamp: null
        }, RB.BaseResource.prototype.defaults());
    },


    rspNamespace: 'reply',
    listKey: 'replies',

    extraQueryArgs: {
        'force-text-type': 'html',
        'include-text-types': 'raw'
    },

    attrToJsonMap: {
        bodyBottom: 'body_bottom',
        bodyBottomRichText: 'body_bottom_text_type',
        bodyTop: 'body_top',
        bodyTopRichText: 'body_top_text_type',
        forceTextType: 'force_text_type',
        includeTextTypes: 'include_text_types'
    },

    serializedAttrs: ['forceTextType', 'includeTextTypes', 'bodyTop', 'bodyTopRichText', 'bodyBottom', 'bodyBottomRichText', 'public'],

    deserializedAttrs: ['bodyTop', 'bodyBottom', 'public', 'timestamp'],

    serializers: {
        forceTextType: RB.JSONSerializers.onlyIfValue,
        includeTextTypes: RB.JSONSerializers.onlyIfValue,
        bodyTopRichText: RB.JSONSerializers.textType,
        bodyBottomRichText: RB.JSONSerializers.textType,
        'public': function _public(value) {
            return value ? true : undefined;
        }
    },

    COMMENT_LINK_NAMES: ['diff_comments', 'file_attachment_comments', 'general_comments', 'screenshot_comments'],

    /**
     * Parse the response from the server.
     *
     * Args:
     *     rsp (object):
     *         The response from the server.
     *
     * Returns:
     *     object:
     *     The attribute values to set on the model.
     */
    parseResourceData: function parseResourceData(rsp) {
        var rawTextFields = rsp.raw_text_fields || rsp;
        var data = RB.BaseResource.prototype.parseResourceData.call(this, rsp);

        data.bodyTopRichText = rawTextFields.body_top_text_type === 'markdown';
        data.bodyBottomRichText = rawTextFields.body_bottom_text_type === 'markdown';
        data.rawTextFields = rsp.raw_text_fields || {};

        return data;
    },


    /**
     * Publish the reply.
     *
     * Before publishing, the "publishing" event will be triggered.
     * After successfully publishing, "published" will be triggered.
     *
     * Args:
     *     options (object):
     *         Options for the save operation.
     *
     *     context (object):
     *         Context to bind when calling callbacks.
     */
    publish: function publish() {
        var _this = this;

        var options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
        var context = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : undefined;

        this.trigger('publishing');

        this.ready({
            ready: function ready() {
                _this.set('public', true);
                _this.save({
                    data: {
                        'public': 1,
                        trivial: options.trivial ? 1 : 0
                    },
                    success: function success() {
                        _this.trigger('published');

                        if (_.isFunction(options.success)) {
                            options.success.call(context);
                        }
                    },
                    error: function error(model, xhr) {
                        model.trigger('publishError', xhr.errorText);

                        if (_.isFunction(options.error)) {
                            options.error.call(context, model, xhr);
                        }
                    }
                });
            }
        });
    },


    /**
     * Discard the reply if it's empty.
     *
     * If the reply doesn't have any remaining comments on the server, then
     * this will discard the reply.
     *
     * When we've finished checking, options.success will be called. It
     * will be passed true if discarded, or false otherwise.
     *
     * Args:
     *     options (object):
     *         Options for the save operation.
     *
     *     context (object):
     *         Context to bind when calling callbacks.
     */
    discardIfEmpty: function discardIfEmpty() {
        var _this2 = this;

        var options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};
        var context = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : undefined;

        options = _.bindCallbacks(options, context);

        this.ready({
            ready: function ready() {
                if (_this2.isNew() || _this2.get('bodyTop') || _this2.get('bodyBottom')) {
                    if (_.isFunction(options.success)) {
                        options.success(false);
                    }

                    return;
                }

                _this2._checkCommentsLink(0, options, context);
            },

            error: options.error
        });
    },


    /**
     * Check if there are comments, given the comment type.
     *
     * This is part of the discardIfEmpty logic.
     *
     * If there are comments, we'll give up and call options.success(false).
     *
     * If there are no comments, we'll move on to the next comment type. If
     * we're done, the reply is discarded, and options.success(true) is called.
     *
     * Args:
     *     linkNamesIndex (number):
     *         An index into the ``COMMENT_LINK_NAMES`` Array.
     *
     *     options (object):
     *         Options for the save operation.
     *
     *     context (object):
     *         Context to bind when calling callbacks.
     */
    _checkCommentsLink: function _checkCommentsLink(linkNameIndex, options, context) {
        var _this3 = this;

        var linkName = this.COMMENT_LINK_NAMES[linkNameIndex];
        var url = this.get('links')[linkName].href;

        RB.apiCall({
            type: 'GET',
            url: url,
            success: function success(rsp) {
                if (rsp[linkName].length > 0) {
                    if (_.isFunction(options.success)) {
                        options.success(false);
                    }
                } else if (linkNameIndex < _this3.COMMENT_LINK_NAMES.length - 1) {
                    _this3._checkCommentsLink(linkNameIndex + 1, options, context);
                } else {
                    _this3.destroy(_.defaults({
                        success: function success() {
                            if (_.isFunction(options.success)) {
                                options.success(true);
                            }
                        }
                    }, options), context);
                }
            },
            error: options.error
        });
    }
});
_.extend(RB.ReviewReply.prototype, RB.DraftResourceModelMixin);

//# sourceMappingURL=reviewReplyModel.js.map