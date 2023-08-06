'use strict';

(function () {

    /**
     * Base class for displaying a comment in the review dialog.
     */
    var BaseCommentView = Backbone.View.extend({
        tagName: 'li',

        thumbnailTemplate: null,

        events: {
            'click .delete-comment': '_deleteComment'
        },

        editorTemplate: _.template('<div class="edit-fields">\n <div class="edit-field">\n  <div class="comment-text-field">\n   <label class="comment-label" for="<%= id %>">\n    <%- commentText %>\n    <a href="#" role="button" class="delete-comment"\n       aria-label="<%- deleteCommentText %>"\n       title="<%- deleteCommentText %>"\n       ><span class="fa fa-trash-o" aria-hidden="true"></span></a>\n   </label>\n   <pre id="<%= id %>" class="reviewtext rich-text"\n        data-rich-text="true"><%- text %></pre>\n  </div>\n </div>\n <div class="edit-field">\n  <input class="issue-opened" id="<%= issueOpenedID %>"\n         type="checkbox">\n  <label for="<%= issueOpenedID %>"><%- openAnIssueText %></label>\n  <% if (showVerify) { %>\n   <input class="issue-verify" id="<%= verifyIssueID %>"\n          type="checkbox">\n   <label for="<%= verifyIssueID %>"><%- verifyIssueText %></label>\n  <% } %>\n </div>\n</div>'),

        _DELETE_COMMENT_TEXT: gettext('Are you sure you want to delete this comment?'),

        /**
         * Initialize the view.
         */
        initialize: function initialize() {
            this.$issueOpened = null;
            this.$editor = null;
            this.textEditor = null;
            this._origExtraData = _.clone(this.model.get('extraData'));

            this._hookViews = [];
        },


        /**
         * Remove the view.
         */
        remove: function remove() {
            this._hookViews.forEach(function (view) {
                return view.remove();
            });
            this._hookViews = [];

            Backbone.View.prototype.remove.call(this);
        },


        /**
         * Return whether or not the comment needs to be saved.
         *
         * The comment will need to be saved if the inline editor is currently
         * open.
         *
         * Returns:
         *     boolean:
         *     Whether the comment needs to be saved.
         */
        needsSave: function needsSave() {
            return this.inlineEditorView.isDirty() || !_.isEqual(this.model.get('extraData'), this._origExtraData);
        },


        /**
         * Save the final state of the view.
         *
         * Saves the inline editor and notifies the caller when the model is
         * synced.
         *
         * Args:
         *     options (object):
         *         Options for the model save operation.
         */
        save: function save(options) {
            /*
             * If the inline editor needs to be saved, ask it to do so. This will
             * call this.model.save(). If it does not, just save the model
             * directly.
             */
            if (this.inlineEditorView.isDirty()) {
                this.model.once('sync', function () {
                    return options.success();
                });
                this.inlineEditorView.submit();
            } else {
                this.model.save(_.extend({
                    attrs: ['forceTextType', 'includeTextTypes', 'extraData']
                }, options));
            }
        },


        /**
         * Render the comment view.
         *
         * Returns:
         *     BaseCommentView:
         *     This object, for chaining.
         */
        render: function render() {
            var _this = this;

            this.$el.addClass('draft').append(this.renderThumbnail()).append(this.editorTemplate({
                deleteCommentText: gettext('Delete comment'),
                commentText: gettext('Comment'),
                id: _.uniqueId('draft_comment_'),
                issueOpenedID: _.uniqueId('issue-opened'),
                openAnIssueText: gettext('Open an Issue'),
                text: this.model.get('text'),
                verifyIssueID: _.uniqueId('issue-verify'),
                showVerify: RB.EnabledFeatures.issueVerification,
                verifyIssueText: RB.CommentDialogView._verifyIssueText
            })).find('time.timesince').timesince().end();

            this.$issueOpened = this.$('.issue-opened').prop('checked', this.model.get('issueOpened')).change(function () {
                _this.model.set('issueOpened', _this.$issueOpened.prop('checked'));

                if (!_this.model.isNew()) {
                    /*
                     * We don't save the issueOpened attribute for unsaved
                     * models because the comment won't exist yet. If we did,
                     * clicking cancel when creating a new comment wouldn't
                     * delete the comment.
                     */
                    _this.model.save({
                        attrs: ['forceTextType', 'includeTextTypes', 'issueOpened']
                    });
                }
            });

            this._$issueVerify = this.$('.issue-verify').prop('checked', this.model.requiresVerification()).change(function () {
                var extraData = _.clone(_this.model.get('extraData'));
                extraData.require_verification = _this._$issueVerify.prop('checked');
                _this.model.set('extraData', extraData);

                if (!_this.model.isNew()) {
                    /*
                     * We don't save the extraData attribute for unsaved models
                     * because the comment won't exist yet. If we did, clicking
                     * cancel when creating a new comment wouldn't delete the
                     * comment.
                     */
                    _this.model.save({
                        attrs: ['forceTextType', 'includeTextTypes', 'extra_data.require_verification']
                    });
                }
            });

            var $editFields = this.$('.edit-fields');

            this.$editor = this.$('pre.reviewtext');

            this.inlineEditorView = new RB.RichTextInlineEditorView({
                el: this.$editor,
                editIconClass: 'rb-icon rb-icon-edit',
                notifyUnchangedCompletion: true,
                multiline: true,
                textEditorOptions: {
                    bindRichText: {
                        model: this.model,
                        attrName: 'richText'
                    }
                }
            });
            this.inlineEditorView.render();

            this.textEditor = this.inlineEditorView.textEditor;

            this.listenTo(this.inlineEditorView, 'complete', function (value) {
                var attrs = ['forceTextType', 'includeTextTypes', 'richText', 'text'];

                if (_this.model.isNew()) {
                    /*
                     * If this is a new comment, we have to send whether or not an
                     * issue was opened because toggling the issue opened checkbox
                     * before it is completed won't save the status to the server.
                     */
                    attrs.push('extra_data.require_verification', 'issueOpened');
                }

                _this.model.set({
                    text: value,
                    richText: _this.textEditor.richText
                });
                _this.model.save({
                    attrs: attrs
                });
            });

            this.listenTo(this.model, 'change:' + this._getRawValueFieldsName(), this._updateRawValue);
            this._updateRawValue();

            this.listenTo(this.model, 'saved', this.renderText);
            this.renderText();

            this.listenTo(this.model, 'destroying', function () {
                return _this.stopListening(_this.model);
            });

            RB.ReviewDialogCommentHook.each(function (hook) {
                var HookView = hook.get('viewType');
                var hookView = new HookView({
                    extension: hook.get('extension'),
                    model: _this.model
                });

                _this._hookViews.push(hookView);

                $('<div class="edit-field"/>').append(hookView.$el).appendTo($editFields);
                hookView.render();
            });

            return this;
        },


        /**
         * Render the thumbnail for this comment.
         *
         * Returns:
         *     jQuery:
         *     The rendered thumbnail element.
         */
        renderThumbnail: function renderThumbnail() {
            if (this.thumbnailTemplate === null) {
                return null;
            }

            return $(this.thumbnailTemplate(this.model.attributes));
        },


        /**
         * Render the text for this comment.
         */
        renderText: function renderText() {
            var reviewRequest = this.model.get('parentObject').get('parentObject');

            if (this.$editor) {
                RB.formatText(this.$editor, {
                    newText: this.model.get('text'),
                    richText: this.model.get('richText'),
                    isHTMLEncoded: true,
                    bugTrackerURL: reviewRequest.get('bugTrackerURL')
                });
            }
        },


        /**
         * Delete the comment associated with the model.
         */
        _deleteComment: function _deleteComment() {
            if (confirm(this._DELETE_COMMENT_TEXT)) {
                this.model.destroy();
            }
        },


        /**
         * Update the stored raw value of the comment text.
         *
         * This updates the raw value stored in the inline editor as a result of a
         * change to the value in the model.
         */
        _updateRawValue: function _updateRawValue() {
            if (this.$editor) {
                this.inlineEditorView.options.hasRawValue = true;
                this.inlineEditorView.options.rawValue = this.model.get(this._getRawValueFieldsName()).text;
            }
        },


        /**
         * Return the field name for the raw value.
         *
         * Returns:
         *     string:
         *     The field name to use, based on the whether the user wants to use
         *     Markdown or not.
         */
        _getRawValueFieldsName: function _getRawValueFieldsName() {
            return RB.UserSession.instance.get('defaultUseRichText') ? 'markdownTextFields' : 'rawTextFields';
        }
    });

    /**
     * Displays a view for diff comments.
     */
    var DiffCommentView = BaseCommentView.extend({
        thumbnailTemplate: _.template('<div class="review-dialog-comment-diff"\n     id="review_draft_comment_container_<%= id %>">\n <table class="sidebyside loading">\n  <thead>\n   <tr>\n    <th class="filename"><%- revisionText %></th>\n   </tr>\n  </thead>\n  <tbody>\n   <% for (var i = 0; i < numLines; i++) { %>\n    <tr><td><pre>&nbsp;</pre></td></tr>\n   <% } %>\n  </tbody>\n </table>\n</div>'),

        /**
         * Render the comment view.
         *
         * After rendering, this will queue up a load of the diff fragment
         * to display. The view will show a spinner until the fragment has
         * loaded.
         *
         * Returns:
         *     DiffCommentView:
         *     This object, for chaining.
         */
        render: function render() {
            BaseCommentView.prototype.render.call(this);

            var fileDiffID = this.model.get('fileDiffID');
            var interFileDiffID = this.model.get('interFileDiffID');

            this.options.diffQueue.queueLoad(this.model.id, interFileDiffID ? fileDiffID + '-' + interFileDiffID : fileDiffID);

            return this;
        },


        /**
         * Render the thumbnail.
         *
         * Returns:
         *     jQuery:
         *     The rendered thumbnail element.
         */
        renderThumbnail: function renderThumbnail() {
            var fileDiff = this.model.get('fileDiff');
            var interFileDiff = this.model.get('interFileDiff');
            var revisionText = void 0;

            if (interFileDiff) {
                revisionText = interpolate(gettext('%(filename)s (Diff revisions %(fileDiffRevision)s - %(interFileDiffRevision)s)'), {
                    filename: fileDiff.get('destFilename'),
                    fileDiffRevision: fileDiff.get('sourceRevision'),
                    inteFfileDiffRevision: interFileDiff.get('sourceRevision')
                }, true);
            } else {
                revisionText = interpolate(gettext('%(filename)s (Diff revision %(fileDiffRevision)s)'), {
                    filename: fileDiff.get('destFilename'),
                    fileDiffRevision: fileDiff.get('sourceRevision')
                }, true);
            }

            return $(this.thumbnailTemplate({
                id: this.model.get('id'),
                numLines: this.model.getNumLines(),
                revisionText: revisionText
            }));
        }
    });

    /**
     * Displays a view for file attachment comments.
     */
    var FileAttachmentCommentView = BaseCommentView.extend({
        thumbnailTemplate: _.template('<div class="file-attachment">\n <span class="filename">\n  <a href="<%- reviewURL %>"><%- linkText %></a>\n </span>\n <span class="diffrevision"><%- revisionsStr %></span>\n <div class="thumbnail"><%= thumbnailHTML %></div>\n</div>'),

        /**
         * Render the thumbnail.
         *
         * Returns:
         *     jQuery:
         *     The rendered thumbnail element.
         */
        renderThumbnail: function renderThumbnail() {
            var fileAttachment = this.model.get('fileAttachment');
            var diffAgainstFileAttachment = this.model.get('diffAgainstFileAttachment');
            var revision = fileAttachment.get('revision');
            var revisionsStr = void 0;

            if (!revision) {
                /* This predates having a revision. Don't show anything. */
                revisionsStr = '';
            } else if (diffAgainstFileAttachment) {
                revisionsStr = interpolate(gettext('(Revisions %(revision1)s - %(revision2)s)'), {
                    revision1: diffAgainstFileAttachment.get('revision'),
                    revision2: revision
                }, true);
            } else {
                revisionsStr = interpolate(gettext('(Revision %s)'), [revision]);
            }

            return $(this.thumbnailTemplate(_.defaults({
                revisionsStr: revisionsStr
            }, this.model.attributes)));
        }
    });

    /**
     * Displays a view for general comments.
     */
    var GeneralCommentView = BaseCommentView.extend({
        thumbnailTemplate: null
    });

    /**
     * Displays a view for screenshot comments.
     */
    var ScreenshotCommentView = BaseCommentView.extend({
        thumbnailTemplate: _.template('<div class="screenshot">\n <span class="filename">\n  <a href="<%- screenshot.reviewURL %>"><%- displayName %></a>\n </span>\n <img src="<%= thumbnailURL %>" width="<%= width %>"\n      height="<%= height %>" alt="<%- displayName %>" />\n</div>'),

        /**
         * Render the thumbnail.
         *
         * Returns:
         *     jQuery:
         *     The rendered thumbnail element.
         */
        renderThumbnail: function renderThumbnail() {
            var screenshot = this.model.get('screenshot');

            return $(this.thumbnailTemplate(_.defaults({
                screenshot: screenshot.attributes,
                displayName: screenshot.getDisplayName()
            }, this.model.attributes)));
        }
    });

    /**
     * The header or footer for a review.
     */
    var HeaderFooterCommentView = Backbone.View.extend({
        tagName: 'li',

        editorTemplate: _.template('<div class="edit-fields">\n <div class="edit-field">\n  <div class="add-link-container">\n   <a href="#" class="add-link"><%- linkText %></a>\n  </div>\n  <div class="comment-text-field">\n   <label for="<%= id %>" class="comment-label">\n    <%- commentText %>\n   </label>\n   <pre id="<%= id %>" class="reviewtext rich-text"\n        data-rich-text="true"><%- text %></pre>\n  </div>\n </div>\n</div>'),

        events: {
            'click .add-link': 'openEditor'
        },

        /**
         * Initialize the view.
         *
         * Args:
         *     options (object):
         *         Options for the view.
         *
         * Option Args:
         *     propertyName (string):
         *         The property name to modify (either ``bodyTop`` or
         *         ``bodyBottom`)).
         *
         *     richTextPropertyName (string):
         *         The property name of the rich text field corresponding to the
         *         ``propertyName``.
         *
         *     linkText (string):
         *         The text to show in the "add" link.
         *
         *     commentText (string):
         *         The text to show in the label for the comment field.
         */
        initialize: function initialize(options) {
            this.propertyName = options.propertyName;
            this.richTextPropertyName = options.richTextPropertyName;
            this.linkText = options.linkText;
            this.commentText = options.commentText;

            this.$editor = null;
            this.textEditor = null;
        },


        /**
         * Set the text of the link.
         *
         * Args:
         *     linkText (string):
         *         The text to show in the "add" link.
         */
        setLinkText: function setLinkText(linkText) {
            this.$('.add-link').text(linkText);
        },


        /**
         * Render the view.
         *
         * Returns:
         *     HeaderFooterCommentView:
         *     This object, for chaining.
         */
        render: function render() {
            var _this2 = this;

            var text = this.model.get(this.propertyName);

            this.$el.addClass('draft').append(this.editorTemplate({
                commentText: this.commentText,
                id: this.propertyName,
                linkText: this.linkText,
                text: text || ''
            })).find('time.timesince').timesince().end();

            this.$editor = this.$('pre.reviewtext');

            this.inlineEditorView = new RB.RichTextInlineEditorView({
                el: this.$editor,
                editIconClass: 'rb-icon rb-icon-edit',
                notifyUnchangedCompletion: true,
                multiline: true,
                textEditorOptions: {
                    bindRichText: {
                        model: this.model,
                        attrName: this.richTextPropertyName
                    }
                }
            });
            this.inlineEditorView.render();

            this.textEditor = this.inlineEditorView.textEditor;

            this.listenTo(this.inlineEditorView, 'complete', function (value) {
                _this2.model.set(_this2.propertyName, value);
                _this2.model.set(_this2.richTextPropertyName, _this2.textEditor.richText);
                _this2.model.save({
                    attrs: [_this2.propertyName, _this2.richTextPropertyName, 'forceTextType', 'includeTextTypes']
                });
            });
            this.listenTo(this.inlineEditorView, 'cancel', function () {
                if (!_this2.model.get(_this2.propertyName)) {
                    _this2._$editorContainer.hide();
                    _this2._$linkContainer.show();
                }
            });

            this._$editorContainer = this.$('.comment-text-field');
            this._$linkContainer = this.$('.add-link-container');

            this.listenTo(this.model, 'change:' + this._getRawValueFieldsName(), this._updateRawValue);
            this._updateRawValue();

            this.listenTo(this.model, 'saved', this.renderText);
            this.renderText();
        },


        /**
         * Render the text for this comment.
         */
        renderText: function renderText() {
            if (this.$editor) {
                var text = this.model.get(this.propertyName);

                if (text) {
                    var reviewRequest = this.model.get('parentObject');

                    this._$editorContainer.show();
                    this._$linkContainer.hide();
                    RB.formatText(this.$editor, {
                        newText: text,
                        richText: this.model.get(this.richTextPropertyName),
                        isHTMLEncoded: true,
                        bugTrackerURL: reviewRequest.get('bugTrackerURL')
                    });
                } else {
                    this._$editorContainer.hide();
                    this._$linkContainer.show();
                }
            }
        },


        /**
         * Return whether or not the comment needs to be saved.
         *
         * The comment will need to be saved if the inline editor is currently
         * open.
         *
         * Returns:
         *     boolean:
         *     Whether the comment needs to be saved.
         */
        needsSave: function needsSave() {
            return this.inlineEditorView.isDirty();
        },


        /**
         * Save the final state of the view.
         *
         * Args:
         *     options (object):
         *         Options for the model save operation.
         */
        save: function save(options) {
            this.model.once('sync', function () {
                return options.success();
            });
            this.inlineEditorView.submit();
        },


        /**
         * Open the editor.
         *
         * This is used for the 'Add ...' link handler, as well as for the default
         * state of the dialog when there are no comments.
         *
         * Args:
         *     ev (Event):
         *         The event that triggered the action.
         *
         * Returns:
         *     boolean:
         *     false, always.
         */
        openEditor: function openEditor(ev) {
            this._$linkContainer.hide();
            this._$editorContainer.show();

            this.inlineEditorView.startEdit();

            if (ev) {
                ev.preventDefault();
            }

            return false;
        },


        /**
         * Delete the comment.
         *
         * This is a no-op, since headers and footers can't be deleted.
         */
        _deleteComment: function _deleteComment() {},


        /**
         * Update the stored raw value of the comment text.
         *
         * This updates the raw value stored in the inline editor as a result of a
         * change to the value in the model.
         */
        _updateRawValue: function _updateRawValue() {
            if (this.$editor) {
                var rawValues = this.model.get(this._getRawValueFieldsName());

                this.inlineEditorView.options.hasRawValue = true;
                this.inlineEditorView.options.rawValue = rawValues[this.propertyName];
            }
        },


        /**
         * Return the field name for the raw value.
         *
         * Returns:
         *     string:
         *     The field name to use, based on the whether the user wants to use
         *     Markdown or not.
         */
        _getRawValueFieldsName: function _getRawValueFieldsName() {
            return RB.UserSession.instance.get('defaultUseRichText') ? 'markdownTextFields' : 'rawTextFields';
        }
    });

    /**
     * Creates a dialog for modifying a draft review.
     *
     * This provides editing capabilities for creating or modifying a new
     * review. The list of comments are retrieved from the server, providing
     * context for the comments.
     */
    RB.ReviewDialogView = Backbone.View.extend({
        id: 'review-form-comments',
        className: 'review',

        template: _.template('<div class="edit-field">\n <input id="id_shipit" type="checkbox" />\n <label for="id_shipit"><%- shipItText %></label>\n</div>\n<div class="review-dialog-hooks-container"></div>\n<div class="edit-field body-top"></div>\n<ol id="review-dialog-body-top-comments" class="review-comments"></ol>\n<ol id="review-dialog-general-comments" class="review-comments"></ol>\n<ol id="review-dialog-screenshot-comments" class="review-comments"></ol>\n<ol id="review-dialog-file-attachment-comments" class="review-comments"></ol>\n<ol id="review-dialog-diff-comments" class="review-comments"></ol>\n<ol id="review-dialog-body-bottom-comments" class="review-comments"></ol>\n<div class="spinner"><span class="fa fa-spinner fa-pulse"></span></div>\n<div class="edit-field body-bottom"></div>'),

        /**
         * Initialize the review dialog.
         */
        initialize: function initialize() {
            var _this3 = this;

            this._$diffComments = $();
            this._$fileAttachmentComments = $();
            this._$generalComments = $();
            this._$screenshotComments = $();
            this._$dlg = null;
            this._$buttons = null;
            this._$spinner = null;
            this._$shipIt = null;

            this._commentViews = [];
            this._hookViews = [];

            _.bindAll(this, '_onAddCommentClicked');

            var reviewRequest = this.model.get('parentObject');
            this._diffQueue = new RB.DiffFragmentQueueView({
                containerPrefix: 'review_draft_comment_container',
                reviewRequestPath: reviewRequest.get('reviewURL'),
                queueName: 'review_draft_diff_comments'
            });

            this._diffCommentsCollection = new RB.ResourceCollection([], {
                model: RB.DiffComment,
                parentResource: this.model,
                extraQueryData: {
                    'order-by': 'filediff,first_line'
                }
            });

            this._bodyTopView = new HeaderFooterCommentView({
                model: this.model,
                propertyName: 'bodyTop',
                richTextPropertyName: 'bodyTopRichText',
                linkText: gettext('Add header'),
                commentText: gettext('Header')
            });

            this._bodyBottomView = new HeaderFooterCommentView({
                model: this.model,
                propertyName: 'bodyBottom',
                richTextPropertyName: 'bodyBottomRichText',
                linkText: gettext('Add footer'),
                commentText: gettext('Footer')
            });

            this.listenTo(this._diffCommentsCollection, 'add', function (comment) {
                var view = new DiffCommentView({
                    model: comment,
                    diffQueue: _this3._diffQueue
                });
                _this3._renderComment(view, _this3._$diffComments);
            });

            this._fileAttachmentCommentsCollection = new RB.ResourceCollection([], {
                model: RB.FileAttachmentComment,
                parentResource: this.model
            });

            this.listenTo(this._fileAttachmentCommentsCollection, 'add', function (comment) {
                var view = new FileAttachmentCommentView({ model: comment });
                _this3._renderComment(view, _this3._$fileAttachmentComments);
            });

            this._$lastGeneralComment = null;

            this._generalCommentsCollection = new RB.ResourceCollection([], {
                model: RB.GeneralComment,
                parentResource: this.model
            });

            this.listenTo(this._generalCommentsCollection, 'add', function (comment) {
                var view = new GeneralCommentView({ model: comment });
                _this3._renderComment(view, _this3._$generalComments);
            });

            this._screenshotCommentsCollection = new RB.ResourceCollection([], {
                model: RB.ScreenshotComment,
                parentResource: this.model
            });

            this.listenTo(this._screenshotCommentsCollection, 'add', function (comment) {
                var view = new ScreenshotCommentView({ model: comment });
                _this3._renderComment(view, _this3._$screenshotComments);
            });

            this._defaultUseRichText = RB.UserSession.instance.get('defaultUseRichText');

            this._queryData = {
                'force-text-type': 'html'
            };

            if (this._defaultUseRichText) {
                this._queryData['include-text-types'] = 'raw,markdown';
            } else {
                this._queryData['include-text-types'] = 'raw';
            }

            this._setTextTypeAttributes(this.model);

            this.options.reviewRequestEditor.incr('editCount');
        },


        /**
         * Remove the dialog from the DOM.
         *
         * This will remove all the extension hook views from the dialog,
         * and then remove the dialog itself.
         */
        remove: function remove() {
            if (this._publishButton) {
                this._publishButton.remove();
                this._publishButton = null;
            }

            this._hookViews.forEach(function (view) {
                return view.remove();
            });
            this._hookViews = [];

            _super(this).remove.call(this);
        },


        /**
         * Close the review dialog.
         *
         * The dialog will be removed from the screen, and the "closed"
         * event will be triggered.
         */
        close: function close() {
            this.options.reviewRequestEditor.decr('editCount');
            this._$dlg.modalBox('destroy');
            this.trigger('closed');

            this.remove();
        },


        /**
         * Render the dialog.
         *
         * The dialog will be shown on the screen, and the comments from
         * the server will begin loading and rendering.
         *
         * Returns:
         *     RB.ReviewDialogView:
         *     This object, for chaining.
         */
        render: function render() {
            var _this4 = this;

            this.$el.html(this.template({
                addHeaderText: gettext('Add header'),
                addFooterText: gettext('Add footer'),
                shipItText: gettext('Ship It'),
                markdownDocsURL: MANUAL_URL + 'users/markdown/',
                markdownText: gettext('Markdown Reference')
            }));

            this._$diffComments = this.$('#review-dialog-diff-comments');
            this._$fileAttachmentComments = this.$('#review-dialog-file-attachment-comments');
            this._$generalComments = this.$('#review-dialog-general-comments');
            this._$screenshotComments = this.$('#review-dialog-screenshot-comments');
            this._$spinner = this.$('.spinner');
            this._$shipIt = this.$('#id_shipit');

            var $hooksContainer = this.$('.review-dialog-hooks-container');

            RB.ReviewDialogHook.each(function (hook) {
                var HookView = hook.get('viewType');
                var hookView = new HookView({
                    extension: hook.get('extension'),
                    model: _this4.model
                });

                _this4._hookViews.push(hookView);

                $hooksContainer.append(hookView.$el);
                hookView.render();
            });

            this._bodyTopView.$el.appendTo(this.$('#review-dialog-body-top-comments'));
            this._bodyBottomView.$el.appendTo(this.$('#review-dialog-body-bottom-comments'));

            /*
             * Even if the model is already loaded, we may not have the right text
             * type data. Force it to reload.
             */
            this.model.set('loaded', false);

            this.model.ready({
                data: this._queryData,
                ready: function ready() {
                    _this4._renderDialog();
                    _this4._bodyTopView.render();
                    _this4._bodyBottomView.render();

                    if (_this4.model.isNew() || _this4.model.get('bodyTop') === '') {
                        _this4._bodyTopView.openEditor();
                    }

                    if (_this4.model.isNew()) {
                        _this4._$spinner.remove();
                        _this4._$spinner = null;

                        _this4._handleEmptyReview();
                    } else {
                        _this4._$shipIt.prop('checked', _this4.model.get('shipIt'));
                        _this4._loadComments();
                    }

                    _this4.listenTo(_this4.model, 'change:bodyBottom', _this4._handleEmptyReview);
                }
            });

            return this;
        },


        /**
         * Load the comments from the server.
         *
         * This will begin chaining together the loads of each set of
         * comment types. Each loaded comment will be rendered to the
         * dialog once loaded.
         */
        _loadComments: function _loadComments() {
            var _this5 = this;

            var collections = [this._screenshotCommentsCollection, this._fileAttachmentCommentsCollection, this._diffCommentsCollection];

            if (RB.EnabledFeatures.generalComments) {
                /*
                 * Prepend the General Comments so they're fetched and shown
                 * first.
                 */
                collections.unshift(this._generalCommentsCollection);
            }

            this._loadCommentsFromCollection(collections, function () {
                _this5._$spinner.remove();
                _this5._$spinner = null;

                _this5._handleEmptyReview();
            });
        },


        /**
         * Properly set the view when the review is empty.
         */
        _handleEmptyReview: function _handleEmptyReview() {
            /*
             * We only display the bottom textarea if we have comments or the user
             * has previously set the bottom textarea -- we don't want the user to
             * not be able to remove their text.
             */
            if (this._commentViews.length === 0 && !this.model.get('bodyBottom')) {
                this._bodyBottomView.$el.hide();
                this._bodyTopView.setLinkText(gettext('Add text'));
            }
        },


        /**
         * Load the comments from a collection.
         *
         * This is part of the load comments flow. The list of remaining
         * collections are passed, and the first one will be removed
         * from the list and loaded.
         *
         * Args:
         *     collections (array):
         *         The list of collections left to load.
         *
         *     onDone (function):
         *         The function to call when all collections have been loaded.
         */
        _loadCommentsFromCollection: function _loadCommentsFromCollection(collections, onDone) {
            var _this6 = this;

            var collection = collections.shift();

            if (collection) {
                collection.fetchAll({
                    data: this._queryData,
                    success: function success() {
                        if (collection === _this6._diffCommentsCollection) {
                            _this6._diffQueue.loadFragments();
                        }

                        _this6._loadCommentsFromCollection(collections, onDone);
                    },
                    error: function error(rsp) {
                        // TODO: Provide better error output.
                        alert(rsp.errorText);
                    }
                });
            } else {
                onDone();
            }
        },


        /**
         * Render a comment to the dialog.
         *
         * Args:
         *     view (BaseCommentView):
         *         The view to render.
         *
         *     $container (jQuery):
         *         The container to add the view to.
         */
        _renderComment: function _renderComment(view, $container) {
            var _this7 = this;

            this._setTextTypeAttributes(view.model);

            this._commentViews.push(view);

            this.listenTo(view.model, 'destroyed', function () {
                view.$el.fadeOut({
                    complete: function complete() {
                        view.remove();
                        _this7._handleEmptyReview();
                    }
                });

                _this7._commentViews = _.without(_this7._commentViews, view);
            });

            $container.append(view.$el);
            view.render();

            this._$dlg.scrollTop(view.$el.position().top + this._$dlg.getExtents('p', 't'));
        },


        /**
         * Render the dialog.
         *
         * This will create and render a dialog to the screen, adding
         * this view's element as the child.
         */
        _renderDialog: function _renderDialog() {
            var _this8 = this;

            var $leftButtons = $('<div class="review-dialog-buttons-left"/>');
            var $rightButtons = $('<div class="review-dialog-buttons-right"/>');
            var buttons = [$leftButtons, $rightButtons];

            if (RB.EnabledFeatures.generalComments) {
                $leftButtons.append($('<input type="button" />').val(gettext('Add General Comment')).attr('title', gettext('Add a new general comment to the review')).click(this._onAddCommentClicked));
            }

            $rightButtons.append($('<div id="review-form-publish-split-btn-container" />'));

            $rightButtons.append($('<input type="button"/>').val(gettext('Discard Review')).click(function () {
                return _this8._onDiscardClicked();
            }));

            $rightButtons.append($('<input type="button"/>').val(gettext('Close')).click(function () {
                _this8._saveReview(false);
                return false;
            }));

            var reviewRequest = this.model.get('parentObject');

            this._$dlg = $('<div/>').attr('id', 'review-form').append(this.$el).modalBox({
                container: this.options.container || 'body',
                boxID: 'review-form-modalbox',
                title: interpolate(gettext('Review for: %s'), [reviewRequest.get('summary')]),
                stretchX: true,
                stretchY: true,
                buttons: buttons
            }).keypress(function (e) {
                return e.stopPropagation();
            }).attr('scrollTop', 0).trigger('ready');

            /* Must be done after the dialog is rendered. */

            this._publishButton = new RB.SplitButtonView({
                el: $('#review-form-publish-split-btn-container'),
                text: gettext('Publish Review'),
                click: function click() {
                    _this8._saveReview(true);
                    return false;
                },
                direction: 'up',
                alternatives: [{
                    text: gettext('... and only e-mail the owner'),
                    click: function click() {
                        _this8._saveReview(true, {
                            publishToOwnerOnly: true
                        });
                        _this8.close();
                        return false;
                    }
                }]
            });

            this._publishButton.render();

            this._$buttons = this._$dlg.modalBox('buttons');
        },


        /**
         * Handle a click on the "Add Comment" button.
         *
         * Returns:
         *     boolean:
         *     This always returns false to indicate that the dialog should not
         *     close.
         */
        _onAddCommentClicked: function _onAddCommentClicked() {
            var comment = this.model.createGeneralComment(undefined, RB.UserSession.instance.get('commentsOpenAnIssue'));

            this._generalCommentsCollection.add(comment);
            this._bodyBottomView.$el.show();
            this._commentViews[this._commentViews.length - 1].inlineEditorView.startEdit();

            return false;
        },


        /**
         * Handle a click on the "Discard Review" button.
         *
         * Prompts the user to confirm that they want the review discarded.
         * If they confirm, the review will be discarded.
         *
         * Returns:
         *     boolean:
         *     This always returns false to indicate that the dialog should not
         *     close.
         */
        _onDiscardClicked: function _onDiscardClicked() {
            var _this9 = this;

            var $cancelButton = $('<input type="button">').val(gettext('Cancel'));

            var $discardButton = $('<input type="button">').val(gettext('Discard')).click(function () {
                _this9.close();
                _this9.model.destroy({
                    success: function success() {
                        return RB.DraftReviewBannerView.instance.hideAndReload();
                    }
                });
            });

            $('<p/>').text(gettext('If you discard this review, all related comments will be permanently deleted.')).modalBox({
                title: gettext('Are you sure you want to discard this review?'),
                buttons: [$cancelButton, $discardButton]
            });

            return false;
        },


        /**
         * Save the review.
         *
         * First, this loops over all the comment editors and saves any which are
         * still in the editing phase.
         *
         * Args:
         *     publish (boolean):
         *         Whether the review should be published.
         *
         *     options (object):
         *         Options for the model save operation.
         */
        _saveReview: function _saveReview(publish) {
            var _this10 = this;

            var options = arguments.length > 1 && arguments[1] !== undefined ? arguments[1] : {};

            if (publish && options.publishToOwnerOnly) {
                this.model.set('publishToOwnerOnly', true);
            }

            this._$buttons.prop('disabled');

            var madeChanges = false;
            $.funcQueue('reviewForm').clear();

            function maybeSave(view) {
                if (view.needsSave()) {
                    $.funcQueue('reviewForm').add(function () {
                        madeChanges = true;
                        view.save({
                            success: function success() {
                                return $.funcQueue('reviewForm').next();
                            }
                        });
                    });
                }
            }

            maybeSave(this._bodyTopView);
            maybeSave(this._bodyBottomView);
            this._commentViews.forEach(function (view) {
                return maybeSave(view);
            });

            $.funcQueue('reviewForm').add(function () {
                var shipIt = _this10._$shipIt.prop('checked');
                var saveFunc = publish ? _this10.model.publish : _this10.model.save;

                if (_this10.model.get('public') === publish && _this10.model.get('shipIt') === shipIt) {
                    $.funcQueue('reviewForm').next();
                } else {
                    madeChanges = true;
                    _this10.model.set({
                        shipIt: shipIt
                    });

                    saveFunc.call(_this10.model, {
                        attrs: ['public', 'shipIt', 'forceTextType', 'includeTextTypes', 'publishToOwnerOnly'],
                        success: function success() {
                            return $.funcQueue('reviewForm').next();
                        },
                        error: function error() {
                            console.error('Failed to save review', arguments);
                        }
                    });
                }
            });

            $.funcQueue('reviewForm').add(function () {
                var reviewBanner = RB.DraftReviewBannerView.instance;

                _this10.close();

                if (reviewBanner) {
                    if (publish) {
                        reviewBanner.hideAndReload();
                    } else if (_this10.model.isNew() && !madeChanges) {
                        reviewBanner.hide();
                    } else {
                        reviewBanner.show();
                    }
                }
            });

            $.funcQueue('reviewForm').start();
        },


        /**
         * Set the text attributes on a model for forcing and including types.
         *
         * Args:
         *     model (Backbone.Model):
         *         The model to set the text type attributes on.
         */
        _setTextTypeAttributes: function _setTextTypeAttributes(model) {
            model.set({
                forceTextType: 'html',
                includeTextTypes: this._defaultUseRichText ? 'raw,markdown' : 'raw'
            });
        }
    }, {
        /*
         * Add some useful singletons to ReviewDialogView for managing the
         * review dialog.
         */

        _instance: null,

        /**
         * Create a ReviewDialogView.
         *
         * Only one is allowed on the screen at any given time.
         *
         * Args:
         *     options (object):
         *         Options for the dialog.
         *
         * Option Args:
         *     container (jQuery):
         *         The DOM container to attach the dialog to.
         *
         *     review (RB.Review):
         *         The review to show in this dialog.
         *
         *     reviewRequestEditor (RB.ReviewRequestEditor):
         *         The review request editor model.
         */
        create: function create() {
            var options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};

            console.assert(!RB.ReviewDialogView._instance, 'A ReviewDialogView is already opened');
            console.assert(options.review, 'A review must be specified');

            var dialog = new RB.ReviewDialogView({
                container: options.container,
                model: options.review,
                reviewRequestEditor: options.reviewRequestEditor
            });
            RB.ReviewDialogView._instance = dialog;

            dialog.render();

            dialog.on('closed', function () {
                RB.ReviewDialogView._instance = null;
            });

            return dialog;
        }
    });
})();

//# sourceMappingURL=reviewDialogView.js.map