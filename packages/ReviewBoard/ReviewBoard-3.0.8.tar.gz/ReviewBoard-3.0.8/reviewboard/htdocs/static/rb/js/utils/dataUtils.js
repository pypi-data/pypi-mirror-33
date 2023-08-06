'use strict';

RB.DataUtils = {
    ArrayBufferTypes: {
        int8: {
            size: 1,
            funcName: 'setInt8'
        },
        uint8: {
            size: 1,
            funcName: 'setUint8'
        },
        int16: {
            size: 2,
            funcName: 'setInt16'
        },
        uint16: {
            size: 2,
            funcName: 'setUint16'
        },
        int32: {
            size: 4,
            funcName: 'setInt32'
        },
        uint32: {
            size: 4,
            funcName: 'setUint32'
        },
        float32: {
            size: 4,
            funcName: 'setFloat32'
        },
        float64: {
            size: 8,
            funcName: 'setFloat64'
        }
    },

    /**
     * Read a Blob as an ArrayBuffer.
     *
     * This is an asynchronous operation.
     *
     * Args:
     *     blob (Blob):
     *         The blob to read as an :js:class:`ArrayBuffer`.
     *
     *     onLoaded (function):
     *         The function to call when the blob has loaded. This will take
     *         the resulting :js:class:`ArrayBuffer` as an argument.
     */
    readBlobAsArrayBuffer: function readBlobAsArrayBuffer(blob, onLoaded) {
        RB.DataUtils._readBlobAs('readAsArrayBuffer', blob, onLoaded);
    },


    /**
     * Read a Blob as a text string.
     *
     * This is an asynchronous operation.
     *
     * Args:
     *     blob (Blob):
     *         The blob to read as text.
     *
     *     onLoaded (function):
     *         The function to call when the blob has loaded. This will take
     *         the resulting string as an argument.
     */
    readBlobAsString: function readBlobAsString(blob, onLoaded) {
        RB.DataUtils._readBlobAs('readAsText', blob, onLoaded);
    },


    /**
     * Read several Blobs as individual ArrayBuffers.
     *
     * This is an asynchronous operation.
     *
     * Args:
     *     blobs (Array):
     *         The array of :js:class:`Blob`s instances to read as
     *         :js:class:`ArrayBuffer`s
     *
     *     onLoaded (function):
     *         The function to call when the blobs have loaded. This will take
     *         one parameter per loaded :js:class:`ArrayBuffer`, in the order
     *         provided for the blobs.
     */
    readManyBlobsAsArrayBuffers: function readManyBlobsAsArrayBuffers(blobs, onLoaded) {
        RB.DataUtils._readManyBlobsAs('readBlobAsArrayBuffer', blobs, onLoaded);
    },


    /**
     * Read several Blobs as individual text strings.
     *
     * This is an asynchronous operation.
     *
     * Args:
     *     blobs (Array):
     *         The array of :js:class:`Blob`s to read as text.
     *
     *     onLoaded (function):
     *         The function to call when the blobs have loaded. This will take
     *         one parameter per loaded string, in the order provided for the
     *         blobs.
     */
    readManyBlobsAsStrings: function readManyBlobsAsStrings(blobs, onLoaded) {
        RB.DataUtils._readManyBlobsAs('readBlobAsString', blobs, onLoaded);
    },


    /**
     * Build an ArrayBuffer based on a schema.
     *
     * This takes a schema that specifies the data that should go into the
     * :js:class:`ArrayBuffer`. Each item in the schema is an object specifying
     * the type and the list of values of that type to add.
     *
     * Args:
     *     schema (Array):
     *         The schema containing the data to load. Each item in the array
     *         is an object that looks like::
     *
     *             {
     *                 type: 'uint8', // Or another type
     *                 values: [1, 2, 3, ...],
     *             }
     *
     *         See :js:data:`RB.DataUtils.ArrayBufferTypes`.
     *
     * Returns:
     *     ArrayBuffer:
     *     The resulting buffer built from the schema.
     */
    buildArrayBuffer: function buildArrayBuffer(schema) {
        var ArrayBufferTypes = RB.DataUtils.ArrayBufferTypes;
        var arrayLen = 0;

        for (var i = 0; i < schema.length; i++) {
            var item = schema[i];

            arrayLen += ArrayBufferTypes[item.type].size * item.values.length;
        }

        var arrayBuffer = new ArrayBuffer(arrayLen);
        var dataView = new DataView(arrayBuffer);
        var pos = 0;

        for (var _i = 0; _i < schema.length; _i++) {
            var _item = schema[_i];
            var values = _item.values;
            var littleEndian = !_item.bigEndian;
            var typeInfo = ArrayBufferTypes[_item.type];
            var func = dataView[typeInfo.funcName];
            var size = typeInfo.size;

            for (var j = 0; j < values.length; j++) {
                func.call(dataView, pos, values[j], littleEndian);
                pos += size;
            }
        }

        return arrayBuffer;
    },


    /**
     * Build a Blob based on a schema.
     *
     * This takes a schema that specifies the data that should go into the
     * :js:class:`Blob`. Each item in the schema is either an array of objects
     * specifying the type and the list of values of that type to add (see
     * :js:func:`RB.DataUtils.buildArrayBuffer` for details), a
     * :js:class:`Blob`, or string to add.
     *
     * Args:
     *     schema (Array):
     *         The schema containing the data to load. Each item in the array
     *         must be a :js:class:`Blob`, string, or an array of objects
     *         supported by :js:func:`RB.DataUtils.buildArrayBuffer`.
     *
     * Returns:
     *     Blob:
     *     The resulting blob built from the schema.
     */
    buildBlob: function buildBlob(schema) {
        var parts = [];

        for (var i = 0; i < schema.length; i++) {
            var schemaItem = schema[i];

            if (_.isArray(schemaItem)) {
                parts.push(RB.DataUtils.buildArrayBuffer(schemaItem));
            } else {
                parts.push(schemaItem);
            }
        }

        return new Blob(parts);
    },


    /**
     * Read a Blob using a specific FileReader function.
     *
     * This is a convenience function that wraps a :js:class:`FileReader`
     * function designed to load a blob as a certain type.
     *
     * Args:
     *     readFuncName (string):
     *         The function name on :js:class:`FileReader` to call.
     *
     *     blob (Blob):
     *         The blob to load.
     *
     *     onLoaded (function):
     *         The function to call when the blob has loaded. This will take
     *         the resulting value as an argument.
     */
    _readBlobAs: function _readBlobAs(readFuncName, blob, onLoaded) {
        var reader = new FileReader();

        reader.addEventListener('loadend', function () {
            return onLoaded(reader.result);
        });
        reader[readFuncName](blob);
    },


    /**
     * Read several Blobs using a specific FileReader function.
     *
     * This is a convenience function that wraps a :js:class:`FileReader`
     * function, chaining multiple results in order to asynchronously load
     * each of the blobs as a certain type.
     *
     * Args:
     *     readFuncName (string):
     *         The function name on :js:class:`FileReader` to call.
     *
     *     blobs (Array):
     *         The array of Blobs to load.
     *
     *     onLoaded (function):
     *         The function to call when the blobs have loaded. This will take
     *         an argument per value loaded.
     */
    _readManyBlobsAs: function _readManyBlobsAs(readFuncName, blobs, onLoaded) {
        var loadFunc = RB.DataUtils[readFuncName];
        var result = new Array(blobs.length);
        var numLoaded = 0;

        function onBlobLoaded(i, text) {
            result[i] = text;
            numLoaded++;

            if (numLoaded === blobs.length) {
                onLoaded.apply(null, result);
            }
        }

        blobs.forEach(function (blob, i) {
            loadFunc(blob, function (text) {
                return onBlobLoaded(i, text);
            });
        });
    }
};

//# sourceMappingURL=dataUtils.js.map