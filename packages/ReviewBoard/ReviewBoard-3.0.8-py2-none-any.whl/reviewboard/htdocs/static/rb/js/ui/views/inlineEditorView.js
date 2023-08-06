'use strict';

/**
 * A view for inline editors.
 *
 * This provides the framework for items which are "editable". These provide a
 * way to switch between a normal view and an edit view, which is usually a
 * text box (either single- or multiple-line).
 */
RB.InlineEditorView = Backbone.View.extend({
    /**
     * Defaults for the view options.
     */
    defaultOptions: {
        animationSpeedMS: 200,
        deferEventSetup: false,
        editIconPath: null,
        editIconClass: null,
        enabled: true,
        extraHeight: 100,
        focusOnOpen: true,
        formatResult: function formatResult(value) {
            return value.htmlEncode();
        },
        formClass: '',
        getFieldValue: function getFieldValue(editor) {
            return editor.$field.val();
        },
        hasRawValue: false,
        isFieldDirty: function isFieldDirty(editor, initialValue) {
            var value = editor.getValue() || '';
            var normValue = (editor.options.hasRawValue ? value : value.htmlEncode()) || '';
            initialValue = editor.normalizeText(initialValue);

            return normValue.length !== initialValue.length || normValue !== initialValue;
        },
        matchHeight: true,
        multiline: false,
        notifyUnchangedCompletion: false,
        promptOnCancel: true,
        rawValue: null,
        setFieldValue: function setFieldValue(editor, value) {
            return editor.$field.val(value);
        },
        showButtons: true,
        showEditIcon: true,
        showRequiredFlag: false,
        startOpen: false
    },

    /**
     * Initialize the view.
     *
     * Args:
     *     options (object):
     *         Options for the view.
     *
     * Option Args:
     *     animationSpeedMS (number, optional):
     *         The duration of animated transitions, in milliseconds.
     *
     *     deferEventSetup (boolean, optional):
     *         Whether to defer event setup after rendering. This should be
     *         used when a consumer wants to prioritize event handling (such as
     *         handling the "enter" key for autocomplete).
     *
     *     editIconClass (string, optional):
     *         The class name to use for the edit icon, when the icon is
     *         created via CSS rules. This is only used if ``editIconPath`` is
     *         unspecified.
     *
     *     editIconPath (string, optional):
     *         The path for an image for the edit icon.
     *
     *     enabled (boolean):
     *         Whether editing is enabled.
     *
     *     extraHeight (number, optional):
     *         Extra height to add when displaying the editor, in pixels.
     *
     *     focusOnOpen (boolean, optional):
     *         Whether to focus the field when opening the editor.
     *
     *     formatResult (function, optional):
     *         A function to format the resulting value after editing back
     *         into the element.
     *
     *     formClass (string, optional):
     *         The class to add to the form's DOM element.
     *
     *     getFieldValue (function, optional):
     *         A function to retrieve the field value.
     *
     *     hasRawValue (boolean, optional):
     *         Whether the field has a "raw value", which is data for the field
     *         separate from the actual contents of the element.
     *
     *     isFieldDirty (function, optional):
     *         A function to calculate whether the editor value is dirty.
     *
     *     matchHeight (boolean, optional):
     *         Whether to attempt to match the height of the editor and the
     *         element it's replacing.
     *
     *     multiline (boolean, optional):
     *         Whether the text input should be multi-line or single-line.
     *
     *     notifyUnchangedCompletion (boolean, optional):
     *         Whether the editor should trigger a ``complete`` event even if
     *         the value was unchanged. If this is ``false``, the editor will
     *         trigger a ``cancel`` event instead.
     *
     *     promptOnCancel (boolean, optional):
     *         Whether to prompt the user before cancelling if the editor is
     *         dirty.
     *
     *     rawValue (*, optional):
     *         When ``hasRawValue`` is ``true``, this provides the data for the
     *         raw value of the item being edited.
     *
     *     setFieldValue (function, optional):
     *         A function to set the field value.
     *
     *     showButtons (boolean, optional):
     *         Whether to show OK/Cancel buttons.
     *
     *     showEditIcon (boolean, optional):
     *         Whether to show the edit icon.
     *
     *     showRequiredFlag (boolean, optional):
     *         Whether to show the required flag on the edit icon.
     *
     *     startOpen (boolean, optional):
     *         Whether the editor should be open when first created.
     *
     *     stripTags (boolean, optional):
     *         Whether to strip out HTML tags when normalizing input.
     *
     *     useEditIconOnly (boolean, optional):
     *         Whether the editor can be opened only by clicking on the edit
     *         icon. If false, clicking on the field value will also trigger an
     *         edit.
     */
    initialize: function initialize(options) {
        this.options = _.defaults(options, this.defaultOptions);
        this._initialValue = null;
        this._editing = false;
        this._dirty = false;
        this._dirtyCalcTimeout = null;
    },


    /**
     * Render the view.
     *
     * Returns:
     *     RB.InlineEditorView:
     *     This object, for chaining.
     */
    render: function render() {
        var _this = this;

        this._$form = $('<form>').addClass('inline-editor-form ' + this.options.formClass).css('display', 'inline').hide().insertBefore(this.$el);

        this.$field = this.createField().prependTo(this._$form);
        this._isTextArea = this.$field[0].tagName === 'TEXTAREA';

        this.$buttons = $();

        if (this.options.showButtons) {
            this.$buttons = $(this.options.multiline ? '<div>' : '<span>').hide().addClass('buttons').appendTo(this._$form);

            $('<input type="button" class="save">').val(gettext('OK')).appendTo(this.$buttons).click(this.submit.bind(this));

            $('<input type="button" class="cancel">').val(gettext('Cancel')).appendTo(this.$buttons).click(this.cancel.bind(this));
        }

        this._$editIcon = $();

        if (this.options.showEditIcon) {
            var editText = gettext('Edit this field');
            this._$editIcon = $('<a class="editicon" href="#" role="button">').attr({
                'title': editText,
                'aria-label': editText
            }).click(function (e) {
                e.preventDefault();
                e.stopPropagation();

                _this.startEdit();
            });

            if (this.options.editIconPath) {
                this._$editIcon.append('<img src="' + this.options.editIconPath + '">');
            } else if (this.options.editIconClass) {
                this._$editIcon.append('<div class="' + this.options.editIconClass + '" aria-hidden="true"></div>');
            }

            if (this.options.showRequiredFlag) {
                var requiredText = gettext('This field is required');
                $('<span class="required-flag">*</span>').attr({
                    'aria-label': requiredText,
                    'title': requiredText
                }).appendTo(this._$editIcon);
            }

            if (this.options.multiline && this.$el[0].id) {
                $('label[for="' + this.$el[0].id + '"]').append(this._$editIcon);
            } else {
                this._$editIcon.insertAfter(this.$el);
            }
        }

        if (!this.options.deferEventSetup) {
            this.setupEvents();
        }

        if (this.options.startOpen) {
            this.startEdit({
                preventAnimation: true
            });
        }

        if (this.options.enabled) {
            this.enable();
        } else {
            this.disable();
        }

        return this;
    },


    /**
     * Create and return the field to use for the input element.
     *
     * Returns:
     *     jQuery:
     *     The newly created input element.
     */
    createField: function createField() {
        if (this.options.multiline) {
            return $('<textarea>').autoSizeTextArea();
        } else {
            return $('<input type="text">');
        }
    },


    /**
     * Connect events.
     */
    setupEvents: function setupEvents() {
        var _this2 = this;

        this.$field.keydown(function (e) {
            e.stopPropagation();

            switch (e.keyCode || e.charCode || e.which) {
                case 13:
                    // Enter
                    if (!_this2.options.multiline || e.ctrlKey) {
                        _this2.submit();
                    }

                    if (!_this2.options.multiline) {
                        e.preventDefault();
                    }

                    break;

                case 27:
                    // Escape
                    _this2.cancel();
                    break;

                case 83: // S
                case 115:
                    // s
                    if (e.ctrlKey) {
                        _this2.submit();
                        e.preventDefault();
                    }
                    break;

                default:
                    break;
            }
        }).keypress(function (e) {
            return e.stopPropagation();
        }).keyup(function (e) {
            e.stopPropagation();
            e.preventDefault();

            _this2._scheduleUpdateDirtyState();
        });

        if (!this.options.useEditIconOnly) {
            /*
             * Check if the mouse was dragging, so that the editor isn't opened
             * when text is selected.
             */
            var isDragging = true;

            this.$el.on('click', 'a', function (e) {
                return e.stopPropagation();
            }).click(function (e) {
                e.stopPropagation();
                e.preventDefault();

                if (!isDragging) {
                    _this2.startEdit();
                }

                isDragging = true;
            }).mousedown(function () {
                isDragging = false;
                _this2.$el.one('mousemove', function () {
                    isDragging = true;
                });
            }).mouseup(function () {
                _this2.$el.unbind('mousemove');
            });
        }

        $(window).resize(this._fitWidthToParent.bind(this));
    },


    /**
     * Start editing.
     *
     * Args:
     *     options (object, optional):
     *         Options for the operation.
     *
     * Option Args:
     *     preventAnimation (boolean, optional):
     *         Whether to prevent the default animation.
     */
    startEdit: function startEdit() {
        var options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};

        if (this._editing || !this.options.enabled) {
            return;
        }

        var value = void 0;

        if (this.options.hasRawValue) {
            this._initialValue = this.options.rawValue;
            value = this._initialValue;
        } else {
            this._initialValue = this.$el.text();
            value = this.normalizeText(this._initialValue).htmlDecode();
        }

        this._editing = true;
        this.options.setFieldValue(this, value);

        this.trigger('beginEditPreShow');
        this.showEditor(options);
        this.trigger('beginEdit');
    },


    /**
     * Show the editor.
     *
     * Args:
     *     options (object, optional):
     *         Options for the operation.
     *
     * Options Args:
     *     preventAnimation (boolean, optional):
     *         Whether to prevent the default animation.
     */
    showEditor: function showEditor() {
        var _this3 = this;

        var options = arguments.length > 0 && arguments[0] !== undefined ? arguments[0] : {};

        if (this.options.multiline && !options.preventAnimation) {
            this._$editIcon.fadeOut(this.options.animationSpeedMS);
        } else {
            this._$editIcon.hide();
        }

        this.$el.hide();
        this._$form.show();

        if (this.options.multiline) {
            var elHeight = this.$el.outerHeight();
            var newHeight = elHeight + this.options.extraHeight;

            this._fitWidthToParent();

            if (this._isTextArea) {
                if (this.options.matchHeight) {
                    // TODO: Set autosize min height
                    this.$field.autoSizeTextArea('setMinHeight', newHeight).css('overflow', 'hidden');

                    if (options.preventAnimation) {
                        this.$field.height(newHeight);
                    } else {
                        this.$field.height(elHeight).animate({ height: newHeight }, this.options.animationSpeedMS);
                    }
                } else {
                    /*
                     * If there's significant processing that happens between
                     * the text and what's displayed in the element, it's
                     * likely that the rendered size will be different from the
                     * editor size. In that case, don't try to match sizes,
                     * just ask the field to auto-size itself to the size of
                     * the source text.
                     */
                    this.$field.autoSizeTextArea('autoSize', true, false, elHeight);
                }
            }
        }

        this.$buttons.show();

        // Execute this after the animation, if we performed one.
        this.$field.queue(function () {
            if (_this3.options.multiline && _this3._isTextArea) {
                _this3.$field.css('overflow', 'auto');
            }

            _this3._fitWidthToParent();

            if (_this3.options.focusOnOpen) {
                _this3.$field.focus();
            }

            if (!_this3.options.multiline && _this3.$field[0].tagName === 'INPUT') {
                _this3.$field[0].select();
            }

            _this3.$field.dequeue();
        });
    },


    /**
     * Hide the inline editor.
     */
    hideEditor: function hideEditor() {
        var _this4 = this;

        this.$field.blur();
        this.$buttons.hide();

        if (this.options.multiline) {
            this._$editIcon.fadeIn(this.options.animationSpeedMS);
        } else {
            this._$editIcon.show();
        }

        if (this.options.multiline && this.options.matchHeight && this._editing && this._isTextArea) {
            this.$field.css('overflow', 'hidden').animate({ height: this.$el.outerHeight() }, this.options.animationSpeedMS);
        }

        this.$field.queue(function () {
            _this4.$el.show();
            _this4._$form.hide();
            _this4.$field.dequeue();
        });

        this._editing = false;
        this._updateDirtyState();
    },


    /**
     * Save the value of the editor.
     */
    save: function save() {
        var value = this.getValue();
        var initialValue = this._initialValue;
        var dirty = this.isDirty();

        if (dirty) {
            this.$el.html(this.options.formatResult(value));
            this._initialValue = this.$el.text();
        }

        if (dirty || this.options.notifyUnchangedCompletion) {
            this.trigger('complete', value, initialValue);

            if (this.options.hasRawValue) {
                this.options.rawValue = value;
            }
        } else {
            this.trigger('cancel', this._initialValue);
        }
    },


    /**
     * Submit the editor.
     */
    submit: function submit() {
        // hideEditor() resets the _dirty flag, so we need to save() first.
        this.save();
        this.hideEditor();
    },


    /**
     * Cancel the edit.
     */
    cancel: function cancel() {
        if (!this.isDirty() || !this.options.promptOnCancel || confirm(gettext('You have unsaved changes. Are you sure you want to discard them?'))) {
            this.hideEditor();
            this.trigger('cancel', this._initialValue);
        }
    },


    /**
     * Return the dirty state of the editor.
     *
     * Returns:
     *     boolean:
     *     Whether the editor is currently dirty.
     */
    isDirty: function isDirty() {
        if (this._dirtyCalcTimeout !== null) {
            clearTimeout(this._dirtyCalcTimeout);
            this._updateDirtyState();
        }

        return this._dirty;
    },


    /**
     * Return the value in the field.
     *
     * Returns:
     *     *:
     *     The current value of the field.
     */
    getValue: function getValue() {
        return this.options.getFieldValue(this);
    },


    /**
     * Set the value in the field.
     *
     * Args:
     *     value (*):
     *     The new value for the field.
     */
    setValue: function setValue(value) {
        this.options.setFieldValue(this, value);
        this._updateDirtyState();
    },


    /**
     * Enable the editor.
     */
    enable: function enable() {
        if (this._editing) {
            this.showEditor();
        }

        this._$editIcon.show();
        this.options.enabled = true;
    },


    /**
     * Disable the editor.
     */
    disable: function disable() {
        if (this._editing) {
            this.hideEditor();
        }

        this._$editIcon.hide();
        this.options.enabled = false;
    },


    /**
     * Return whether the editor is currently in edit mode.
     *
     * Returns:
     *     boolean:
     *     true if the inline editor is open.
     */
    editing: function editing() {
        return this._editing;
    },


    /**
     * Normalize the given text.
     *
     * Args:
     *     text (string):
     *         The text to normalize.
     *
     * Returns:
     *     string:
     *     The text with ``<br>`` elements turned into newlines and (in the
     *     case of multi-line data), whitespace collapsed.
     */
    normalizeText: function normalizeText(text) {
        if (this.options.stripTags) {
            /*
             * Turn <br> elements back into newlines before stripping out all
             * other tags. Without this, we lose multi-line data when editing
             * some legacy data.
             */
            text = text.replace(/<br>/g, '\n');
            text = text.stripTags().strip();
        }

        if (!this.options.multiline) {
            text = text.replace(/\s{2,}/g, ' ');
        }

        return text;
    },


    /**
     * Schedule an update for the dirty state.
     */
    _scheduleUpdateDirtyState: function _scheduleUpdateDirtyState() {
        if (this._dirtyCalcTimeout === null) {
            this._dirtyCalcTimeout = setTimeout(this._updateDirtyState.bind(this), 200);
        }
    },


    /**
     * Update the dirty state of the editor.
     */
    _updateDirtyState: function _updateDirtyState() {
        var newDirtyState = this._editing && this.options.isFieldDirty(this, this._initialValue);

        if (this._dirty !== newDirtyState) {
            this._dirty = newDirtyState;
            this.trigger('dirtyStateChanged', this._dirty);
        }

        this._dirtyCalcTimeout = null;
    },


    /**
     * Fit the editor width to the parent element.
     */
    _fitWidthToParent: function _fitWidthToParent() {
        if (!this._editing) {
            return;
        }

        if (this.options.multiline) {
            this.$field.css({
                '-webkit-box-sizing': 'border-box',
                '-moz-box-sizing': 'border-box',
                'box-sizing': 'border-box',
                'width': '100%'
            });
            return;
        }

        var $formParent = this._$form.parent();
        var parentTextAlign = $formParent.css('text-align');
        var isLeftAligned = parentTextAlign === 'left';

        if (!isLeftAligned) {
            $formParent.css('text-align', 'left');
        }

        var boxSizing = this.$field.css('box-sizing');
        var extentTypes = void 0;

        if (boxSizing === 'border-box') {
            extentTypes = 'm';
        } else if (boxSizing === 'padding-box') {
            extentTypes = 'p';
        } else {
            extentTypes = 'bmp';
        }

        var buttonsWidth = 0;

        if (this.$buttons.length !== 0) {
            var buttonsDisplay = this.$buttons.css('display');

            if (buttonsDisplay === 'inline' || buttonsDisplay === 'inline-block') {
                /*
                 * The buttons are set for the same line as the field, so
                 * factor the width of the buttons container into the field
                 * width calculation below.
                 */
                buttonsWidth = this.$buttons.outerWidth();
            }
        }

        /*
         * First make the field really small so it will fit without wrapping,
         * then figure out the offset and use it to calculate the desired
         * width.
         */
        this.$field.width(0).outerWidth($formParent.innerWidth() - (this._$form.offset().left - $formParent.offset().left) - this.$field.getExtents(extentTypes, 'lr') - buttonsWidth);

        if (!isLeftAligned) {
            $formParent.css('text-align', parentTextAlign);
        }
    }
});

