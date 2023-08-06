webpackJsonp([33],{

/***/ 1425:
/***/ (function(module, exports, __webpack_require__) {

// style-loader: Adds some css to the DOM by adding a <style> tag

// load the styles
var content = __webpack_require__(1426);
if(typeof content === 'string') content = [[module.i, content, '']];
// add the styles to the DOM
var update = __webpack_require__(18)(content, {});
if(content.locals) module.exports = content.locals;
// Hot Module Replacement
if(false) {
	// When the styles change, update the <style> tags
	if(!content.locals) {
		module.hot.accept("!!../../../../node_modules/css-loader/index.js!../../../../node_modules/less-loader/dist/cjs.js?{\"modifyVars\":{\"url\":\"'../../../extensions/geppetto-netpyne/css/colors'\"}}!./GoogleViewer.less", function() {
			var newContent = require("!!../../../../node_modules/css-loader/index.js!../../../../node_modules/less-loader/dist/cjs.js?{\"modifyVars\":{\"url\":\"'../../../extensions/geppetto-netpyne/css/colors'\"}}!./GoogleViewer.less");
			if(typeof newContent === 'string') newContent = [[module.id, newContent, '']];
			update(newContent);
		});
	}
	// When the module is disposed, remove the <style> tags
	module.hot.dispose(function() { update(); });
}

/***/ }),

/***/ 1426:
/***/ (function(module, exports, __webpack_require__) {

exports = module.exports = __webpack_require__(17)(undefined);
// imports


// module
exports.push([module.i, ".googleViewer {\n  height: 100%;\n}\n.googleviewer-widget {\n  padding: .5em 0em 0em !important;\n}\n", ""]);

// exports


/***/ }),

/***/ 1427:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_FACTORY__, __WEBPACK_AMD_DEFINE_RESULT__;(function(root, factory) {

	if (root === null) {
		throw new Error('Google-maps package can be used only in browser');
	}

	if (true) {
		!(__WEBPACK_AMD_DEFINE_FACTORY__ = (factory),
				__WEBPACK_AMD_DEFINE_RESULT__ = (typeof __WEBPACK_AMD_DEFINE_FACTORY__ === 'function' ?
				(__WEBPACK_AMD_DEFINE_FACTORY__.call(exports, __webpack_require__, exports, module)) :
				__WEBPACK_AMD_DEFINE_FACTORY__),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));
	} else if (typeof exports === 'object') {
		module.exports = factory();
	} else {
		root.GoogleMapsLoader = factory();
	}

})(typeof window !== 'undefined' ? window : null, function() {


	'use strict';


	var googleVersion = '3.18';

	var script = null;

	var google = null;

	var loading = false;

	var callbacks = [];

	var onLoadEvents = [];

	var originalCreateLoaderMethod = null;


	var GoogleMapsLoader = {};


	GoogleMapsLoader.URL = 'https://maps.googleapis.com/maps/api/js';

	GoogleMapsLoader.KEY = null;

	GoogleMapsLoader.LIBRARIES = [];

	GoogleMapsLoader.CLIENT = null;

	GoogleMapsLoader.CHANNEL = null;

	GoogleMapsLoader.LANGUAGE = null;

	GoogleMapsLoader.REGION = null;

	GoogleMapsLoader.VERSION = googleVersion;

	GoogleMapsLoader.WINDOW_CALLBACK_NAME = '__google_maps_api_provider_initializator__';


	GoogleMapsLoader._googleMockApiObject = {};


	GoogleMapsLoader.load = function(fn) {
		if (google === null) {
			if (loading === true) {
				if (fn) {
					callbacks.push(fn);
				}
			} else {
				loading = true;

				window[GoogleMapsLoader.WINDOW_CALLBACK_NAME] = function() {
					ready(fn);
				};

				GoogleMapsLoader.createLoader();
			}
		} else if (fn) {
			fn(google);
		}
	};


	GoogleMapsLoader.createLoader = function() {
		script = document.createElement('script');
		script.type = 'text/javascript';
		script.src = GoogleMapsLoader.createUrl();

		document.body.appendChild(script);
	};


	GoogleMapsLoader.isLoaded = function() {
		return google !== null;
	};


	GoogleMapsLoader.createUrl = function() {
		var url = GoogleMapsLoader.URL;

		url += '?callback=' + GoogleMapsLoader.WINDOW_CALLBACK_NAME;

		if (GoogleMapsLoader.KEY) {
			url += '&key=' + GoogleMapsLoader.KEY;
		}

		if (GoogleMapsLoader.LIBRARIES.length > 0) {
			url += '&libraries=' + GoogleMapsLoader.LIBRARIES.join(',');
		}

		if (GoogleMapsLoader.CLIENT) {
			url += '&client=' + GoogleMapsLoader.CLIENT + '&v=' + GoogleMapsLoader.VERSION;
		}

		if (GoogleMapsLoader.CHANNEL) {
			url += '&channel=' + GoogleMapsLoader.CHANNEL;
		}

		if (GoogleMapsLoader.LANGUAGE) {
			url += '&language=' + GoogleMapsLoader.LANGUAGE;
		}

		if (GoogleMapsLoader.REGION) {
			url += '&region=' + GoogleMapsLoader.REGION;
		}

		return url;
	};


	GoogleMapsLoader.release = function(fn) {
		var release = function() {
			GoogleMapsLoader.KEY = null;
			GoogleMapsLoader.LIBRARIES = [];
			GoogleMapsLoader.CLIENT = null;
			GoogleMapsLoader.CHANNEL = null;
			GoogleMapsLoader.LANGUAGE = null;
			GoogleMapsLoader.REGION = null;
			GoogleMapsLoader.VERSION = googleVersion;

			google = null;
			loading = false;
			callbacks = [];
			onLoadEvents = [];

			if (typeof window.google !== 'undefined') {
				delete window.google;
			}

			if (typeof window[GoogleMapsLoader.WINDOW_CALLBACK_NAME] !== 'undefined') {
				delete window[GoogleMapsLoader.WINDOW_CALLBACK_NAME];
			}

			if (originalCreateLoaderMethod !== null) {
				GoogleMapsLoader.createLoader = originalCreateLoaderMethod;
				originalCreateLoaderMethod = null;
			}

			if (script !== null) {
				script.parentElement.removeChild(script);
				script = null;
			}

			if (fn) {
				fn();
			}
		};

		if (loading) {
			GoogleMapsLoader.load(function() {
				release();
			});
		} else {
			release();
		}
	};


	GoogleMapsLoader.onLoad = function(fn) {
		onLoadEvents.push(fn);
	};


	GoogleMapsLoader.makeMock = function() {
		originalCreateLoaderMethod = GoogleMapsLoader.createLoader;

		GoogleMapsLoader.createLoader = function() {
			window.google = GoogleMapsLoader._googleMockApiObject;
			window[GoogleMapsLoader.WINDOW_CALLBACK_NAME]();
		};
	};


	var ready = function(fn) {
		var i;

		loading = false;

		if (google === null) {
			google = window.google;
		}

		for (i = 0; i < onLoadEvents.length; i++) {
			onLoadEvents[i](google);
		}

		if (fn) {
			fn(google);
		}

		for (i = 0; i < callbacks.length; i++) {
			callbacks[i](google);
		}

		callbacks = [];
	};


	return GoogleMapsLoader;

});


/***/ }),

