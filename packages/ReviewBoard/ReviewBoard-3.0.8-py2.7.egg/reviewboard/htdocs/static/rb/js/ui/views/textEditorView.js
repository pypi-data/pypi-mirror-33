'use strict';

(function () {

    /**
     * Wraps CodeMirror, providing a standard interface for TextEditorView's usage.
     */
    var CodeMirrorWrapper = Backbone.View.extend({
        /**
         * Initialize CodeMirrorWrapper.
         *
         * This will set up CodeMirror based on the objects, add it to the parent,
         * and begin listening to events.
         *
         * Args:
         *     options (object):
         *         Options for the wrapper.
         *
         * Option Args:
         *     autoSize (boolean):
         *         Whether the editor should automatically resize itself to fit its
         *         container.
         *
         *     parentEl (Element):
         *        The parent element for the editor.
         *
         *    minHeight (number):
         *        The minimum vertical size of the editor.
         */
        initialize: function initialize(options) {
            var _this = this;

            var codeMirrorOptions = {
                mode: {
                    name: 'gfm',
                    /*
                     *The following token type overrides will be prefixed with
                     * ``cm-`` when used as classes.
                     */
                    tokenTypeOverrides: {
                        code: 'rb-markdown-code',
                        list1: 'rb-markdown-list1',
                        list2: 'rb-markdown-list2',
                        list3: 'rb-markdown-list3'
                    }
                },
                theme: 'rb default',
                lineWrapping: true,
                electricChars: false,
                extraKeys: {
                    'Home': 'goLineLeft',
                    'End': 'goLineRight',
                    'Enter': 'newlineAndIndentContinueMarkdownList',
                    'Shift-Tab': false,
                    'Tab': false
                }
            };

            if (options.autoSize) {
                codeMirrorOptions.viewportMargin = Infinity;
            }

            this._codeMirror = new CodeMirror(options.parentEl, codeMirrorOptions);

            this.setElement(this._codeMirror.getWrapperElement());

            if (this.options.minHeight !== undefined) {
                this.$el.css('min-height', this.options.minHeight);
            }

            this._codeMirror.on('viewportChange', function () {
                return _this.$el.triggerHandler('resize');
            });
            this._codeMirror.on('change', function () {
                return _this.trigger('change');
            });
        },


        /**
         * Return whether or not the editor's contents have changed.
         *
         * Args:
         *     initialValue (string):
         *         The initial value of the editor.
         *
         * Returns:
         *     boolean:
         *     Whether or not the editor is dirty.
         */
        isDirty: function isDirty(initialValue) {
            /*
             * We cannot trust codeMirror's isClean() method.
             *
             * It is also possible for initialValue to be undefined, so we use an
             * empty string in that case instead.
             */
            return (initialValue || '') !== this.getText();
        },


        /**
         * Set the text in the editor.
         *
         * Args:
         *     text (string):
         *         The new text for the editor.
         */
        setText: function setText(text) {
            this._codeMirror.setValue(text);
        },


        /**
         * Return the text in the editor.
         *
         * Returns:
         *     string:
         *     The current contents of the editor.
         */
        getText: function getText() {
            return this._codeMirror.getValue();
        },


        /**
         * Insert a new line of text into the editor.
         *
         * If the editor has focus, insert at the cursor position. Otherwise,
         * insert at the end.
         *
         * Args:
         *     text (string):
         *         The text to insert.
         */
        insertLine: function insertLine(text) {
            var position = void 0;

            if (this._codeMirror.hasFocus()) {
                var cursor = this._codeMirror.getCursor();
                var line = this._codeMirror.getLine(cursor.line);
                position = CodeMirror.Pos(cursor.line, line.length - 1);

                if (line.length !== 0) {
                    /*
                     * If the current line has some content, insert the new text on
                     * the line after it.
                     */
                    text = '\n' + text;
                }

                if (!text.endsWith('\n')) {
                    text += '\n';
                }
            } else {
                position = CodeMirror.Pos(this._codeMirror.lastLine());
                text = '\n' + text;
            }

            this._codeMirror.replaceRange(text, position);
        },


        /**
         * Return the full client height of the content.
         *
         * Returns:
         *     number:
         *     The client height of the editor.
         */
        getClientHeight: function getClientHeight() {
            return this._codeMirror.getScrollInfo().clientHeight;
        },


        /**
         * Set the size of the editor.
         *
         * Args:
         *     width (number):
         *         The new width of the editor.
         *
         *     height (number):
         *         The new height of the editor.
         */
        setSize: function setSize(width, height) {
            this._codeMirror.setSize(width, height);
            this._codeMirror.refresh();
        },


        /**
         * Focus the editor.
         */
        focus: function focus() {
            this._codeMirror.focus();
        }
    });

    /**
     * Wraps <textarea>, providing a standard interface for TextEditorView's usage.
     */
    var TextAreaWrapper = Backbone.View.extend({
        tagName: 'textarea',

        /*
         * Initialize TextAreaWrapper.
         *
         * This will set up the element based on the provided options, begin
         * listening for events, and add the element to the parent.
         *
         * Args:
         *     options (object):
         *         Options for the wrapper.
         *
         * Option Args:
         *     autoSize (boolean):
         *         Whether the editor should automatically resize itself to fit its
         *         container.
         *
         *     parentEl (Element):
         *        The parent element for the editor.
         *
         *    minHeight (number):
         *        The minimum vertical size of the editor.
         */
        initialize: function initialize(options) {
            var _this2 = this;

            this.options = options;

            if (options.autoSize) {
                this.$el.autoSizeTextArea();
            }

            this.$el.css('width', '100%').appendTo(options.parentEl).on('change keydown keyup keypress', function () {
                return _this2.trigger('change');
            });

            if (options.minHeight !== undefined) {
                if (options.autoSize) {
                    this.$el.autoSizeTextArea('setMinHeight', options.minHeight);
                } else {
                    this.$el.css('min-height', this.options.minHeight);
                }
            }
        },


        /**
         * Return whether or not the editor's contents have changed.
         *
         * Args:
         *     initialValue (string):
         *         The initial value of the editor.
         *
         * Returns:
         *     boolean:
         *     Whether or not the editor is dirty.
         */
        isDirty: function isDirty(initialValue) {
            var value = this.el.value || '';

            return value.length !== initialValue.length || value !== initialValue;
        },


        /**
         * Set the text in the editor.
         *
         * Args:
         *     text (string):
         *         The new text for the editor.
         */
        setText: function setText(text) {
            this.el.value = text;

            if (this.options.autoSize) {
                this.$el.autoSizeTextArea('autoSize');
            }
        },


        /**
         * Return the text in the editor.
         *
         * Returns:
         *     string:
         *     The current contents of the editor.
         */
        getText: function getText() {
            return this.el.value;
        },


        /**
         * Insert a new line of text into the editor.
         *
         * Args:
         *     text (string):
         *         The text to insert.
         */
        insertLine: function insertLine(text) {
            if (this.$el.is(':focus')) {
                var value = this.el.value;
                var cursor = this.el.selectionEnd;
                var endOfLine = value.indexOf('\n', cursor);

                if (endOfLine === -1) {
                    // The cursor is on the last line.
                    this.el.value += '\n' + text;
                } else {
                    // The cursor is in the middle of the text.
                    this.el.value = value.slice(0, endOfLine + 1) + '\n' + text + '\n' + value.slice(endOfLine);
                }
            } else {
                this.el.value += '\n' + text;
            }
        },


        /**
         * Return the full client height of the content.
         *
         * Returns:
         *     number:
         *     The client height of the editor.
         */
        getClientHeight: function getClientHeight() {
            return this.el.clientHeight;
        },


        /**
         * Set the size of the editor.
         *
         * Args:
         *     width (number):
         *         The new width of the editor.
         *
         *     height (number):
         *         The new height of the editor.
         */
        setSize: function setSize(width, height) {
            if (width !== null) {
                this.$el.innerWidth(width);
            }

            if (height !== null) {
                if (height === 'auto' && this.options.autoSize) {
                    this.$el.autoSizeTextArea('autoSize', true);
                } else {
                    this.$el.innerHeight(height);
                }
            }
        },


        /**
         * Focus the editor.
         */
        focus: function focus() {
            this.$el.focus();
        }
    });

    /**
     * Provides an editor for editing plain or Markdown text.
     *
     * The editor allows for switching between plain or Markdown text on-the-fly.
     *
     * When editing plain text, this uses a standard textarea widget.
     *
     * When editing Markdown, this makes use of CodeMirror. All Markdown content
     * will be formatted as the user types, making it easier to notice when a
     * stray _ or ` will cause Markdown-specific behavior.
     */
    RB.TextEditorView = Backbone.View.extend({
        className: 'text-editor',

        defaultOptions: {
            autoSize: true,
            minHeight: 70
        },

        events: {
            'focus': 'focus',
            'remove': '_onRemove'
        },

        /**
         * Initialize the view with any provided options.
         *
         * Args:
         *     options (object):
         *         Options for view construction.
         *
         * Option Args:
         *     richText (boolean):
         *         Whether the editor is using rich text (Markdown).
         *
         *     text (string):
         *         The initial text.
         *
         *     bindRichText (object):
         *         An object with ``model`` and ``attrName`` keys, for when the
         *         rich text should be bound to an attribute on another model.
         */
        initialize: function initialize() {
            var options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};

            this._files = [];
            this._editor = null;
            this._prevClientHeight = null;

            this.options = _.defaults(options, this.defaultOptions);
            this.richText = !!this.options.richText;
            this._dropTarget = null;
            this._value = this.options.text || '';
            this._richTextDirty = false;

            if (this.options.bindRichText) {
                this.bindRichTextAttr(this.options.bindRichText.model, this.options.bindRichText.attrName);
            }

            /*
             * If the user is defaulting to rich text, we're going to want to
             * show the rich text UI by default, even if any bound rich text
             * flag is set to False.
             *
             * This requires cooperation with the template or API results
             * that end up backing this TextEditor. The expectation is that
             * those will be providing escaped data for any plain text, if
             * the user's set to use rich text by default. If this expectation
             * holds, the user will have a consistent experience for any new
             * text fields.
             */
            if (RB.UserSession.instance.get('defaultUseRichText')) {
                this.setRichText(true);
            }
        },


        /**
         * Render the text editor.
         *
         * This will set the class name on the element, ensuring we have a
         * standard set of styles, even if this editor is bound to an existing
         * element.
         *
         * Returns:
         *     RB.TextEditorView:
         *     This object, for chaining.
         */
        render: function render() {
            this.$el.addClass(this.className);

            return this;
        },


        /**
         * Set whether or not rich text (Markdown) is to be used.
         *
         * This can dynamically change the text editor to work in plain text
         * or Markdown.
         *
         * Args:
         *     richText (boolean):
         *         Whether the editor should use rich text.
         */
        setRichText: function setRichText(richText) {
            if (richText === this.richText) {
                return;
            }

            if (this._editor) {
                this._hideEditor();
                this.richText = richText;
                this._showEditor();

                this._richTextDirty = true;

                this.$el.triggerHandler('resize');
            } else {
                this.richText = richText;
            }

            this.trigger('change:richText', richText);
            this.trigger('change');
        },


        /**
         * Bind a richText attribute on a model to the mode on this editor.
         *
         * This editor's richText setting will stay in sync with the attribute
         * on the given mode.
         *
         * Args:
         *     model (Backbone.Model):
         *         A model to bind to.
         *
         *     attrName (string):
         *         The name of the attribute to bind.
         */
        bindRichTextAttr: function bindRichTextAttr(model, attrName) {
            var _this3 = this;

            this.setRichText(model.get(attrName));

            this.listenTo(model, 'change:' + attrName, function (model, value) {
                return _this3.setRichText(value);
            });
        },


        /**
         * Bind an Enable Markdown checkbox to this text editor.
         *
         * The checkbox will initially be set to the value of the editor's
         * richText property. Toggling the checkbox will then manipulate that
         * property.
         *
         * Args:
         *     $checkbox (jQuery):
         *         The checkbox to bind.
         */
        bindRichTextCheckbox: function bindRichTextCheckbox($checkbox) {
            var _this4 = this;

            $checkbox.prop('checked', this.richText).on('change', function () {
                return _this4.setRichText($checkbox.prop('checked'));
            });

            this.on('change:richText', function () {
                return $checkbox.prop('checked', _this4.richText);
            });
        },


        /**
         * Bind the visibility of an element to the richText property.
         *
         * If richText ist true, the element will be shown. Otherwise, it
         * will be hidden.
         *
         * Args:
         *     $el (jQuery):
         *         The element to show when richText is true.
         */
        bindRichTextVisibility: function bindRichTextVisibility($el) {
            var _this5 = this;

            $el.setVisible(this.richText);

            this.on('change:richText', function () {
                return $el.setVisible(_this5.richText);
            });
        },


        /**
         * Return whether or not the editor's contents have changed.
         *
         * Args:
         *     initialValue (string):
         *         The initial value of the editor.
         *
         * Returns:
         *     boolean:
         *     Whether or not the editor is dirty.
         */
        isDirty: function isDirty(initialValue) {
            return this._editor !== null && (this._richTextDirty || this._editor.isDirty(initialValue || ''));
        },


        /**
         * Set the text in the editor.
         *
         * Args:
         *     text (string):
         *         The new text for the editor.
         */
        setText: function setText(text) {
            if (text !== this.getText()) {
                if (this._editor) {
                    this._editor.setText(text);
                } else {
                    this._value = text;
                }
            }
        },


        /**
         * Return the text in the editor.
         *
         * Returns:
         *     string:
         *     The current contents of the editor.
         */
        getText: function getText() {
            return this._editor ? this._editor.getText() : this._value;
        },


        /**
         * Insert a new line of text into the editor.
         *
         * Args:
         *     text (string):
         *         The text to insert.
         */
        insertLine: function insertLine(text) {
            if (this._editor) {
                this._editor.insertLine(text);
            } else {
                if (this._value.endsWith('\n')) {
                    this._value += text + '\n';
                } else {
                    this._value += '\n' + text;
                }
            }
        },


        /**
         * Set the size of the editor.
         *
         * Args:
         *     width (number):
         *         The new width of the editor.
         *
         *     height (number):
         *         The new height of the editor.
         */
        setSize: function setSize(width, height) {
            if (this._editor) {
                this._editor.setSize(width, height);
            }
        },


        /**
         * Show the editor.
         */
        show: function show() {
            this.$el.show();
            this._showEditor();
        },


        /**
         * Hide the editor.
         */
        hide: function hide() {
            this._hideEditor();
            this.$el.hide();
        },


        /**
         * Focus the editor.
         */
        focus: function focus() {
            if (this._editor) {
                this._editor.focus();
            }
        },


        /**
         * Handler for the remove event.
         *
         * Disables the drag-and-drop overlay.
         */
        _onRemove: function _onRemove() {
            RB.DnDUploader.instance.unregisterDropTarget(this.$el);
        },


        /**
         * Show the actual editor wrapper.
         *
         * Any stored text will be transferred to the editor, and the editor
         * will take control over all operations.
         */
        _showEditor: function _showEditor() {
            var _this6 = this;

            var EditorCls = this.richText ? CodeMirrorWrapper : TextAreaWrapper;

            if (this.richText) {
                RB.DnDUploader.instance.registerDropTarget(this.$el, gettext('Drop to add an image'), this._uploadImage.bind(this));
            }

            this._editor = new EditorCls({
                parentEl: this.el,
                autoSize: this.options.autoSize,
                minHeight: this.options.minHeight
            });

            this._editor.setText(this._value);
            this._value = '';
            this._richTextDirty = false;
            this._prevClientHeight = null;

            this._editor.$el.on('resize', _.throttle(function () {
                return _this6.$el.triggerHandler('resize');
            }, 250));

            this.listenTo(this._editor, 'change', _.throttle(function () {
                /*
                 * Make sure that the editor wasn't closed before the throttled
                 * handler was reached.
                 */
                if (_this6._editor === null) {
                    return;
                }

                var clientHeight = _this6._editor.getClientHeight();

                if (clientHeight !== _this6._prevClientHeight) {
                    _this6._prevClientHeight = clientHeight;
                    _this6.$el.triggerHandler('resize');
                }

                _this6.trigger('change');
            }, 500));

            this.focus();
        },


        /**
         * Hide the actual editor wrapper.
         *
         * The last value from the editor will be stored for later retrieval.
         */
        _hideEditor: function _hideEditor() {
            RB.DnDUploader.instance.unregisterDropTarget(this.$el);

            if (this._editor) {
                this._value = this._editor.getText();
                this._richTextDirty = false;
                this._editor.remove();
                this._editor = null;

                this.$el.empty();
            }
        },


        /**
         * Return whether or not a given file is an image.
         *
         * Args:
         *     file (File):
         *         The file to check.
         *
         * Returns:
         *     boolean:
         *     True if the given file appears to be an image.
         */
        _isImage: function _isImage(file) {
            if (file.type) {
                return file.type.split('/')[0] === 'image';
            }

            var filename = file.name.toLowerCase();
            return ['.jpeg', '.jpg', '.png', '.gif', '.bmp', '.tiff', '.svg'].some(function (extension) {
                return filename.endsWith(extension);
            });
        },


        /**
         * Upload the image and append an image link to the editor's contents.
         *
         * Creates an instance of UserFileAttachment and saves it without the file,
         * then updates the model with the file. This allows the file to be
         * uploaded asynchronously after we get the link that is generated when the
         * UserFileAttachment is created.
         *
         * Args:
         *     file (File):
         *         The image file to upload.
         */
        _uploadImage: function _uploadImage(file) {
            var _this7 = this;

            if (!this._isImage(file)) {
                return;
            }

            var userFileAttachment = new RB.UserFileAttachment({
                caption: file.name
            });

            userFileAttachment.save({
                success: function success() {
                    _this7.insertLine('![Image](' + userFileAttachment.get('downloadURL') + ')');

                    userFileAttachment.set('file', file);
                    userFileAttachment.save({
                        error: function error(model, response) {
                            return alert(response.errorText);
                        }
                    });
                },
                error: function error(model, response) {
                    return alert(response.errorText);
                }
            });
        }
    }, {
        /**
         * Return options used to display a TextEditorView in an inlineEditor.
         *
         * Args:
         *     options (object):
         *         Options to be passed on to the TextEditorView.
         *
         * Returns:
         *     object:
         *     An options object to be used with an inlineEditor. The resulting
         *     inlineEditor will make use of the TextEditorView instead of its
         *     default textarea.
         */
        getInlineEditorOptions: function getInlineEditorOptions(options) {
            var textEditor = void 0;

            return {
                matchHeight: false,
                multiline: true,

                createMultilineField: function createMultilineField(editor) {
                    var $editor = editor.element;
                    var origRichText = void 0;

                    textEditor = new RB.TextEditorView(options);
                    textEditor.render();

                    $editor.one('beginEdit', function () {
                        var $buttons = $editor.inlineEditor('buttons');
                        var $span = $('<span class="enable-markdown" />');

                        var $checkbox = $('<input/>').attr({
                            id: _.uniqueId('markdown_check'),
                            type: 'checkbox'
                        }).appendTo($span);
                        textEditor.bindRichTextCheckbox($checkbox);

                        $span.append($('<label/>').attr('for', $checkbox[0].id).text(gettext('Enable Markdown')));

                        $buttons.append($span);

                        var $markdownRef = $('<a/>').addClass('markdown-info').attr({
                            href: MANUAL_URL + 'users/markdown/',
                            target: '_blank'
                        }).text(gettext('Markdown Reference')).setVisible(textEditor.richText).appendTo($buttons);
                        textEditor.bindRichTextVisibility($markdownRef);
                    });

                    $editor.on('beginEdit', function () {
                        textEditor._showEditor();
                        origRichText = textEditor.richText;
                    });

                    $editor.on('cancel', function () {
                        textEditor._hideEditor();
                        textEditor.setRichText(origRichText);
                    });

                    $editor.on('complete', function () {
                        textEditor._hideEditor();
                    });

                    textEditor.$el.data('text-editor', textEditor);

                    return textEditor.$el;
                },
                setFieldValue: function setFieldValue(editor, value) {
                    textEditor.setText(value || '');
                },
                getFieldValue: function getFieldValue() {
                    return textEditor.getText();
                },
                isFieldDirty: function isFieldDirty(editor, initialValue) {
                    return textEditor.isDirty(initialValue);
                }
            };
        },


        /**
         * Return the TextEditorView for an inlineEditor element.
         *
         * Returns:
         *     TextEditorView:
         *     The view corresponding to the editor.
         */
        getFromInlineEditor: function getFromInlineEditor($editor) {
            return $editor.inlineEditor('field').data('text-editor');
        }
    });
})();

//# sourceMappingURL=textEditorView.js.map