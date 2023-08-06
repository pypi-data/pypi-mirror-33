webpackJsonp([10],{

/***/ 2212:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_RESULT__;var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _get = function get(object, property, receiver) { if (object === null) object = Function.prototype; var desc = Object.getOwnPropertyDescriptor(object, property); if (desc === undefined) { var parent = Object.getPrototypeOf(object); if (parent === null) { return undefined; } else { return get(parent, property, receiver); } } else if ("value" in desc) { return desc.value; } else { var getter = desc.get; if (getter === undefined) { return undefined; } return getter.call(receiver); } };

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require) {

	var React = __webpack_require__(1),
	    $ = __webpack_require__(16),
	    Button = __webpack_require__(2529),
	    GEPPETTO = __webpack_require__(71);

	__webpack_require__(3881);

	$.cookie = __webpack_require__(3883);

	var AbstractComponent = __webpack_require__(72);

	return function (_AbstractComponent) {
		_inherits(Tutorial, _AbstractComponent);

		function Tutorial(props) {
			_classCallCheck(this, Tutorial);

			var _this = _possibleConstructorReturn(this, (Tutorial.__proto__ || Object.getPrototypeOf(Tutorial)).call(this, props));

			_this.tutorials = [];

			_this.state = {
				tutorialData: {},
				activeTutorial: undefined,
				currentStep: 0
			};

			_this.prevStep = _this.prevStep.bind(_this);
			_this.nextStep = _this.nextStep.bind(_this);
			return _this;
		}

		/**
   * Stores cookie to avoid showing tutorial next time at startup
   */


		_createClass(Tutorial, [{
			key: 'dontShowAtStartup',
			value: function dontShowAtStartup(val) {
				var value = $('#ignoreTutorialCheck').prop('checked');
				$.cookie('ignore_tutorial', value);
			}

			/**
    * Initial message at launch of tutorial
    */

		}, {
			key: 'start',
			value: function start() {
				this.state.currentStep = 0;
				this.updateTutorialWindow();
				this.started = true;
			}
		}, {
			key: 'getActiveTutorial',
			value: function getActiveTutorial() {
				return this.state.tutorialData[this.state.activeTutorial];
			}
		}, {
			key: 'updateTutorialWindow',
			value: function updateTutorialWindow() {
				var self = this;
				if (this.getActiveTutorial() != undefined) {
					var step = this.getActiveTutorial().steps[this.state.currentStep];

					if (step.content_url != undefined) {
						$.ajax({
							type: 'GET',
							dataType: 'html',
							url: step.content_url,
							success: function success(responseData, textStatus, jqXHR) {
								step.message = responseData;
								self.forceUpdate();
							},
							error: function error(responseData, textStatus, errorThrown) {
								throw "Error retrieving tutorial: " + responseData + "  with error " + errorThrown;
							}
						});
					} else {
						this.forceUpdate();
					}

					//execute action associated with message
					if (step.action != undefined) {
						if (step.action != "") {
							eval(step.action);
						}
					}
				}
			}
		}, {
			key: 'gotToStep',
			value: function gotToStep(currentStep) {
				this.state.currentStep = currentStep;
				if (this.getActiveTutorial() != undefined) {
					if (this.state.currentStep <= this.getActiveTutorial().steps.length - 1) {
						this.updateTutorialWindow();
					} else {
						this.start();
					}
				}

				this.setDirty(true);
			}
		}, {
			key: 'nextStep',
			value: function nextStep() {
				this.state.currentStep++;
				if (this.state.currentStep <= this.getActiveTutorial().steps.length - 1) {
					this.updateTutorialWindow();
				} else {
					this.start();
				}

				this.setDirty(true);
			}
		}, {
			key: 'prevStep',
			value: function prevStep() {
				this.state.currentStep--;
				GEPPETTO.tutorialEnabled = false;
				this.updateTutorialWindow();
				this.setDirty(true);
			}
		}, {
			key: 'close',
			value: function close() {
				this.dialog.parent().hide();
			}
		}, {
			key: 'open',
			value: function open(started) {
				var p = this.dialog.parent();
				var shake = p.is(":visible");
				p.show();

				if (!started) {
					if (shake) {
						p.effect("shake", { distance: 5, times: 3 }, 500, undefined);
					}
				} else {
					//wait before ticking box, needed for dialog to appear and render
					setTimeout(function () {
						var ignoreTutorial = $.cookie('ignore_tutorial');
						if (ignoreTutorial == 'true') {
							$('#ignoreTutorialCheck').prop('checked', true);
						}
					}, 100);
				}
			}
		}, {
			key: 'setTutorial',
			value: function setTutorial(tutorialURL) {
				this.state.tutorialData = {};
				this.addTutorial(tutorialURL);
				this.setDirty(true);
			}
		}, {
			key: 'goToChapter',
			value: function goToChapter(chapter) {
				this.state.activeTutorial = chapter;
				this.start();
				this.setDirty(true);
			}
		}, {
			key: 'addTutorial',
			value: function addTutorial(tutorialURL, callback) {
				// do not add if the same url was already successfully added
				if (this.tutorials.includes(tutorialURL)) {
					if (callback != undefined) {
						callback(this.tutorials);
					}
					return;
				}

				var self = this;

				$.ajax({
					type: 'GET',
					dataType: 'json',
					url: tutorialURL,
					success: function success(responseData, textStatus, jqXHR) {
						self.tutorials.push(tutorialURL);
						self.setDirty(true);
						self.loadTutorial(responseData, false);
						// load tutorial
						if (callback != undefined) {
							callback(self.tutorials);
						}
					},
					error: function error(responseData, textStatus, errorThrown) {
						throw "Error retrieving tutorial: " + responseData + "  with error " + errorThrown;
					}
				});
			}
		}, {
			key: 'loadTutorial',
			value: function loadTutorial(tutorialData, start) {
				this.state.tutorialData[tutorialData.name] = tutorialData;

				if (start) {
					this.state.activeTutorial = tutorialData.name;
					this.state.currentStep = 0;
				}

				if (!this.getIgnoreTutorialCookie()) {
					if (start) {
						this.start();
						this.forceUpdate();
						if (!this.props.closeByDefault) {
							this.open(true);
						}
					}
				}
			}
		}, {
			key: 'showChaptersMenu',
			value: function showChaptersMenu(event) {
				var that = this;
				var allTutorials = Object.keys(this.state.tutorialData);
				if (allTutorials.length > 0) {

					var data = [];
					for (var i = 0; i < allTutorials.length; i++) {
						data.push({
							"label": allTutorials[i],
							"action": ["GEPPETTO.Tutorial.goToChapter('" + allTutorials[i] + "')"],
							"icon": "fa fa-bookmark",
							"position": i
						});
					}

					this.chaptersMenu.show({
						top: event.pageY,
						left: event.pageX + 1,
						groups: data,
						data: that
					});
				}

				if (event != null) {
					event.preventDefault();
				}
				return false;
			}
		}, {
			key: 'componentDidUpdate',
			value: function componentDidUpdate() {
				if (this.chaptersMenu == undefined) {
					var that = this;
					this.chaptersMenu = new GEPPETTO.ContextMenuView();

					var button = $("<div class='fa fa-leanpub' title='Select chapter'></div>").on('click', function (event) {
						that.showChaptersMenu(event);
						event.stopPropagation();
					}).bind(this);

					var dialog = this.dialog.parent();
					var closeButton = dialog.find("button.ui-dialog-titlebar-close");
					closeButton.off("click");
					closeButton.click(this.close.bind(this));
					dialog.find("div.ui-dialog-titlebar").prepend(button);
					$(button).addClass("widget-title-bar-button");
					this.dialog.css("overflow", "auto");
				}
			}
		}, {
			key: 'componentDidMount',
			value: function componentDidMount() {
				this.close();
				var self = this;

				GEPPETTO.on("widgetRestored", function (id) {
					if (self.$el[0].id == id) {
						self.forceUpdate();
					}
				});

				//launches specific tutorial is experiment is loaded
				GEPPETTO.on(GEPPETTO.Events.Model_loaded, function () {
					if (!self.dontShowTutorial) {
						//default tutorial when user doesn't specify one for this event
						if (self.props.tutorialURL != undefined) {
							self.addTutorial(self.props.tutorialURL);
						} else if (self.props.tutorialData != undefined) {
							self.loadTutorial(self.props.tutorialData, true);
						}
						self.dontShowTutorial = true;
					}
				});

				//Launches tutorial from button 
				GEPPETTO.on(GEPPETTO.Events.Show_Tutorial, function () {
					if (self.started == undefined) {
						self.loadTutorial(self.props.tutorialData, true);
						self.open(false);
					} else if (self.started) {
						self.open(false);
					} else {
						if (!self.state.visible) {
							self.start();
							self.open(false);
						} else {
							//default tutorial when user doesn't specify one for this event
							if (self.state.tutorialData == {}) {
								self.setTutorial("/org.geppetto.frontend/geppetto/js/components/interface/tutorial/configuration/experiment_loaded_tutorial.json", "Geppetto tutorial");
							} else {
								self.start();
							}
						}
					}
				});

				//Hides tutorial
				GEPPETTO.on(GEPPETTO.Events.Hide_Tutorial, function () {
					self.close();
				});

				GEPPETTO.Tutorial = this;

				if (GEPPETTO.ForegroundControls != undefined) {
					GEPPETTO.ForegroundControls.refresh();
				}
			}
		}, {
			key: 'getIgnoreTutorialCookie',
			value: function getIgnoreTutorialCookie() {
				var ignoreTutorial = $.cookie('ignore_tutorial');
				if (ignoreTutorial == undefined) {
					//sets to string instead of boolean since $.cookie returns string even when storing as boolean
					return false;
				} else {
					return ignoreTutorial === "true";
				}
			}
		}, {
			key: 'getHTML',
			value: function getHTML(message) {
				return { __html: message };
			}
		}, {
			key: 'getView',
			value: function getView() {
				// add data-type and data field + any other custom fields in the component-specific attribute
				var baseView = _get(Tutorial.prototype.__proto__ || Object.getPrototypeOf(Tutorial.prototype), 'getView', this).call(this);
				baseView.dataType = "array";
				baseView.data = this.tutorials;
				baseView.componentSpecific = {
					activeTutorial: this.state.activeTutorial,
					currentStep: this.state.currentStep
				};

				return baseView;
			}
		}, {
			key: 'setComponentSpecificView',
			value: function setComponentSpecificView(componentSpecific) {
				if (componentSpecific != undefined) {
					if (componentSpecific.activeTutorial != undefined) {
						this.goToChapter(componentSpecific.activeTutorial);
					}

					if (componentSpecific.currentStep != undefined) {
						this.gotToStep(componentSpecific.currentStep);
					}
				}
			}
		}, {
			key: 'setView',
			value: function setView(view) {
				// set base properties
				_get(Tutorial.prototype.__proto__ || Object.getPrototypeOf(Tutorial.prototype), 'setView', this).call(this, view);
				var self = this;
				var cb = function cb(tutorials) {
					// only restore chapter and step once all the tutorials are loaded
					if (tutorials.length == view.data.length) {
						self.setComponentSpecificView(view.componentSpecific);
					}
				};

				// set data
				if (view.data != undefined) {
					if (view.dataType == 'array') {
						if (view.data.length == this.tutorials.length) {
							this.setComponentSpecificView(view.componentSpecific);
							if (view.position != undefined) {
								this.updatePosition(view.position);
							}
						} else if (view.data.length > 0) {
							for (var i = 0; i < view.data.length; i++) {
								this.addTutorial(view.data[i], cb);
							}
						}
					}
				}

				this.setDirty(false);
			}
		}, {
			key: 'updatePosition',
			value: function updatePosition(position) {
				var left, top;
				var screenWidth = $(window).width();
				var screenHeight = $(window).height();

				if (position.left != undefined && position.top != undefined) {
					left = position.left;
					top = position.top;
				} else {
					left = screenWidth / 2 - this.dialog.parent().width() / 2;
					top = screenHeight / 2 - this.dialog.parent().height() / 2;
				}

				if (typeof top === 'string' && typeof left === 'string') {
					left = screenWidth / 2 - this.dialog.parent().width() / 2;
					top = screenHeight / 2 - this.dialog.parent().height() / 2;
				}

				this.dialog.parent().css("top", top + "px");
				this.dialog.parent().css("left", left + "px");
			}
		}, {
			key: 'render',
			value: function render() {

				var ignoreTutorial = this.getIgnoreTutorialCookie();
				var activeTutorial = this.getActiveTutorial();
				if (activeTutorial != undefined) {

					var step = activeTutorial.steps[this.state.currentStep];

					var dialog = this.dialog.parent();
					dialog.find(".ui-dialog-title").html(step.title);
					var iconClass = "";
					if (step.icon != null && step.icon != undefined && step.icon != "") {
						iconClass = step.icon + " fa-3x";
					}

					var prevDisabled = this.state.currentStep == 0;
					var lastStep = this.state.currentStep == activeTutorial.steps.length - 1;
					var lastStepLabel = this.state.currentStep == activeTutorial.steps.length - 1 ? "Restart" : "";
					var cookieClass = this.state.currentStep == 0 ? "checkbox-inline cookieTutorial" : "hide";

					var width = this.getActiveTutorial()["width"];
					var height = this.getActiveTutorial()["height"];

					if (height != undefined) {
						dialog.height(height + "px");
						//some padding on the bottom
						this.dialog.css("height", height - 15 + "px");
					}
					if (width != undefined) {
						dialog.width(width + "px");
						this.dialog.css("width", width + "px");
					}

					var showMemoryCheckbox = this.props.showMemoryCheckbox;
					if (showMemoryCheckbox == undefined) {
						showMemoryCheckbox = true;
					}

					return React.createElement(
						'div',
						{ className: 'mainTutorialContainer' },
						React.createElement(
							'div',
							{ className: "tutorial-message " + this.props.tutorialMessageClass },
							React.createElement('div', { id: 'tutorialIcon', className: iconClass }),
							React.createElement('div', { id: 'message', dangerouslySetInnerHTML: this.getHTML(step.message) })
						),
						React.createElement(
							'div',
							{ className: (activeTutorial.steps.length > 1 ? "visible " : "hide ") + "btn-group tutorial-buttons", role: 'group' },
							React.createElement(
								'div',
								{ className: (activeTutorial.steps.length > 1 ? "visible " : "hide ") + "tutorial-buttons" },
								React.createElement(
									'button',
									{ className: 'prevBtn btn btn-default btn-lg', disabled: prevDisabled, 'data-toogle': 'tooltip', 'data-placement': 'bottom', title: 'Previous step', 'data-container': 'body', onClick: this.prevStep },
									React.createElement(
										'span',
										null,
										React.createElement('i', { className: 'fa fa-arrow-left fa-2x', 'aria-hidden': 'true' })
									)
								),
								React.createElement(
									'button',
									{ className: 'nextBtn btn btn-default btn-lg', 'data-toogle': 'tooltip', 'data-placement': 'bottom', title: 'Next step', 'data-container': 'body', onClick: this.nextStep },
									React.createElement(
										'span',
										null,
										lastStepLabel,
										'   ',
										React.createElement('i', { className: lastStep ? "fa fa-undo fa-2x" : "fa fa-arrow-right fa-2x", 'aria-hidden': 'true' })
									)
								)
							),
							React.createElement(
								'label',
								{ className: (showMemoryCheckbox ? "visible " : "hide ") + cookieClass, id: 'ignoreTutorial' },
								React.createElement('input', { type: 'checkbox', id: 'ignoreTutorialCheck', value: 'Do not show tutorial at startup again.', onClick: this.dontShowAtStartup }),
								' Do not show tutorial at startup again.'
							)
						)
					);
				} else {
					return null;
				}
			}
		}]);

		return Tutorial;
	}(AbstractComponent);
}.call(exports, __webpack_require__, exports, module),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ 2529:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require) {

    var React = __webpack_require__(1);

    return React.createClass({

        mixins: [],

        displayName: 'Button',

        getDefaultProps: function getDefaultProps() {
            return {
                disabled: false,
                className: ''
            };
        },

        render: function render() {
            return React.DOM.button({
                type: 'button',
                className: 'btn ' + this.props.className,
                'data-toggle': this.props['data-toggle'],
                onClick: this.props.onClick,
                disabled: this.props.disabled
            }, React.DOM.i({ className: this.props.icon }, " " + this.props.children));
        }
    });
}.call(exports, __webpack_require__, exports, module),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ 3881:
/***/ (function(module, exports, __webpack_require__) {

// style-loader: Adds some css to the DOM by adding a <style> tag

// load the styles
var content = __webpack_require__(3882);
if(typeof content === 'string') content = [[module.i, content, '']];
// add the styles to the DOM
var update = __webpack_require__(18)(content, {});
if(content.locals) module.exports = content.locals;
// Hot Module Replacement
if(false) {
	// When the styles change, update the <style> tags
	if(!content.locals) {
		module.hot.accept("!!../../../../node_modules/css-loader/index.js!../../../../node_modules/less-loader/dist/cjs.js?{\"modifyVars\":{\"url\":\"'../../../extensions/geppetto-netpyne/css/colors'\"}}!./Tutorial.less", function() {
			var newContent = require("!!../../../../node_modules/css-loader/index.js!../../../../node_modules/less-loader/dist/cjs.js?{\"modifyVars\":{\"url\":\"'../../../extensions/geppetto-netpyne/css/colors'\"}}!./Tutorial.less");
			if(typeof newContent === 'string') newContent = [[module.id, newContent, '']];
			update(newContent);
		});
	}
	// When the module is disposed, remove the <style> tags
	module.hot.dispose(function() { update(); });
}

/***/ }),

