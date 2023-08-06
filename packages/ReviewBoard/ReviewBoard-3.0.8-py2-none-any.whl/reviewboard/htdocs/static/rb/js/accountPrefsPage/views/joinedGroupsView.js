'use strict';

var _slicedToArray = function () { function sliceIterator(arr, i) { var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"]) _i["return"](); } finally { if (_d) throw _e; } } return _arr; } return function (arr, i) { if (Array.isArray(arr)) { return arr; } else if (Symbol.iterator in Object(arr)) { return sliceIterator(arr, i); } else { throw new TypeError("Invalid attempt to destructure non-iterable instance"); } }; }();

(function () {

    /**
     * An item representing the user's membership with a group.
     *
     * This keeps track of the group's information and the membership state
     * for the user. It also allows changing that membership.
     *
     * This provides two actions: 'Join', and 'Leave'.
     */
    var GroupMembershipItem = Djblets.Config.ListItem.extend({
        defaults: _.defaults({
            localSiteName: null,
            displayName: null,
            groupName: null,
            joined: false,
            showRemove: false,
            url: null
        }, Djblets.Config.ListItem.prototype.defaults),

        /**
         * Initialize the item.
         *
         * The item's name and URL will be taken from the serialized group
         * information, and a proxy ReviewGroup will be created to handle
         * membership.
         */
        initialize: function initialize() {
            Djblets.Config.ListItem.prototype.initialize.apply(this, arguments);

            var name = this.get('name');
            var localSiteName = this.get('localSiteName');

            this.set({
                text: name,
                editURL: this.get('url')
            });

            this.group = new RB.ReviewGroup({
                id: this.get('reviewGroupID'),
                name: name,
                localSitePrefix: localSiteName ? 's/' + localSiteName + '/' : ''
            });

            this.on('change:joined', this._updateActions, this);
            this._updateActions();
        },


        /**
         * Join the group.
         *
         * This will add the user to the group, and set the 'joined' property
         * to true upon completion.
         */
        joinGroup: function joinGroup() {
            var _this = this;

            this.group.addUser(RB.UserSession.instance.get('username'), {
                success: function success() {
                    return _this.set('joined', true);
                }
            });
        },


        /**
         * Leave the group.
         *
         * This will remove the user from the group, and set the 'joined' property
         * to false upon completion.
         */
        leaveGroup: function leaveGroup() {
            var _this2 = this;

            this.group.removeUser(RB.UserSession.instance.get('username'), {
                success: function success() {
                    return _this2.set('joined', false);
                }
            });
        },


        /**
         * Update the list of actions.
         *
         * This will replace the existing action, if any, with a new action
         * allowing the user to join or leave the group, depending on their
         * current membership status.
         */
        _updateActions: function _updateActions() {
            if (this.get('joined')) {
                this.actions = [{
                    id: 'leave',
                    label: gettext('Leave')
                }];
            } else {
                this.actions = [{
                    id: 'join',
                    label: gettext('Join')
                }];
            }

            this.trigger('actionsChanged');
        }
    });

    /**
     * Provides UI for showing a group membership.
     *
     * This will display the group information and provide buttons for
     * the Join/Leave actions.
     */
    var GroupMembershipItemView = Djblets.Config.ListItemView.extend({
        actionHandlers: {
            'join': '_onJoinClicked',
            'leave': '_onLeaveClicked'
        },

        template: _.template(['<span class="config-group-name">', ' <a href="<%- editURL %>"><%- text %></a>', '</span>', '<span class="config-group-display-name"><%- displayName %></span>'].join('')),

        /**
         * Handler for when Join is clicked.
         *
         * Tells the model to join the group.
         */
        _onJoinClicked: function _onJoinClicked() {
            this.model.joinGroup();
        },


        /**
         * Handler for when Leave is clicked.
         *
         * Tells the model to leave the group.
         */
        _onLeaveClicked: function _onLeaveClicked() {
            this.model.leaveGroup();
        }
    });

    /**
     * Displays a list of group membership items, globally or for a Local Site.
     *
     * If displaying for a Local Site, then the name of the site will be shown
     * before the list.
     *
     * Each group in the list will be shown as an item with Join/Leave buttons.
     *
     * The list of groups are filterable. When filtering, if there are no groups
     * that match the filter, then the whole view will be hidden.
     */
    var SiteGroupsView = Backbone.View.extend({
        template: _.template(['<% if (name) { %>', ' <h3><%- name %></h3>', '<% } %>', '<div class="groups" />'].join('')),

        /**
         * Initialize the view.
         *
         * This will create a list for all groups in this view.
         *
         * Args:
         *     options (object):
         *         Options for view construction.
         *
         * Option Args:
         *     name (string):
         *         The name of the local site, if any.
         */
        initialize: function initialize(options) {
            this.name = options.name;
            this.collection = new RB.FilteredCollection(null, {
                collection: new Backbone.Collection(options.groups, {
                    model: GroupMembershipItem
                })
            });
            this.groupList = new Djblets.Config.List({}, {
                collection: this.collection
            });
        },


        /**
         * Render the view.
         *
         * Returns:
         *     SiteGroupsView:
         *     This object, for chaining.
         */
        render: function render() {
            this._listView = new Djblets.Config.ListView({
                ItemView: GroupMembershipItemView,
                model: this.groupList
            });

            this.$el.html(this.template({
                name: this.name
            }));

            this._listView.render();
            this._listView.$el.addClass('box-recessed').appendTo(this.$('.groups'));

            return this;
        },


        /**
         * Filter the list of groups by name.
         *
         * If no groups are found, then the view will hide itself.
         *
         * Args:
         *     name (string):
         *         The group name to search for.
         */
        filterBy: function filterBy(name) {
            this.collection.setFilters({
                'name': name
            });

            this.$el.setVisible(this.collection.length > 0);
        }
    });

    /**
     * Provides UI for managing a user's group memberships.
     *
     * All accessible groups will be shown to the user, sectioned by
     * Local Site. This list is filterable through a search box at the top of
     * the view.
     *
     * Each group entry provides a button for joining or leaving the group,
     * allowing users to manage their memberships.
     */
    RB.JoinedGroupsView = Backbone.View.extend({
        template: _.template(['<div class="search">', ' <span class="rb-icon rb-icon-search-dark"></span>', ' <input type="text" />', '</div>', '<div class="group-lists" />'].join('')),

        events: {
            'submit': '_onSubmit',
            'keyup .search input': '_onGroupSearchChanged',
            'change .search input': '_onGroupSearchChanged'
        },

        /*
         * Initialize the view.
         *
         * Args:
         *     options (object):
         *         Options for view construction.
         *
         * Option Args:
         *     groups (Array of object):
         *         Initial set of groups.
         */
        initialize: function initialize(options) {
            this.groups = options.groups;

            this._$listsContainer = null;
            this._$search = null;
            this._searchText = null;
            this._groupViews = [];
        },


        /**
         * Render the view.
         *
         * This will set up the elements and the list of SiteGroupsViews.
         *
         * Returns:
         *     RB.JoinedGroupsView.
         *     This object, for chaining.
         */
        render: function render() {
            this.$el.html(this.template());

            this._$listsContainer = this.$('.group-lists');
            this._$search = this.$('.search input');

            var _iteratorNormalCompletion = true;
            var _didIteratorError = false;
            var _iteratorError = undefined;

            try {
                for (var _iterator = Object.entries(this.groups)[Symbol.iterator](), _step; !(_iteratorNormalCompletion = (_step = _iterator.next()).done); _iteratorNormalCompletion = true) {
                    var _step$value = _slicedToArray(_step.value, 2),
                        localSiteName = _step$value[0],
                        groups = _step$value[1];

                    if (groups.length > 0) {
                        var view = new SiteGroupsView({
                            name: localSiteName,
                            groups: groups
                        });

                        view.$el.appendTo(this._$listsContainer);
                        view.render();

                        this._groupViews.push(view);
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

            return this;
        },


        /**
         * Handler for when the search box changes.
         *
         * This will instruct the SiteGroupsViews to filter their contents
         * by the text entered into the search box.
         */
        _onGroupSearchChanged: function _onGroupSearchChanged() {
            var _this3 = this;

            var text = this._$search.val();

            if (text !== this._searchText) {
                this._searchText = text;
                this._groupViews.forEach(function (view) {
                    return view.filterBy(_this3._searchText);
                });
            }
        },


        /**
         * Prevent form submission.
         *
         * This form live updates based on the content of the <input> field and
         * submitting it will result in a CSRF error.
         *
         * Args:
         *     e (Event):
         *         The form submission event.
         */
        _onSubmit: function _onSubmit(e) {
            e.preventDefault();
        }
    });
})();

//# sourceMappingURL=joinedGroupsView.js.map