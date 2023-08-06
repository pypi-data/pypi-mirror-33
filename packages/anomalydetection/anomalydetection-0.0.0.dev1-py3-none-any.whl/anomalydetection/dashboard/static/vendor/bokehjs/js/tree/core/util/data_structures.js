"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var array_1 = require("./array");
var eq_1 = require("./eq");
var types_1 = require("./types");
var MultiDict = /** @class */ (function () {
    function MultiDict() {
        this._dict = {};
    }
    MultiDict.prototype._existing = function (key) {
        if (key in this._dict)
            return this._dict[key];
        else
            return null;
    };
    MultiDict.prototype.add_value = function (key, value) {
        /*
        if value == null
          throw new Error("Can't put null in this dict")
        if isArray(value)
          throw new Error("Can't put arrays in this dict")
        */
        var existing = this._existing(key);
        if (existing == null) {
            this._dict[key] = value;
        }
        else if (types_1.isArray(existing)) {
            existing.push(value);
        }
        else {
            this._dict[key] = [existing, value];
        }
    };
    MultiDict.prototype.remove_value = function (key, value) {
        var existing = this._existing(key);
        if (types_1.isArray(existing)) {
            var new_array = array_1.difference(existing, [value]);
            if (new_array.length > 0)
                this._dict[key] = new_array;
            else
                delete this._dict[key];
        }
        else if (eq_1.isEqual(existing, value)) {
            delete this._dict[key];
        }
    };
    MultiDict.prototype.get_one = function (key, duplicate_error) {
        var existing = this._existing(key);
        if (types_1.isArray(existing)) {
            if (existing.length === 1)
                return existing[0];
            else
                throw new Error(duplicate_error);
        }
        else
            return existing;
    };
    return MultiDict;
}());
exports.MultiDict = MultiDict;
var Set = /** @class */ (function () {
    function Set(obj) {
        if (obj == null) {
            this.values = [];
        }
        else if (obj instanceof Set) {
            this.values = array_1.copy(obj.values);
        }
        else {
            this.values = this._compact(obj);
        }
    }
    Set.prototype._compact = function (array) {
        var newArray = [];
        for (var _i = 0, array_2 = array; _i < array_2.length; _i++) {
            var item = array_2[_i];
            if (newArray.indexOf(item) === -1) {
                newArray.push(item);
            }
        }
        return newArray;
    };
    Set.prototype.push = function (item) {
        if (this.missing(item))
            this.values.push(item);
    };
    Set.prototype.remove = function (item) {
        var i = this.values.indexOf(item);
        this.values = this.values.slice(0, i).concat(this.values.slice(i + 1));
    };
    Set.prototype.length = function () {
        return this.values.length;
    };
    Set.prototype.includes = function (item) {
        return this.values.indexOf(item) != -1;
    };
    Set.prototype.missing = function (item) {
        return !this.includes(item);
    };
    Set.prototype.slice = function (from, to) {
        return this.values.slice(from, to);
    };
    Set.prototype.join = function (str) {
        return this.values.join(str);
    };
    Set.prototype.toString = function () {
        return this.join(', ');
    };
    Set.prototype.union = function (set) {
        set = new Set(set);
        return new Set(this.values.concat(set.values));
    };
    Set.prototype.intersect = function (set) {
        set = new Set(set);
        var newSet = new Set();
        for (var _i = 0, _a = set.values; _i < _a.length; _i++) {
            var item = _a[_i];
            if (this.includes(item) && set.includes(item))
                newSet.push(item);
        }
        return newSet;
    };
    Set.prototype.diff = function (set) {
        set = new Set(set);
        var newSet = new Set();
        for (var _i = 0, _a = this.values; _i < _a.length; _i++) {
            var item = _a[_i];
            if (set.missing(item))
                newSet.push(item);
        }
        return newSet;
    };
    return Set;
}());
exports.Set = Set;

//# sourceMappingURL=data_structures.js.map