/***/ 663:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_RESULT__;var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require) {

	__webpack_require__(1425);
	var React = __webpack_require__(1);
	var GoogleMapsLoader = __webpack_require__(1427);
	var AbstractComponent = __webpack_require__(72);

	return function (_AbstractComponent) {
		_inherits(GoogleViewer, _AbstractComponent);

		function GoogleViewer(props) {
			_classCallCheck(this, GoogleViewer);

			var _this2 = _possibleConstructorReturn(this, (GoogleViewer.__proto__ || Object.getPrototypeOf(GoogleViewer)).call(this, props));

			var _this = _this2;
			var mapSettings = {
				center: { lat: 0, lng: 0 },
				zoom: 1,
				streetViewControl: false,
				mapTypeControl: false
			};

			var path = _this2.extractFilesPath(_this2.props.data);
			var imageMapTypeSettings = {
				getTileUrl: function getTileUrl(coord, zoom) {
					var normalizedCoord = _this.getNormalizedCoord(coord, zoom);
					if (!normalizedCoord) {
						return null;
					}
					var bound = Math.pow(2, zoom);
					return _this.state.path + '/' + zoom + '/' + normalizedCoord.x + '/' + (bound - normalizedCoord.y - 1) + '.jpg';
				},
				isPng: false,
				maxZoom: 11,
				minZoom: 0,
				radius: 1738000,
				path: path
			};

			_this2.state = {
				mapSettings: $.extend(mapSettings, _this2.props.mapSettings),
				imageMapTypeSettings: $.extend(imageMapTypeSettings, _this2.props.imageMapTypeSettings),
				tileWidth: _this2.props.tileWidth != undefined ? _this2.props.tileWidth : 256,
				tileHeight: _this2.props.tileHeight != undefined ? _this2.props.tileHeight : 256,
				path: path
			};
			return _this2;
		}

		_createClass(GoogleViewer, [{
			key: 'extractFilesPath',
			value: function extractFilesPath(data) {
				var path;
				if (data != undefined) {
					if (data.getMetaType == undefined) {
						path = data;
					} else if (data.getMetaType() == "Instance") {
						if (data.getVariable().getInitialValues()[0].value.format == "GOOGLE_MAP") {
							path = data.getVariable().getInitialValues()[0].value.data;
						}
					}
				}
				return path;
			}
		}, {
			key: 'setData',
			value: function setData(data) {
				this.setState({ path: this.extractFilesPath(data) });
			}

			// Normalizes the coords that tiles repeat across the x axis (horizontally)
			// like the standard Google map tiles.

		}, {
			key: 'getNormalizedCoord',
			value: function getNormalizedCoord(coord, zoom) {
				var y = coord.y;
				var x = coord.x;

				// tile range in one direction range is dependent on zoom level
				// 0 = 1 tile, 1 = 2 tiles, 2 = 4 tiles, 3 = 8 tiles, etc
				var tileRange = 1 << zoom;

				// don't repeat across y-axis (vertically)
				if (y < 0 || y >= tileRange) {
					return null;
				}

				// repeat across x-axis
				if (x < 0 || x >= tileRange) {
					x = (x % tileRange + tileRange) % tileRange;
				}

				return { x: x, y: y };
			}
		}, {
			key: 'getMap',
			value: function getMap() {
				return this.map;
			}
		}, {
			key: 'setMap',
			value: function setMap(map) {
				this.map = map;
				this.addResizeHandler();
			}
		}, {
			key: 'componentDidMount',
			value: function componentDidMount() {
				var _this = this;
				GoogleMapsLoader.KEY = this.props.googleKey;
				GoogleMapsLoader.load(function (google) {
					var container = document.getElementById(_this.props.id + "_component");

					_this.map = new google.maps.Map(container, _this.state.mapSettings);

					// tileSize: new google.maps.Size(256, 256),
					_this.state.imageMapTypeSettings['tileSize'] = new google.maps.Size(_this.state.tileWidth, _this.state.tileHeight);
					var imageMapType = new google.maps.ImageMapType(_this.state.imageMapTypeSettings);

					_this.map.mapTypes.set('imageMapType', imageMapType);
					_this.map.setMapTypeId('imageMapType');

					$(window).resize(function () {
						google.maps.event.trigger(_this.map, "resize");
					});

					_this.addResizeHandler();
				});

				GoogleMapsLoader.onLoad(function (google) {
					//console.log('I just loaded google maps api');
				});
			}
		}, {
			key: 'addResizeHandler',
			value: function addResizeHandler() {
				var _this = this;
				_this.newCenter = null;
				google.maps.event.addListener(_this.map, 'idle', function () {
					if (_this.newCenter == null) {
						_this.newCenter = _this.map.getCenter();
					}
				});
				google.maps.event.addListener(_this.map, 'resize', function () {
					setTimeout(function () {
						_this.map.setCenter(_this.newCenter);
					}, 200);
				});
			}
		}, {
			key: 'download',
			value: function download() {
				//What do we do here?
				console.log("Downloading data...");
			}
		}, {
			key: 'render',
			value: function render() {
				return React.createElement('div', { key: this.props.id + "_component", id: this.props.id + "_component", className: 'googleViewer', style: this.props.style });
			}
		}]);

		return GoogleViewer;
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
//# sourceMappingURL=33.bundle.js.map