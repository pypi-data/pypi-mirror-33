webpackJsonp([16],{

/***/ 2204:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require) {

    var React = __webpack_require__(1);
    var GEPPETTO = __webpack_require__(71);

    $.widget.bridge('uitooltip', $.ui.tooltip);

    var saveControlComp = React.createClass({
        displayName: 'saveControlComp',

        attachTooltip: function attachTooltip() {
            var self = this;
            $('.SaveButton').uitooltip({
                position: { my: "right center", at: "left-25 center" },
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

        getInitialState: function getInitialState() {
            return {
                disableSave: true,
                tooltipLabel: "Click here to persist this project!",
                icon: "fa fa-star"
            };
        },

        componentDidMount: function componentDidMount() {

            var self = this;

            GEPPETTO.on(GEPPETTO.Events.Project_persisted, function () {
                self.setState({ disableSave: false });
                // update contents of what's displayed on tooltip
                $('.SaveButton').uitooltip({ content: "The project was persisted and added to your dashboard!",
                    position: { my: "right center", at: "left center" } });
                $(".SaveButton").mouseover().delay(2000).queue(function () {
                    $(this).mouseout().dequeue();
                });
                self.setState({ disableSave: true });
            });

            GEPPETTO.on('spin_persist', function () {
                self.setState({ icon: "fa fa-star fa-spin" });
            }.bind($(".saveButton")));

            GEPPETTO.on('stop_spin_persist', function () {
                self.setState({ icon: "fa fa-star" });
            }.bind($(".saveButton")));

            self.attachTooltip();

            GEPPETTO.on(GEPPETTO.Events.Project_loaded, function () {
                self.setState(self.evaluateState());
            });

            if (window.Project != undefined) {
                this.setState(this.evaluateState());
            }
        },

        evaluateState: function evaluateState() {
            return { disableSave: window.Project.persisted || !GEPPETTO.UserController.hasPermission(GEPPETTO.Resources.WRITE_PROJECT) };
        },

        clickEvent: function clickEvent() {
            var self = this;
            // update contents of what's displayed on tooltip
            $('.SaveButton').uitooltip({ content: "The project is getting persisted..." });
            $(".SaveButton").mouseover().delay(2000).queue(function () {
                $(this).mouseout().dequeue();
            });
            self.setState({ disableSave: true });
            GEPPETTO.CommandController.execute("Project.persist();");
            GEPPETTO.trigger("spin_persist");
        },

        render: function render() {
            return React.createElement(
                'div',
                { className: 'saveButton' },
                React.createElement(
                    'button',
                    { className: 'btn SaveButton pull-right', type: 'button', title: '',
                        rel: 'tooltip', onClick: this.clickEvent, disabled: this.state.disableSave },
                    React.createElement('i', { className: this.state.icon })
                )
            );
        }
    });

    return saveControlComp;
}.call(exports, __webpack_require__, exports, module),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ })

});
//# sourceMappingURL=16.bundle.js.map