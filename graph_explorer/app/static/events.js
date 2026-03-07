const GraphEvents = {
    _listeners: {},
    subscribe(event, fn) {
        if (!this._listeners[event]) this._listeners[event] = [];
        this._listeners[event].push(fn);
    },
    publish(event, data) {
        (this._listeners[event] || []).forEach(fn => fn(data));
    }
};