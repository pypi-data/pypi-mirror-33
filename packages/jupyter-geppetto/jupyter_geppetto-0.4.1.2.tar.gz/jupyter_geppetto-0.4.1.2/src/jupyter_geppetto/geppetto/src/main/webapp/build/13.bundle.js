webpackJsonp([13],{

/***/ 2215:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require) {
    __webpack_require__(3895);
    var React = __webpack_require__(1);

    var linkButton = React.createClass({
        displayName: 'linkButton',

        render: function render() {
            var customStyle = {
                left: this.props.left != undefined ? this.props.left : '41px',
                top: this.props.top != undefined ? this.props.top : '415px'
            };

            var iconClass = "fa {0}".format(this.props.icon);

            return React.createElement(
                'div',
                { id: 'github' },
                React.createElement(
                    'a',
                    { href: this.props.url, target: '_blank' },
                    React.createElement('icon', { className: iconClass, id: 'git', style: customStyle })
                )
            );
        }
    });

    return linkButton;
}.call(exports, __webpack_require__, exports, module),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ 3895:
/***/ (function(module, exports, __webpack_require__) {

// style-loader: Adds some css to the DOM by adding a <style> tag

// load the styles
var content = __webpack_require__(3896);
if(typeof content === 'string') content = [[module.i, content, '']];
// add the styles to the DOM
var update = __webpack_require__(18)(content, {});
if(content.locals) module.exports = content.locals;
// Hot Module Replacement
if(false) {
	// When the styles change, update the <style> tags
	if(!content.locals) {
		module.hot.accept("!!../../../../node_modules/css-loader/index.js!../../../../node_modules/less-loader/dist/cjs.js?{\"modifyVars\":{\"url\":\"'../../../extensions/geppetto-netpyne/css/colors'\"}}!./LinkButton.less", function() {
			var newContent = require("!!../../../../node_modules/css-loader/index.js!../../../../node_modules/less-loader/dist/cjs.js?{\"modifyVars\":{\"url\":\"'../../../extensions/geppetto-netpyne/css/colors'\"}}!./LinkButton.less");
			if(typeof newContent === 'string') newContent = [[module.id, newContent, '']];
			update(newContent);
		});
	}
	// When the module is disposed, remove the <style> tags
	module.hot.dispose(function() { update(); });
}

/***/ }),

/***/ 3896:
/***/ (function(module, exports, __webpack_require__) {

exports = module.exports = __webpack_require__(17)(undefined);
// imports


// module
exports.push([module.i, ".dark-orange {\n  color: #cc215a;\n}\n.orange {\n  color: #f23d7a;\n}\n.orange-color {\n  color: #f23d7a;\n}\n.orange-color-bg {\n  background-color: #f23d7a;\n}\n#github icon {\n  color: #f23d7a;\n  position: fixed;\n  text-decoration: none;\n  font-size: 20px;\n}\n#github icon:hover {\n  color: #cc215a;\n}\n", ""]);

// exports


/***/ })

});
//# sourceMappingURL=13.bundle.js.map