/***/ 3882:
/***/ (function(module, exports, __webpack_require__) {

exports = module.exports = __webpack_require__(17)(undefined);
// imports


// module
exports.push([module.i, ".dark-orange {\n  color: #cc215a;\n}\n.orange {\n  color: #f23d7a;\n}\n.orange-color {\n  color: #f23d7a;\n}\n.orange-color-bg {\n  background-color: #f23d7a;\n}\n.tutorial {\n  overflow: auto;\n}\n#message {\n  height: 100%;\n  overflow: auto;\n}\n.mainTutorialContainer {\n  height: 100%;\n}\n.tutorial-message {\n  display: inline-block;\n  width: auto;\n  min-height: 0px;\n  max-height: none;\n  width: 100%;\n  height: 80%;\n  color: #f23d7a;\n  overflow: hidden;\n}\n.tutorial-message .invert {\n  filter: invert(100%);\n}\n.tutorial-message .center {\n  margin: 0 auto;\n  display: block;\n  margin-bottom: 20px;\n  margin-top: 20px;\n}\n.tutorial-message a {\n  color: #f23d7a;\n  cursor: pointer;\n  text-decoration: none;\n}\n.tutorial-message a:hover {\n  color: #cc215a;\n}\n#ignoreTutorial {\n  width: auto;\n  margin-top: 30px;\n  color: #f23d7a;\n}\n.tutorial-buttons {\n  width: 100%;\n  height: 20%;\n  text-align: center;\n}\n.prevBtn {\n  border: 0;\n  background-color: transparent !important;\n}\n.nextBtn {\n  border: 0;\n  background-color: transparent !important;\n}\n#tutorialIcon {\n  color: #f23d7a;\n  width: 100%;\n  text-align: center;\n  margin-bottom: 10px;\n}\n.tutorialTitle {\n  font-size: 16px;\n  padding: 0 !important;\n  margin: 0 !important;\n  font-weight: bold;\n  color: #f23d7a;\n  margin-left: 5px;\n}\n.showTutorial {\n  display: block;\n}\n.hideTutorial {\n  display: none;\n}\n", ""]);

// exports


/***/ }),

