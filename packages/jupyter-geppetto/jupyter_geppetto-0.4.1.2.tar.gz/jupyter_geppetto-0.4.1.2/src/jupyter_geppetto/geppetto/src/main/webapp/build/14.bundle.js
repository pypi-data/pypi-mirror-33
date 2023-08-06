webpackJsonp([14],{

/***/ 2216:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_RESULT__;var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require) {

	var React = __webpack_require__(1);
	var GEPPETTO = __webpack_require__(71);
	__webpack_require__(3897);

	$.widget.bridge('uitooltip', $.ui.tooltip);

	var AbstractComponent = __webpack_require__(72);

	var ButtonComponent = React.createClass({
		displayName: 'ButtonComponent',

		icon: null,
		tooltip: null,
		label: null,
		actions: null,
		attachTooltip: function attachTooltip() {
			var self = this;
			$("#" + this.props.id).uitooltip({
				position: { my: "left+15 center", at: "right center" },
				tooltipClass: "tooltip-persist",
				show: {
					effect: "slide",
					direction: "right",
					delay: 200
				},
				hide: {
					effect: "slide",
					direction: "right",
					delay: 200
				},
				content: function content() {
					return self.props.title;
				}
			});
		},

		getInitialState: function getInitialState() {
			return {
				icon: this.icon,
				label: this.label,
				tooltip: this.tooltip,
				actions: this.actions,
				disabled: false
			};
		},

		componentDidMount: function componentDidMount() {
			this.attachTooltip();
			this.evaluateState();
		},

		onClick: function onClick() {
			//execute all actions
			for (var action in this.actions) {
				if (this.actions.hasOwnProperty(action)) {
					GEPPETTO.CommandController.execute(this.actions[action], true);
				}
			}

			this.evaluateState();
		},

		evaluateState: function evaluateState() {

			// condition could be function or string
			var condition = this.props.configuration.condition;
			var conditionResult = false;
			if (typeof condition === 'function') {
				conditionResult = condition();
			} else {
				if (condition != '') {
					conditionResult = eval(condition);
				}
			}

			if (conditionResult != undefined) {
				if (!conditionResult) {
					this.icon = this.props.configuration.false.icon;
					this.actions = this.props.configuration.false.actions;
					this.label = this.props.configuration.false.label;
					this.tooltip = this.props.configuration.false.tooltip;
				} else {
					this.icon = this.props.configuration.true.icon;
					this.actions = this.props.configuration.true.actions;
					this.label = this.props.configuration.true.label;
					this.tooltip = this.props.configuration.true.tooltip;
				}
			} else {
				this.icon = this.props.configuration.icon;
				this.actions = this.props.configuration.actions;
				this.label = this.props.configuration.label;
				this.tooltip = this.props.configuration.tooltip;
			}

			if (this.isMounted()) {
				this.setState({ toggled: conditionResult, icon: this.icon, actions: this.actions, label: this.label, tooltip: this.tooltip });
			}
		},

		render: function render() {
			return React.createElement(
				'button',
				{ className: 'btn btn-default btn-lg button-bar-btn', 'data-toogle': 'tooltip', onClick: this.onClick,
					'data-placement': 'bottom', title: this.state.tooltip, id: this.props.id },
				React.createElement(
					'span',
					{ className: this.state.icon },
					this.state.label
				)
			);
		}
	});

	return function (_AbstractComponent) {
		_inherits(ButtonBar, _AbstractComponent);

		function ButtonBar() {
			_classCallCheck(this, ButtonBar);

			return _possibleConstructorReturn(this, (ButtonBar.__proto__ || Object.getPrototypeOf(ButtonBar)).apply(this, arguments));
		}

		_createClass(ButtonBar, [{
			key: 'render',
			value: function render() {
				var buttons = [];

				//add buttons using the configuration passed on component creation
				for (var key in this.props.configuration) {
					var b = this.props.configuration[key];
					var id = b.id;
					//if ID was not assigned as part of the configuration, we assinged the key value to it
					if (id == null || id == undefined) {
						id = key;
					}
					buttons.push(React.createElement(ButtonComponent, { id: id, key: key, configuration: b }));
				}

				return React.createElement(
					'div',
					{ id: 'button-bar-container', className: 'button-bar-container' },
					React.createElement(
						'div',
						{ id: 'bar-div', className: 'toolbar' },
						React.createElement(
							'div',
							{ className: 'btn-group' },
							buttons
						)
					)
				);
			}
		}]);

		return ButtonBar;
	}(AbstractComponent);
}.call(exports, __webpack_require__, exports, module),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ 3897:
/***/ (function(module, exports, __webpack_require__) {

// style-loader: Adds some css to the DOM by adding a <style> tag

// load the styles
var content = __webpack_require__(3898);
if(typeof content === 'string') content = [[module.i, content, '']];
// add the styles to the DOM
var update = __webpack_require__(18)(content, {});
if(content.locals) module.exports = content.locals;
// Hot Module Replacement
if(false) {
	// When the styles change, update the <style> tags
	if(!content.locals) {
		module.hot.accept("!!../../../../node_modules/css-loader/index.js!../../../../node_modules/less-loader/dist/cjs.js?{\"modifyVars\":{\"url\":\"'../../../extensions/geppetto-netpyne/css/colors'\"}}!./ButtonBar.less", function() {
			var newContent = require("!!../../../../node_modules/css-loader/index.js!../../../../node_modules/less-loader/dist/cjs.js?{\"modifyVars\":{\"url\":\"'../../../extensions/geppetto-netpyne/css/colors'\"}}!./ButtonBar.less");
			if(typeof newContent === 'string') newContent = [[module.id, newContent, '']];
			update(newContent);
		});
	}
	// When the module is disposed, remove the <style> tags
	module.hot.dispose(function() { update(); });
}

/***/ }),

/***/ 3898:
/***/ (function(module, exports, __webpack_require__) {

exports = module.exports = __webpack_require__(17)(undefined);
// imports


// module
exports.push([module.i, ".button-bar-btn {\n  border: none !important;\n  margin-right: 5px;\n  margin-left: 5px;\n  min-width: 35px;\n  min-height: 35px;\n}\n", ""]);

// exports


/***/ })

});
//# sourceMappingURL=14.bundle.js.map