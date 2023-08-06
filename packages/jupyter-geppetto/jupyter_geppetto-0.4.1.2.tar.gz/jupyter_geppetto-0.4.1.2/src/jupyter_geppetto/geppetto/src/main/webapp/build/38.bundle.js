webpackJsonp([38],{

/***/ 1275:
/***/ (function(module, exports, __webpack_require__) {

// style-loader: Adds some css to the DOM by adding a <style> tag

// load the styles
var content = __webpack_require__(1276);
if(typeof content === 'string') content = [[module.i, content, '']];
// add the styles to the DOM
var update = __webpack_require__(18)(content, {});
if(content.locals) module.exports = content.locals;
// Hot Module Replacement
if(false) {
	// When the styles change, update the <style> tags
	if(!content.locals) {
		module.hot.accept("!!../../../../node_modules/css-loader/index.js!../../../../node_modules/less-loader/dist/cjs.js?{\"modifyVars\":{\"url\":\"'../../../extensions/geppetto-netpyne/css/colors'\"}}!./ToggleButton.less", function() {
			var newContent = require("!!../../../../node_modules/css-loader/index.js!../../../../node_modules/less-loader/dist/cjs.js?{\"modifyVars\":{\"url\":\"'../../../extensions/geppetto-netpyne/css/colors'\"}}!./ToggleButton.less");
			if(typeof newContent === 'string') newContent = [[module.id, newContent, '']];
			update(newContent);
		});
	}
	// When the module is disposed, remove the <style> tags
	module.hot.dispose(function() { update(); });
}

/***/ }),

/***/ 1276:
/***/ (function(module, exports, __webpack_require__) {

exports = module.exports = __webpack_require__(17)(undefined);
// imports


// module
exports.push([module.i, ".dark-orange {\n  color: #cc215a;\n}\n.orange {\n  color: #f23d7a;\n}\n.orange-color {\n  color: #f23d7a;\n}\n.orange-color-bg {\n  background-color: #f23d7a;\n}\n.toggle-button-toggled {\n  color: white !important;\n  background: #f23d7a !important;\n}\n.toggle-button-hidden {\n  display: none;\n}\n.tooltip-toggle {\n  height: 25px;\n  max-width: 800px;\n  border-radius: 5px;\n  border: 1px solid black;\n  padding: 2px 4px 2px 4px;\n  background: white;\n  opacity: 1;\n  left: 200px;\n}\n", ""]);

// exports


/***/ }),

/***/ 611:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require) {

  var React = __webpack_require__(1);
  var GEPPETTO = __webpack_require__(71);
  __webpack_require__(1275);

  $.widget.bridge('uitooltip', $.ui.tooltip);

  var ToggleButton = React.createClass({
    displayName: 'ToggleButton',

    icon: null,
    tooltip: null,
    tooltipPosition: null,
    label: null,
    action: null,
    attachTooltip: function attachTooltip() {
      var self = this;
      self.tooltipPosition = this.props.configuration.tooltipPosition;
      if (self.tooltipPosition == null) {
        self.tooltipPosition = { my: "center bottom", at: "center top-10" };
      }
      $("#" + self.props.configuration.id).uitooltip({
        position: self.tooltipPosition,
        tooltipClass: "tooltip-toggle",
        show: null, // show immediately
        open: function open(event, ui) {
          if (typeof event.originalEvent === 'undefined') {
            return false;
          }

          var $id = $(ui.tooltip).attr('id');

          // close any lingering tooltips
          $('div.ui-tooltip').not('#' + $id).remove();
        },
        close: function close(event, ui) {
          ui.tooltip.hover(function () {
            $(this).stop(true).fadeTo(400, 1);
          }, function () {
            $(this).fadeOut('400', function () {
              $(this).remove();
            });
          });
        },
        content: function content() {
          return self.state.tooltip;
        }
      });
    },

    getInitialState: function getInitialState() {
      return {
        icon: this.icon,
        label: this.label,
        tooltip: this.tooltip,
        action: this.action,
        disabled: false
      };
    },

    componentDidMount: function componentDidMount() {
      this.attachTooltip();
      this.evaluateState();

      // attach handlers if any
      if (this.props.configuration.eventHandler != undefined) {
        this.props.configuration.eventHandler(this);
      }
    },

    clickEvent: function clickEvent() {
      this.evaluateState();
      // there may or may not be a dynamic action to be executed via console
      if (this.action != '') {
        GEPPETTO.CommandController.execute(this.action, true);
      }
      if (this.props.configuration.clickHandler != undefined) {
        this.props.configuration.clickHandler(this.props.id);
      }
      $('div.ui-tooltip').remove();
    },

    showToolTip: function showToolTip() {
      var self = this;
      var selfSelector = $("#" + self.props.configuration.id);
      selfSelector.uitooltip({ content: self.state.tooltip, position: { my: "right center", at: "left center" } });
      selfSelector.mouseover().delay(2000).queue(function () {
        $(this).mouseout().dequeue();
      });
    },

    evaluateState: function evaluateState() {
      // figure out if disabled
      var disableBtn = this.props.disabled;
      if (disableBtn == undefined) {
        // fall back on disableCondition from config if any
        var disableCondition = this.props.configuration.disableCondition;
        if (disableCondition != '' && disableCondition != undefined) {
          disableCondition = disableCondition.replace(/['"]+/g, '');
          disableBtn = eval(disableCondition);
        }
      }

      // figure out if hidden
      var hideBtn = this.props.hidden;
      if (hideBtn == undefined) {
        // fall back on disableCondition from config if any
        var hideCondition = this.props.configuration.hideCondition;
        if (hideCondition != '' && hideCondition != undefined) {
          hideCondition = hideCondition.replace(/['"]+/g, '');
          hideBtn = eval(hideCondition);
        }
      }

      // condition could be function or string
      var condition = this.props.configuration.condition;
      var conditionResult = false;
      if (typeof condition === 'function') {
        conditionResult = condition();
      } else {
        if (condition != '') {
          condition = condition.replace(/['"]+/g, '');
          conditionResult = eval(condition);
        }
      }

      if (!conditionResult) {
        this.icon = this.props.configuration.false.icon;
        this.action = this.props.configuration.false.action;
        this.label = this.props.configuration.false.label;
        this.tooltip = this.props.configuration.false.tooltip;
      } else {
        this.icon = this.props.configuration.true.icon;
        this.action = this.props.configuration.true.action;
        this.label = this.props.configuration.true.label;
        this.tooltip = this.props.configuration.true.tooltip;
      }

      if (this.isMounted()) {
        this.setState({ toggled: conditionResult, icon: this.icon, action: this.action, label: this.label, tooltip: this.tooltip, disabled: disableBtn, hidden: hideBtn });
      }
    },

    render: function render() {
      // build css for button
      var cssClass = this.props.configuration.id + " btn pull-right";

      // figure out if toggled to reflect visually with css class
      var toggled = false;
      if (this.props.toggled != undefined && typeof this.props.toggled === "boolean") {
        // if prop is passed ignore state, prop overrides precedence
        // NOTE: this lets the component be controlled from a parent with props
        toggled = this.props.toggled;
      } else {
        // fallback on internally kept state
        toggled = this.state.toggled;
      }

      if (toggled) {
        cssClass += " toggle-button-toggled";
      }

      // check if the button is being hidden from he parent via prop
      if (this.props.hidden === true) {
        cssClass += " toggle-button-hidden";
      }

      return React.createElement(
        'div',
        { className: 'toggleButton' },
        React.createElement(
          'button',
          { id: this.props.configuration.id, className: cssClass, type: 'button', title: '',
            rel: 'tooltip', onClick: this.clickEvent, disabled: this.props.disabled === true || this.state.disabled === true },
          React.createElement('i', { className: this.state.icon }),
          this.state.label
        )
      );
    }
  });

  return ToggleButton;
}.call(exports, __webpack_require__, exports, module),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ })

});
//# sourceMappingURL=38.bundle.js.map