/***/ 3883:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_FACTORY__, __WEBPACK_AMD_DEFINE_RESULT__;/*!
 * JavaScript Cookie v2.2.0
 * https://github.com/js-cookie/js-cookie
 *
 * Copyright 2006, 2015 Klaus Hartl & Fagner Brack
 * Released under the MIT license
 */
;(function (factory) {
	var registeredInModuleLoader = false;
	if (true) {
		!(__WEBPACK_AMD_DEFINE_FACTORY__ = (factory),
				__WEBPACK_AMD_DEFINE_RESULT__ = (typeof __WEBPACK_AMD_DEFINE_FACTORY__ === 'function' ?
				(__WEBPACK_AMD_DEFINE_FACTORY__.call(exports, __webpack_require__, exports, module)) :
				__WEBPACK_AMD_DEFINE_FACTORY__),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));
		registeredInModuleLoader = true;
	}
	if (true) {
		module.exports = factory();
		registeredInModuleLoader = true;
	}
	if (!registeredInModuleLoader) {
		var OldCookies = window.Cookies;
		var api = window.Cookies = factory();
		api.noConflict = function () {
			window.Cookies = OldCookies;
			return api;
		};
	}
}(function () {
	function extend () {
		var i = 0;
		var result = {};
		for (; i < arguments.length; i++) {
			var attributes = arguments[ i ];
			for (var key in attributes) {
				result[key] = attributes[key];
			}
		}
		return result;
	}

	function init (converter) {
		function api (key, value, attributes) {
			var result;
			if (typeof document === 'undefined') {
				return;
			}

			// Write

			if (arguments.length > 1) {
				attributes = extend({
					path: '/'
				}, api.defaults, attributes);

				if (typeof attributes.expires === 'number') {
					var expires = new Date();
					expires.setMilliseconds(expires.getMilliseconds() + attributes.expires * 864e+5);
					attributes.expires = expires;
				}

				// We're using "expires" because "max-age" is not supported by IE
				attributes.expires = attributes.expires ? attributes.expires.toUTCString() : '';

				try {
					result = JSON.stringify(value);
					if (/^[\{\[]/.test(result)) {
						value = result;
					}
				} catch (e) {}

				if (!converter.write) {
					value = encodeURIComponent(String(value))
						.replace(/%(23|24|26|2B|3A|3C|3E|3D|2F|3F|40|5B|5D|5E|60|7B|7D|7C)/g, decodeURIComponent);
				} else {
					value = converter.write(value, key);
				}

				key = encodeURIComponent(String(key));
				key = key.replace(/%(23|24|26|2B|5E|60|7C)/g, decodeURIComponent);
				key = key.replace(/[\(\)]/g, escape);

				var stringifiedAttributes = '';

				for (var attributeName in attributes) {
					if (!attributes[attributeName]) {
						continue;
					}
					stringifiedAttributes += '; ' + attributeName;
					if (attributes[attributeName] === true) {
						continue;
					}
					stringifiedAttributes += '=' + attributes[attributeName];
				}
				return (document.cookie = key + '=' + value + stringifiedAttributes);
			}

			// Read

			if (!key) {
				result = {};
			}

			// To prevent the for loop in the first place assign an empty array
			// in case there are no cookies at all. Also prevents odd result when
			// calling "get()"
			var cookies = document.cookie ? document.cookie.split('; ') : [];
			var rdecode = /(%[0-9A-Z]{2})+/g;
			var i = 0;

			for (; i < cookies.length; i++) {
				var parts = cookies[i].split('=');
				var cookie = parts.slice(1).join('=');

				if (!this.json && cookie.charAt(0) === '"') {
					cookie = cookie.slice(1, -1);
				}

				try {
					var name = parts[0].replace(rdecode, decodeURIComponent);
					cookie = converter.read ?
						converter.read(cookie, name) : converter(cookie, name) ||
						cookie.replace(rdecode, decodeURIComponent);

					if (this.json) {
						try {
							cookie = JSON.parse(cookie);
						} catch (e) {}
					}

					if (key === name) {
						result = cookie;
						break;
					}

					if (!key) {
						result[name] = cookie;
					}
				} catch (e) {}
			}

			return result;
		}

		api.set = api;
		api.get = function (key) {
			return api.call(api, key);
		};
		api.getJSON = function () {
			return api.apply({
				json: true
			}, [].slice.call(arguments));
		};
		api.defaults = {};

		api.remove = function (key, attributes) {
			api(key, '', extend(attributes, {
				expires: -1
			}));
		};

		api.withConverter = init;

		return api;
	}

	return init(function () {});
}));


/***/ })

});
//# sourceMappingURL=10.bundle.js.map