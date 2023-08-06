'use strict';

/**
 * A widget to select related objects using search and autocomplete.
 *
 * This is particularly useful for models where there can be a ton of rows in
 * the database. The built-in admin widgets provide a pretty poor
 * experience--either populating the list with the entire contents of the
 * table, which is super slow, or just listing PKs, which isn't usable.
 */
RB.RelatedObjectSelectorView = Backbone.View.extend({
    className: 'related-object-select',

    /**
     * The search placeholder text.
     *
     * Subclasses should override this.
     */
    searchPlaceholderText: '',

    /**
     * The element template.
     *
     * Subclasses may override this to change rendering.
     */
    template: _.template('<select placeholder="<%- searchPlaceholderText %>"\n        class="related-object-options"></select>\n<% if (multivalued) { %>\n<ul class="related-object-selected"></ul>\n<% } %>'),

    /**
     * Initialize the view.
     *
     * Args:
     *     options (object):
     *         Options for the view.
     *
     * Option Args:
     *     $input (jQuery):
     *         The ``<input>`` element which should be populated with the list
     *         of selected item PKs.
     *
     *     initialOptions (Array of object):
     *         The initially selected options.
     *
     *     multivalued (boolean):
     *         Whether or not the widget should allow selecting multiple
     *         values.
     *
     *     selectizeOptions (object):
     *          Additional options to pass in to $.selectize.
     */
    initialize: function initialize(options) {
        this.options = options;
        this._$input = options.$input;
        this._selectizeOptions = options.selectizeOptions;
        this._selectedIDs = new Map();

        _.bindAll(this, 'renderOption');
    },


    /**
     * Render the view.
     *
     * Returns:
     *     RB.RelatedObjectSelectorView:
     *     This object, for chaining.
     */
    render: function render() {
        var _this = this;

        var self = this;

        this.$el.html(this.template({
            searchPlaceholderText: this.searchPlaceholderText,
            multivalued: this.options.multivalued
        }));

        this._$selected = this.$('.related-object-selected');

        var renderItem = this.options.multivalued ? function () {
            return '';
        } : this.renderOption;

        var selectizeOptions = _.defaults(this._selectizeOptions, {
            copyClassesToDropdown: true,
            dropdownParent: 'body',
            preload: 'focus',
            render: {
                item: renderItem,
                option: this.renderOption
            },
            load: function load(query, callback) {
                self.loadOptions(query, function (data) {
                    return callback(data.filter(function (item) {
                        return !self._selectedIDs.has(item.id);
                    }));
                });
            },
            onChange: function onChange(selected) {
                if (selected) {
                    self._onItemSelected(this.options[selected], true);

                    if (self.options.multivalued) {
                        this.removeOption(selected);
                    }
                }

                if (self.options.multivalued) {
                    this.clear();
                }
            }
        });

        if (!this.options.multivalued && this.options.initialOptions.length) {
            var item = this.options.initialOptions[0];
            selectizeOptions.options = this.options.initialOptions;
            selectizeOptions.items = [item[selectizeOptions.valueField]];
        }

        this.$('select').selectize(selectizeOptions);

        if (this.options.multivalued) {
            this.options.initialOptions.forEach(function (item) {
                return _this._onItemSelected(item, false);
            });
        }

        this._$input.after(this.$el);
        return this;
    },


    /**
     * Update the "official" ``<input>`` element.
     *
     * This copies the list of selected item IDs into the form field which will
     * be submitted.
     */
    _updateInput: function _updateInput() {
        this._$input.val(Array.from(this._selectedIDs.keys()).join(','));
    },


    /**
     * Callback for when an item is selected.
     *
     * Args:
     *     item (object):
     *         The newly-selected item.
     *
     *     addToInput (boolean):
     *         Whether the ID of the item should be added to the ``<input>``
     *         field.
     *
     *         This will be ``false`` when populating the visible list from the
     *         value of the form field when the page is initially loaded, and
     *         ``true`` when adding items interactively.
     */
    _onItemSelected: function _onItemSelected(item, addToInput) {
        var _this2 = this;

        if (this.options.multivalued) {
            var $li = $('<li>').html(this.renderOption(item));
            var $items = this._$selected.children();
            var text = $li.text();

            $('<span class="remove-item fa fa-close">').click(function () {
                return _this2._onItemRemoved($li, item);
            }).appendTo($li);

            var attached = false;

            for (var i = 0; i < $items.length; i++) {
                var $item = $items.eq(i);

                if ($item.text().localeCompare(text) > 0) {
                    $item.before($li);
                    attached = true;
                    break;
                }
            }

            if (!attached) {
                $li.appendTo(this._$selected);
            }

            this._selectedIDs.set(item.id, item);

            if (addToInput) {
                this._updateInput();
            }
        } else {
            this._selectedIDs = new Map([[item.id, item]]);
            this._updateInput();
        }
    },


    /**
     * Callback for when an item is removed from the list.
     *
     * Args:
     *     $li (jQuery):
     *         The element representing the item in the selected list.
     *
     *     item (object):
     *         The item being removed.
     */
    _onItemRemoved: function _onItemRemoved($li, item) {
        $li.remove();
        this._selectedIDs.delete(item.id);
        this._updateInput();
    },


    /**
     * Render an option in the drop-down menu.
     *
     * This should be overridden in order to render type-specific data.
     *
     * Args:
     *     item (object):
     *         The item to render.
     *
     * Returns:
     *     string:
     *     HTML to insert into the drop-down menu.
     */
    renderOption: function renderOption() /* item */{
        return '';
    },


    /**
     * Load options from the server.
     *
     * This should be overridden in order to make whatever API requests are
     * necessary.
     *
     * Args:
     *     query (string):
     *         The string typed in by the user.
     *
     *     callback (function):
     *         A callback to be called once data has been loaded. This should
     *         be passed an array of objects, each representing an option in
     *         the drop-down.
     */
    loadOptions: function loadOptions(query, callback) {
        callback();
    }
});

//# sourceMappingURL=relatedObjectSelectorView.js.map