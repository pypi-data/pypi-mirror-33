webpackJsonp([17],{

/***/ 2213:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require) {

	var React = __webpack_require__(1);
	var GEPPETTO = __webpack_require__(71);

	$.widget.bridge('uitooltip', $.ui.tooltip);

	var button = React.createClass({
		displayName: 'button',

		attachTooltip: function attachTooltip() {
			var self = this;
			$("#" + this.props.configuration.id).uitooltip({
				position: this.props.configuration.tooltipPosition,
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
					return self.state.tooltipLabel;
				}
			});
		},

		showToolTip: function showToolTip(tooltipLabel, tooltipPosition) {
			var position = tooltipPosition;
			if (position == undefined) {
				position = this.props.configuration.tooltipPosition;
			}

			var selector = $("#" + this.props.configuration.id);
			selector.uitooltip("option", "show");
			// update contents of what's displayed on tooltip
			selector.uitooltip({ content: tooltipLabel, position: position });
			selector.mouseover().delay(2000).queue(function () {
				$(this).mouseout().dequeue();
			});
		},

		hideToolTip: function hideToolTip() {
			$("#" + this.props.configuration.id).uitooltip("option", "hide");
		},

		getInitialState: function getInitialState() {
			return {
				disableButton: this.props.configuration.disabled,
				tooltipLabel: this.props.configuration.tooltipLabel,
				icon: this.props.configuration.icon
			};
		},

		componentDidMount: function componentDidMount() {
			this.attachTooltip();
			if (this.props.configuration.eventHandler != undefined) {
				this.props.configuration.eventHandler(this);
			}
		},

		render: function render() {
			return React.createElement(
				'div',
				null,
				React.createElement(
					'button',
					{ className: this.props.configuration.className + " btn pull-right", type: 'button', title: '',
						id: this.props.configuration.id, rel: 'tooltip', onClick: this.props.configuration.onClick },
					React.createElement('i', { className: this.state.icon })
				)
			);
		}
	});
	return button;
}.call(exports, __webpack_require__, exports, module),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ })

});
//# sourceMappingURL=17.bundle.js.map