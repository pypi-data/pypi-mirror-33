webpackJsonp([12],{

/***/ 2203:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require) {

    __webpack_require__(3801);

    var React = __webpack_require__(1);
    var GEPPETTO = __webpack_require__(71);

    var logoDiv = React.createClass({
        displayName: 'logoDiv',

        componentDidMount: function componentDidMount() {
            GEPPETTO.on('spin_logo', function (label) {
                //TODO Fix this to use state instead and not touching the dom element with jQuery
                $("#geppettologo").addClass("fa-spin").attr('title', 'Loading data');
            }.bind($("." + this.props.logo)));

            GEPPETTO.on('stop_spin_logo', function (label) {
                $("#geppettologo").removeClass("fa-spin").attr('title', '');
            }.bind($("." + this.props.logo)));
        },

        render: function render() {
            return React.createElement('div', { className: this.props.logo });
        }
    });

    return logoDiv;
}.call(exports, __webpack_require__, exports, module),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ 3801:
/***/ (function(module, exports, __webpack_require__) {

// style-loader: Adds some css to the DOM by adding a <style> tag

// load the styles
var content = __webpack_require__(3802);
if(typeof content === 'string') content = [[module.i, content, '']];
// add the styles to the DOM
var update = __webpack_require__(18)(content, {});
if(content.locals) module.exports = content.locals;
// Hot Module Replacement
if(false) {
	// When the styles change, update the <style> tags
	if(!content.locals) {
		module.hot.accept("!!../../../../node_modules/css-loader/index.js!../../../../node_modules/less-loader/dist/cjs.js?{\"modifyVars\":{\"url\":\"'../../../extensions/geppetto-netpyne/css/colors'\"}}!./Logo.less", function() {
			var newContent = require("!!../../../../node_modules/css-loader/index.js!../../../../node_modules/less-loader/dist/cjs.js?{\"modifyVars\":{\"url\":\"'../../../extensions/geppetto-netpyne/css/colors'\"}}!./Logo.less");
			if(typeof newContent === 'string') newContent = [[module.id, newContent, '']];
			update(newContent);
		});
	}
	// When the module is disposed, remove the <style> tags
	module.hot.dispose(function() { update(); });
}

/***/ }),

/***/ 3802:
/***/ (function(module, exports, __webpack_require__) {

exports = module.exports = __webpack_require__(17)(undefined);
// imports


// module
exports.push([module.i, ".dark-orange {\n  color: #cc215a;\n}\n.orange {\n  color: #f23d7a;\n}\n.orange-color {\n  color: #f23d7a;\n}\n.orange-color-bg {\n  background-color: #f23d7a;\n}\n#geppettologo {\n  top: 12px;\n  height: 37px;\n  left: 33px;\n  position: absolute;\n  z-index: 3;\n  color: #f23d7a;\n  font-size: 33px;\n}\n#geppettologo:hover {\n  text-decoration: none;\n  color: red;\n  text-shadow: none;\n  -webkit-transition: 2000ms linear 0s;\n  -moz-transition: 2000ms linear 0s;\n  -o-transition: 2000ms linear 0s;\n  transition: 2000ms linear 0s;\n  outline: 0 none;\n}\n@media (-webkit-min-device-pixel-ratio: 2), (min-resolution: 192dpi) {\n  #geppettologo {\n    background-size: 170px 37px;\n  }\n}\n", ""]);

// exports


/***/ })

});
//# sourceMappingURL=12.bundle.js.map