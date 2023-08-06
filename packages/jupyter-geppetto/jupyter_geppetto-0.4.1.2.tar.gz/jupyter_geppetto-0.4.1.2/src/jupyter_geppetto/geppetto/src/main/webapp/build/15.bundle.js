webpackJsonp([15],{

/***/ 2207:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require) {

    var React = __webpack_require__(1);
    var HomeButton = __webpack_require__(3811);

    var HomeControls = React.createClass({
        displayName: 'HomeControls',


        render: function render() {
            return React.DOM.div({ className: 'homeButton' }, React.createFactory(HomeButton)({ disabled: false }));
        }

    });

    return HomeControls;
}.call(exports, __webpack_require__, exports, module),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ 2271:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require) {
    /**
     * Button used as part of GEPPETTO Components
     *
     * @mixin Button
     */
    var React = __webpack_require__(1);

    return {
        displayName: 'Button',

        render: function render() {
            return React.DOM.button({
                type: 'button',
                id: this.props.id,
                className: 'btn ' + this.props.className + (this.props.hidden === true ? ' hiddenElement' : ''),
                'data-toggle': this.props['data-toggle'],
                onClick: this.props.onClick,
                disabled: this.props.disabled,
                icon: this.props.icon
            }, React.DOM.i({ className: this.props.icon }), " " + this.props.label);
        }
    };
}.call(exports, __webpack_require__, exports, module),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ 3811:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require) {

    var React = __webpack_require__(1),
        GEPPETTO = __webpack_require__(71);

    return React.createClass({
        mixins: [__webpack_require__(2271)],

        componentDidMount: function componentDidMount() {},

        getDefaultProps: function getDefaultProps() {
            return {
                label: '',
                className: 'HomeButton pull-right',
                icon: 'fa fa-home',
                onClick: function onClick() {
                    var targetWindow = '_blank';
                    if (GEPPETTO_CONFIGURATION.embedded) {
                        targetWindow = '_self';
                    }
                    var win = window.open("./", targetWindow);
                    win.focus();
                }
            };
        }

    });
}.call(exports, __webpack_require__, exports, module),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ })

});
//# sourceMappingURL=15.bundle.js.map