webpackJsonp([40],{

/***/ 659:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_RESULT__;var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require, exports, module) {

	var React = __webpack_require__(1);
	var AbstractComponent = __webpack_require__(72);

	return function (_AbstractComponent) {
		_inherits(TextField, _AbstractComponent);

		function TextField(props) {
			_classCallCheck(this, TextField);

			var _this = _possibleConstructorReturn(this, (TextField.__proto__ || Object.getPrototypeOf(TextField)).call(this, props));

			_this.state = {
				value: _this.props.sync_value,
				handleChange: _this.handleChange.bind(_this),
				handleBlur: _this.handleBlur.bind(_this)
			};

			_this.handleChange = _this.handleChange.bind(_this);
			_this.handleBlur = _this.handleBlur.bind(_this);
			return _this;
		}
		// getInitialState: function () {
		// 	return { value: this.props.sync_value };
		// },


		_createClass(TextField, [{
			key: 'handleChange',
			value: function handleChange(event) {
				this.setState({ value: event.target.value });
				this.state.handleChange(event.target.value);
			}
		}, {
			key: 'handleBlur',
			value: function handleBlur(event) {
				//this.setState({value: event.target.value});
				this.state.handleBlur(event.target.value);
			}
		}, {
			key: 'componentWillReceiveProps',
			value: function componentWillReceiveProps(nextProps) {
				this.setState({
					value: nextProps.sync_value
				});
			}
		}, {
			key: 'sync',
			value: function sync() {
				var kernel = IPython.notebook.kernel;
				kernel.execute('from jupyter_geppetto.geppetto_comm import GeppettoJupyterGUISync');
				kernel.execute('tf = GeppettoJupyterGUISync.TextFieldSync(path="' + this.props.path + '",value="' + this.props.value + '")');
				kernel.execute('tf.sync()');
			}
		}, {
			key: 'componentDidMount',
			value: function componentDidMount() {
				if (!('TEXTFIELD' in GEPPETTO.ComponentFactory.componentsMap)) {
					GEPPETTO.ComponentFactory.componentsMap['TEXTFIELD'] = [];
				}
				GEPPETTO.ComponentFactory.componentsMap['TEXTFIELD'].push(this);

				this.sync();
			}
		}, {
			key: 'render',
			value: function render() {
				var readOnly = this.props.readOnly === true;
				return React.createElement('input', { readOnly: readOnly, type: 'text', id: this.props.id, value: this.state.value, onChange: this.handleChange, onBlur: this.handleBlur });
			}
		}]);

		return TextField;
	}(AbstractComponent);
}.call(exports, __webpack_require__, exports, module),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ 72:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_RESULT__;var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

/**
 *
 * High Level widget component
 * @module Widgets/Widget
 * @author Adrian Quintana (adrian@metacell.us)
 */
!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require) {

    var Backbone = __webpack_require__(94);
    var React = __webpack_require__(1);
    var ReactDOM = __webpack_require__(13);

    /**
     * Creates base view for widget
     */
    //https://gist.github.com/aldendaniels/5d94ecdbff89295f4cd6
    return function (_React$Component) {
        _inherits(AbstractComponent, _React$Component);

        function AbstractComponent(props) {
            _classCallCheck(this, AbstractComponent);

            var _this = _possibleConstructorReturn(this, (AbstractComponent.__proto__ || Object.getPrototypeOf(AbstractComponent)).call(this, props));

            _this.dirtyView = false;
            _this.container = null;
            window[_this.props.id] = _this;
            return _this;
        }

        _createClass(AbstractComponent, [{
            key: 'getContainer',
            value: function getContainer() {
                if (this.container == null) {
                    this.container = $(this.props.parentContainer).children().get(0);
                }

                // If widget is added in a react way parent Container will be null
                if (this.container == null) {
                    this.container = ReactDOM.findDOMNode(this);
                }

                return this.container;
            }
        }, {
            key: 'isWidget',
            value: function isWidget() {
                return false;
            }
        }, {
            key: 'help',
            value: function help() {
                return GEPPETTO.CommandController.getObjectCommands(this.props.id);
            }
        }, {
            key: 'getComponentType',
            value: function getComponentType() {
                return this.props.componentType;
            }

            /**
             * Gets the ID of the widget
             *
             * @command getId()
             * @returns {String} - ID of widget
             */

        }, {
            key: 'getId',
            value: function getId() {
                return this.props.id;
            }
        }, {
            key: 'getHelp',
            value: function getHelp() {
                return '### Inline help not yet available for this widget! \n\n' + 'Try the <a href="http://docs.geppetto.org/en/latest/usingwidgets.html" target="_blank">online documentation</a> instead.';
            }

            /**
             * Did something change in the state of the widget?
             *
             * @command isDirty()
             * @returns {boolean} - ID of widget
             */

        }, {
            key: 'isDirty',
            value: function isDirty() {
                return this.dirtyView;
            }

            /**
             * Explicitly sets status of view
             * NOTE: we need to be able to control this from outside the component
             *
             * @command setDirty()
             * @param {boolean} dirty
             */

        }, {
            key: 'setDirty',
            value: function setDirty(dirty) {
                this.dirtyView = dirty;
            }

            /**
             * Get view with attributes common to all widgets
             *
             * @returns {{size: {height: *, width: *}, position: {left: *, top: *}}}
             */

        }, {
            key: 'getView',
            value: function getView() {
                return {
                    widgetType: this.getComponentType(),
                    isWidget: this.isWidget()
                };
            }

            /**
             * Set attributes common to all widgets - override for widget specific behaviour
             *
             * @param view
             */

        }, {
            key: 'setView',
            value: function setView(view) {
                // after setting view through setView, reset dirty flag
                this.dirtyView = false;
            }
        }, {
            key: 'isStateLess',
            value: function isStateLess() {
                return this.props.isStateless;
            }
        }, {
            key: 'render',
            value: function render() {}
        }]);

        return AbstractComponent;
    }(React.Component);
}.call(exports, __webpack_require__, exports, module),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ })

});
//# sourceMappingURL=40.bundle.js.map