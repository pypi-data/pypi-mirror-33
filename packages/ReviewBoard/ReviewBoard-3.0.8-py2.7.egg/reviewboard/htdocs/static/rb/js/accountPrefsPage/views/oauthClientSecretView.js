'use strict';

/**
 * A view for editing a client secret.
 *
 * This view hits the API to regenerate the associated application's
 * client secret and updates the ``<input>`` element with the updated value. It
 * also bundles a copy button so that the value can be copied to the user's
 * clipboard.
 */
RB.OAuthClientSecretView = Backbone.View.extend({
    events: {
        'click .copyable-text-input-link': '_onCopyClicked',
        'click .regenerate-secret-button': '_onRegenerateClicked'
    },

    /**
     * Initialize the view.
     *
     * Args:
     *     options (object):
     *         The view options.
     *
     * Option Args:
     *     apiURL (string):
     *         The URL of the API endpoint for the application.
     */
    initialize: function initialize(options) {
        this._apiURL = options.apiURL;
    },


    /**
     * Render the view.
     *
     * Returns:
     *     RB.OAuthClientSecretView:
     *     This view.
     */
    render: function render() {
        this._$input = this.$('input');
        this._$regen = this.$('.regenerate-secret-button');

        return this;
    },


    /**
     * Copy the client secret to the clipboard.
     *
     * Args:
     *     e (Event):
     *         The click event that triggered this handler.
     */
    _onCopyClicked: function _onCopyClicked(e) {
        e.preventDefault();
        e.stopPropagation();

        this._$input.focus().select();

        document.execCommand('copy');
    },


    /**
     * Regenerate the client secret.
     *
     * Args:
     *     e (Event):
     *         The click event that triggered this handler.
     */
    _onRegenerateClicked: function _onRegenerateClicked(e) {
        var _this = this;

        e.preventDefault();
        e.stopPropagation();

        this._$regen.prop('disabled', true);
        RB.apiCall({
            url: this._apiURL,
            method: 'PUT',
            data: {
                'regenerate_client_secret': 1
            },
            success: function success(rsp) {
                _this._$input.val(rsp.oauth_app.client_secret);
                _this._$regen.prop('disabled', false);
            },
            error: function error(xhr) {
                if (xhr.errorText) {
                    alert(xhr.errorText);
                }

                _this._$regen.prop('disabled', false);
            }
        });
    }
});

//# sourceMappingURL=oauthClientSecretView.js.map