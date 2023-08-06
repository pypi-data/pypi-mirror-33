'use strict';

RB.JSONSerializers = {
    onlyIfUnloaded: function onlyIfUnloaded(value, state) {
        return state.loaded ? undefined : value;
    },
    onlyIfUnloadedAndValue: function onlyIfUnloadedAndValue(value, state) {
        return !state.loaded && value ? value : undefined;
    },
    onlyIfValue: function onlyIfValue(value) {
        return value || undefined;
    },
    onlyIfNew: function onlyIfNew(value, state) {
        return state.isNew ? value : undefined;
    },
    textType: function textType(value) {
        return value ? 'markdown' : 'plain';
    }
};

//# sourceMappingURL=serializers.js.map