/**
 * A view for inline editors which use the CodeMirror editor for Markdown.
 */
RB.RichTextInlineEditorView = RB.InlineEditorView.extend({
    /**
     * Defaults for the view options.
     */
    defaultOptions: _.defaults({
        matchHeight: false,
        multiline: true,
        setFieldValue: function setFieldValue(editor, value) {
            return editor.textEditor.setText(value || '');
        },
        getFieldValue: function getFieldValue(editor) {
            return editor.textEditor.getText();
        },
        isFieldDirty: function isFieldDirty(editor, initialValue) {
            initialValue = editor.normalizeText(initialValue);

            return editor.textEditor.isDirty(initialValue);
        }
    }, RB.InlineEditorView.prototype.defaultOptions),

    /**
     * Create and return the field to use for the input element.
     *
     * Returns:
     *     jQuery:
     *     The newly created input element.
     */
    createField: function createField() {
        var _this5 = this;

        var origRichText = void 0;

        this.textEditor = new RB.TextEditorView(this.options.textEditorOptions);
        this.textEditor.$el.on('resize', function () {
            return _this5.trigger('resize');
        });

        this.$el.data('text-editor', this.textEditor);

        this.once('beginEdit', function () {
            var $span = $('<span class="enable-markdown">');
            var $checkbox = $('<input type="checkbox">').attr('id', _.uniqueId('markdown_check')).appendTo($span);

            _this5.textEditor.bindRichTextCheckbox($checkbox);

            $('<label>').attr('for', $checkbox[0].id).text(gettext('Enable Markdown')).appendTo($span);

            _this5.$buttons.append($span);

            var $markdownRef = $('<a class="markdown-info" target="_blank">').attr('href', MANUAL_URL + 'users/markdown/').text(gettext('Markdown Reference')).setVisible(_this5.textEditor.richText).appendTo(_this5.$buttons);

            _this5.textEditor.bindRichTextVisibility($markdownRef);
        });

        this.listenTo(this, 'beginEdit', function () {
            _this5.textEditor._showEditor();
            origRichText = _this5.textEditor.richText;
        });

        this.listenTo(this, 'cancel', function () {
            _this5.textEditor._hideEditor();
            _this5.textEditor.setRichText(origRichText);
        });

        this.listenTo(this, 'complete', function () {
            return _this5.textEditor._hideEditor();
        });

        return this.textEditor.render().$el;
    }
});

//# sourceMappingURL=inlineEditorView.js.map