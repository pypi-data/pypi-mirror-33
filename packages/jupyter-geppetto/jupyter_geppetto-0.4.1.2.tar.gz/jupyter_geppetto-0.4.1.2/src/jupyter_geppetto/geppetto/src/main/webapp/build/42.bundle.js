webpackJsonp([42],{

/***/ 658:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require, exports, module) {

    var React = __webpack_require__(1);

    var Checkbox = React.createClass({
        displayName: 'Checkbox',

        getInitialState: function getInitialState() {
            return {
                value: this.props.sync_value == 'true'
            };
        },
        handleChange: function handleChange(event) {
            this.setState({ value: event.target.checked });
            this.props.handleChange(event.target.value);
        },
        componentWillReceiveProps: function componentWillReceiveProps(nextProps) {
            this.setState({
                value: nextProps.sync_value == 'true'
            });
        },

        render: function render() {
            return React.createElement(
                'p',
                { className: "checkboxContainer" },
                React.createElement('input', { type: 'checkbox', id: this.props.id, checked: this.state.value, onChange: this.handleChange }),
                React.createElement('label', { htmlFor: this.props.id })
            );
        }
    });

    return Checkbox;
}.call(exports, __webpack_require__, exports, module),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ })

});
//# sourceMappingURL=42.bundle.js.map