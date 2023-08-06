webpackJsonp([4],{

/***/ 2208:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require) {

    var React = __webpack_require__(1);

    var RunButton = __webpack_require__(3812);
    var PlayButton = __webpack_require__(3813);
    var PauseButton = __webpack_require__(3814);
    var StopButton = __webpack_require__(3815);
    var HelpButton = __webpack_require__(3816);
    var MenuButton = __webpack_require__(487);

    var GEPPETTO = __webpack_require__(71);

    __webpack_require__(3820);

    var SimulationControls = React.createClass({
        displayName: 'SimulationControls',


        getInitialState: function getInitialState() {
            return {
                disableRun: true,
                disablePlay: true,
                disablePause: true,
                disableStop: true
            };
        },

        getDefaultProps: function getDefaultProps() {
            return {
                hideHelp: false,
                hideRun: false,
                hidePlay: false,
                hidePause: false,
                hideStop: false
            };
        },

        permissions: function permissions() {
            var experiment = window.Project.getActiveExperiment();
            var writePermission = GEPPETTO.UserController.hasPermission(GEPPETTO.Resources.WRITE_PROJECT);
            var runPermission = GEPPETTO.UserController.hasPermission(GEPPETTO.Resources.RUN_EXPERIMENT);
            var projectPersisted = experiment.getParent().persisted;
            var login = GEPPETTO.UserController.isLoggedIn() && GEPPETTO.UserController.hasPersistence();
            var readOnlyProject = window.Project.isReadOnly();

            if (writePermission && runPermission && projectPersisted && login && !readOnlyProject) {
                return true;
            }

            return false;
        },

        componentDidMount: function componentDidMount() {
            var self = this;

            GEPPETTO.on(GEPPETTO.Events.Experiment_loaded, function () {
                self.updateStatus();
            });

            GEPPETTO.on(GEPPETTO.Events.Project_persisted, function () {
                self.updateStatus();
            });

            GEPPETTO.on(GEPPETTO.Events.Project_loaded, function () {
                self.updateStatus();
            });

            GEPPETTO.on(GEPPETTO.Events.Experiment_running, function () {
                self.updateStatus();
            });

            GEPPETTO.on(GEPPETTO.Events.Experiment_failed, function (id) {
                var activeExperiment = window.Project.getActiveExperiment();
                if (activeExperiment != null || undefined) {
                    if (activeExperiment.getId() == id) {
                        self.setState({ disableRun: false, disablePlay: true, disablePause: true, disableStop: true });
                    }
                }
            });

            GEPPETTO.on(GEPPETTO.Events.Experiment_completed, function () {
                self.updateStatus();
            });

            GEPPETTO.on(GEPPETTO.Events.Experiment_play, function (options) {
                self.updateStatus();
            });

            GEPPETTO.on(GEPPETTO.Events.Experiment_resume, function () {
                self.updateStatus();
            });

            GEPPETTO.on(GEPPETTO.Events.Experiment_pause, function () {
                self.updateStatus();
            });

            GEPPETTO.on(GEPPETTO.Events.Experiment_stop, function (options) {
                self.updateStatus();
            });

            GEPPETTO.on(GEPPETTO.Events.Experiment_deleted, function () {
                var experiment = window.Project.getActiveExperiment();
                if (experiment == null || undefined) {
                    self.setState({ disableRun: true, disablePlay: true, disablePause: true, disableStop: true });
                }
            });

            GEPPETTO.on('disable_all', function () {
                self.setState({ disableRun: true, disablePlay: true, disablePause: true, disableStop: true });
            });

            GEPPETTO.on(GEPPETTO.Events.Experiment_over, function () {
                self.updateStatus();
            });

            this.updateStatus();
        },

        updateStatus: function updateStatus() {
            var experiment = window.Project.getActiveExperiment();

            if (experiment != null || undefined) {
                if (experiment.getStatus() == GEPPETTO.Resources.ExperimentStatus.COMPLETED) {
                    if (GEPPETTO.ExperimentsController.isPaused()) {
                        this.setState({ disableRun: true, disablePlay: false, disablePause: true, disableStop: false });
                    } else if (GEPPETTO.ExperimentsController.isPlaying()) {
                        this.setState({ disableRun: true, disablePlay: true, disablePause: false, disableStop: false });
                    } else if (GEPPETTO.ExperimentsController.isStopped()) {
                        this.setState({ disableRun: true, disablePlay: false, disablePause: true, disableStop: true });
                    }
                } else if (experiment.getStatus() == GEPPETTO.Resources.ExperimentStatus.RUNNING) {
                    this.setState({ disableRun: true, disablePlay: true, disablePause: true, disableStop: true });
                } else if (experiment.getStatus() == GEPPETTO.Resources.ExperimentStatus.ERROR) {
                    if (this.permissions()) {
                        this.setState({ disableRun: false, disablePlay: true, disablePause: true, disableStop: true });
                    } else {
                        this.setState({ disableRun: true, disablePlay: true, disablePause: true, disableStop: true });
                    }
                } else if (experiment.getStatus() == GEPPETTO.Resources.ExperimentStatus.DESIGN) {
                    if (this.permissions()) {
                        this.setState({ disableRun: false, disablePlay: true, disablePause: true, disableStop: true });
                    } else {
                        this.setState({ disableRun: true, disablePlay: true, disablePause: true, disableStop: true });
                    }
                }
            }
        },

        render: function render() {

            var runButton = "";
            if (this.props.runConfiguration != undefined) {
                this.props.runConfiguration.buttonDisabled = this.state.disableRun;
                runButton = React.createElement(MenuButton, { configuration: this.props.runConfiguration });
            } else {
                runButton = React.createElement(RunButton, { disabled: this.state.disableRun, hidden: this.props.hideRun });
            }

            return React.createElement(
                'div',
                { className: 'simulation-controls' },
                React.createElement(HelpButton, { disabled: false, hidden: this.props.hideHelp }),
                React.createElement(StopButton, { disabled: this.state.disableStop, hidden: this.props.hideStop }),
                React.createElement(PauseButton, { disabled: this.state.disablePause, hidden: this.props.hidePause }),
                React.createElement(PlayButton, { disabled: this.state.disablePlay, hidden: this.props.hidePlay }),
                runButton
            );
        }

    });

    return SimulationControls;
}.call(exports, __webpack_require__, exports, module),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ 2271:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require) {
    /**
     * Button used as part of GEPPETTO Components
     *
     * @mixin Button
     */
    var React = __webpack_require__(1);

    return {
        displayName: 'Button',

        render: function render() {
            return React.DOM.button({
                type: 'button',
                id: this.props.id,
                className: 'btn ' + this.props.className + (this.props.hidden === true ? ' hiddenElement' : ''),
                'data-toggle': this.props['data-toggle'],
                onClick: this.props.onClick,
                disabled: this.props.disabled,
                icon: this.props.icon
            }, React.DOM.i({ className: this.props.icon }), " " + this.props.label);
        }
    };
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

/***/ 3812:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require) {

    var React = __webpack_require__(1),
        GEPPETTO = __webpack_require__(71);

    return React.createClass({
        mixins: [__webpack_require__(2271)],

        componentDidMount: function componentDidMount() {},

        getDefaultProps: function getDefaultProps() {
            return {
                label: 'Run',
                className: 'pull-right',
                icon: 'fa fa-cogs',
                onClick: function onClick() {
                    GEPPETTO.Flows.onRun("Project.getActiveExperiment().run();");
                }
            };
        }

    });
}.call(exports, __webpack_require__, exports, module),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ 3813:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require) {

    var React = __webpack_require__(1),
        GEPPETTO = __webpack_require__(71);

    return React.createClass({
        mixins: [__webpack_require__(2271)],

        componentDidMount: function componentDidMount() {},

        getDefaultProps: function getDefaultProps() {
            return {
                label: 'Play',
                className: 'pull-right',
                icon: 'fa fa-play',
                onClick: function onClick() {

                    if (GEPPETTO.ExperimentsController.isPaused()) {
                        GEPPETTO.CommandController.execute("Project.getActiveExperiment().resume();");
                    } else {
                        if (GEPPETTO.isKeyPressed("shift")) {
                            GEPPETTO.Flows.onPlay("Project.getActiveExperiment().play();");
                        } else {
                            GEPPETTO.Flows.onPlay("Project.getActiveExperiment().playAll();");
                        }
                    }
                }
            };
        }

    });
}.call(exports, __webpack_require__, exports, module),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ 3814:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require) {

    var React = __webpack_require__(1),
        GEPPETTO = __webpack_require__(71);

    return React.createClass({
        mixins: [__webpack_require__(2271)],

        componentDidMount: function componentDidMount() {},

        getDefaultProps: function getDefaultProps() {
            return {
                label: 'Pause',
                className: 'pull-right',
                icon: 'fa fa-pause',
                onClick: function onClick() {
                    GEPPETTO.CommandController.execute("Project.getActiveExperiment().pause()", true);
                }
            };
        }

    });
}.call(exports, __webpack_require__, exports, module),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ 3815:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require) {

    var React = __webpack_require__(1),
        GEPPETTO = __webpack_require__(71);

    return React.createClass({
        mixins: [__webpack_require__(2271)],

        componentDidMount: function componentDidMount() {},

        getDefaultProps: function getDefaultProps() {
            return {
                label: 'Stop',
                className: 'pull-right',
                icon: 'fa fa-stop',
                onClick: function onClick() {
                    GEPPETTO.CommandController.execute("Project.getActiveExperiment().stop()", true);
                }
            };
        }

    });
}.call(exports, __webpack_require__, exports, module),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ 3816:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require) {

    var React = __webpack_require__(1),
        ReactDOM = __webpack_require__(13),
        GEPPETTO = __webpack_require__(71);
    $ = __webpack_require__(16), HelpModal = __webpack_require__(3817);

    return React.createClass({
        mixins: [__webpack_require__(2271)],

        componentDidMount: function componentDidMount() {

            GEPPETTO.on('simulation:show_helpwindow', function () {
                ReactDOM.render(React.createFactory(HelpModal)({ show: true }), document.getElementById('modal-region'));

                $("#help-modal").css("margin-right", "-20px");
                $('#help-modal').css('max-height', $(window).height() * 0.7);
                $('#help-modal .modal-body').css('max-height', $(window).height() * 0.5);
            });

            GEPPETTO.on('simulation:hide_helpwindow', function () {
                GEPPETTO.ComponentFactory.addComponent('LOADINGSPINNER', { show: true, keyboard: false, logo: "gpt-gpt_logo" }, document.getElementById("modal-region"));
            });
        },

        getDefaultProps: function getDefaultProps() {
            return {
                label: 'Help',
                id: 'genericHelpBtn',
                className: 'pull-right help-button',
                icon: 'fa fa-info-circle',
                onClick: function onClick() {
                    GEPPETTO.CommandController.execute("G.showHelpWindow(true)", true);
                }
            };
        }
    });
}.call(exports, __webpack_require__, exports, module),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ 3817:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require) {

    var React = __webpack_require__(1),
        Button = __webpack_require__(2529),
        GEPPETTO = __webpack_require__(71);

    __webpack_require__(3818);

    return React.createClass({
        mixins: [__webpack_require__(182)],

        startTutorial: function startTutorial() {
            GEPPETTO.trigger('start:tutorial');
            GEPPETTO.tutorialEnabled = true;
            this.hide();
        },

        render: function render() {
            return React.createElement(
                'div',
                { className: 'modal fade', id: 'help-modal' },
                React.createElement(
                    'div',
                    { className: 'modal-dialog' },
                    React.createElement(
                        'div',
                        { className: 'modal-content' },
                        React.createElement(
                            'div',
                            { className: 'modal-header' },
                            React.createElement(
                                'a',
                                { className: 'btn pull-right', icon: 'fa-file-text', href: 'http://docs.geppetto.org', target: '_blank' },
                                'Docs '
                            ),
                            React.createElement(
                                'h4',
                                { className: 'modal-title pagination-centered' },
                                'Quick Help'
                            )
                        ),
                        React.createElement(
                            'div',
                            { className: 'modal-body' },
                            React.createElement(
                                'h4',
                                null,
                                'Navigation Controls'
                            ),
                            React.createElement(
                                'h5',
                                null,
                                'Rotation'
                            ),
                            React.createElement(
                                'p',
                                null,
                                'Left click and drag with the mouse to rotate.'
                            ),
                            React.createElement(
                                'h5',
                                null,
                                'Pan'
                            ),
                            React.createElement(
                                'p',
                                null,
                                'Right click and drag with the mouse to pan.'
                            ),
                            React.createElement(
                                'h5',
                                null,
                                'Zoom'
                            ),
                            React.createElement(
                                'p',
                                null,
                                'Wheel click and move your mouse up and down to zoom in and out. In addition, you can use the buttons in the upper left corner. The Home button resets the view.'
                            ),
                            React.createElement(
                                'h4',
                                null,
                                'Selection Controls'
                            ),
                            React.createElement(
                                'p',
                                null,
                                'Left click will select the closest object under the pointer. Holding ',
                                React.createElement(
                                    'kbd',
                                    null,
                                    'Shift'
                                ),
                                ' enables multiple objects to be selected at once.'
                            ),
                            React.createElement(
                                'h5',
                                null,
                                'Selection Order'
                            ),
                            React.createElement(
                                'p',
                                null,
                                'Solid objects are selected over closer transparent objects. Holding ',
                                React.createElement(
                                    'kbd',
                                    null,
                                    'Ctrl'
                                ),
                                ' enables selection of the closest object regardless.'
                            ),
                            React.createElement(
                                'p',
                                null,
                                'To toggle through multiple stacked transparent objects, just keep clicking.'
                            ),
                            React.createElement(
                                'h5',
                                null,
                                'Clear Selection'
                            ),
                            React.createElement(
                                'p',
                                null,
                                'To unselect all objects simply click on empty space with ',
                                React.createElement(
                                    'kbd',
                                    null,
                                    'Ctrl'
                                ),
                                ' pressed.'
                            ),
                            React.createElement(
                                'h4',
                                null,
                                'Geppetto Console'
                            ),
                            React.createElement(
                                'p',
                                null,
                                'The console provides a way to interact with Geppetto without having to use the UI controls. Through the console, the user can control the Geppetto project and experiments and use the other features available.'
                            ),
                            React.createElement(
                                'h5',
                                null,
                                'Commands'
                            ),
                            React.createElement(
                                'p',
                                null,
                                'Open the console and type help() in it to view list of available commands, a description on how to use each one of them is also provided.'
                            ),
                            React.createElement(
                                'h5',
                                null,
                                'Autocompletion'
                            ),
                            React.createElement(
                                'p',
                                null,
                                'Console autcompletes a command once you start typing. Pressing double',
                                React.createElement(
                                    'kbd',
                                    null,
                                    'Tab'
                                ),
                                'provides list of available commands that match the entered input.'
                            ),
                            React.createElement(
                                'h4',
                                null,
                                'Loading a Project'
                            ),
                            React.createElement(
                                'h5',
                                null,
                                'Using Controls'
                            ),
                            React.createElement(
                                'p',
                                null,
                                'Use the home button button in the top right corner to go back to the dashboard load a Geppetto project by double-clicking on it.'
                            ),
                            React.createElement(
                                'h5',
                                null,
                                'Using console'
                            ),
                            React.createElement(
                                'p',
                                null,
                                'Projects can be loaded via console using commands',
                                React.createElement(
                                    'a',
                                    { className: 'label label-default' },
                                    'Project.loadFromURL(projectURL)'
                                )
                            ),
                            React.createElement(
                                'h5',
                                null,
                                'Passing a parameter via URL'
                            ),
                            React.createElement(
                                'p',
                                null,
                                'A project can be loaded by specifying its ID as a paramater in the Geppetto URL, for easy bookmarking. This will automatically load the project when the Geppetto simulation environment is opened. To use this feature add the query string paramater ',
                                React.createElement(
                                    'a',
                                    { className: 'label label-default' },
                                    'load_project_from_id=PROJECT_ID'
                                ),
                                ', where',
                                React.createElement(
                                    'a',
                                    { className: 'label label-default' },
                                    'PROJECT_ID'
                                ),
                                ' corresponds to the ID of the project you want to load.'
                            ),
                            React.createElement('div', { className: 'help-small-spacer help-clearer' }),
                            React.createElement(
                                'h4',
                                null,
                                'Colour coding for connections and connected elements'
                            ),
                            React.createElement('div', { className: 'circle default help-clearer left-floater' }),
                            React.createElement(
                                'div',
                                { className: 'circle-description left-floater' },
                                'The element is ',
                                React.createElement(
                                    'b',
                                    null,
                                    'unselected'
                                ),
                                '.'
                            ),
                            React.createElement('div', { className: 'circle selected help-clearer left-floater' }),
                            React.createElement(
                                'div',
                                { className: 'circle-description left-floater' },
                                'The element is ',
                                React.createElement(
                                    'b',
                                    null,
                                    'selected.'
                                )
                            ),
                            React.createElement('div', { className: 'circle input help-clearer left-floater' }),
                            React.createElement(
                                'div',
                                { className: 'circle-description left-floater' },
                                'The element is an ',
                                React.createElement(
                                    'b',
                                    null,
                                    'input'
                                ),
                                ' to the selected one.'
                            ),
                            React.createElement('div', { className: 'circle output help-clearer left-floater' }),
                            React.createElement(
                                'div',
                                { className: 'circle-description left-floater' },
                                'The element is an ',
                                React.createElement(
                                    'b',
                                    null,
                                    'output'
                                ),
                                ' from the selected one.'
                            ),
                            React.createElement('div', { className: 'circle inputoutput help-clearer left-floater' }),
                            React.createElement(
                                'div',
                                { className: 'circle-description left-floater' },
                                'The element is both an ',
                                React.createElement(
                                    'b',
                                    null,
                                    'input and an output'
                                ),
                                ' to/from the selected one.'
                            ),
                            React.createElement('div', { className: 'help-spacer help-clearer' }),
                            React.createElement(
                                'h4',
                                null,
                                'Colour coding for experiment status lifecycle'
                            ),
                            React.createElement('div', { className: 'circle design-status help-clearer left-floater' }),
                            React.createElement(
                                'div',
                                { className: 'circle-description left-floater' },
                                'The experiment is in ',
                                React.createElement(
                                    'b',
                                    null,
                                    'design'
                                ),
                                ' phase. If available in the model, parameters can be set and state variables can be set to be recorded before running the experiment.'
                            ),
                            React.createElement('div', { className: 'circle queued-status help-clearer left-floater' }),
                            React.createElement(
                                'div',
                                { className: 'circle-description left-floater' },
                                'The experiment is ',
                                React.createElement(
                                    'b',
                                    null,
                                    'queued'
                                ),
                                ' for running on the configured server.'
                            ),
                            React.createElement('div', { className: 'circle running-status help-clearer left-floater' }),
                            React.createElement(
                                'div',
                                { className: 'circle-description left-floater' },
                                'The experiment is currently ',
                                React.createElement(
                                    'b',
                                    null,
                                    'running'
                                ),
                                ' on the designated server.'
                            ),
                            React.createElement('div', { className: 'circle completed-status help-clearer left-floater' }),
                            React.createElement(
                                'div',
                                { className: 'circle-description left-floater' },
                                'The experiment has successfully ',
                                React.createElement(
                                    'b',
                                    null,
                                    'completed'
                                ),
                                ' running. Simulation results (state variables that were recorded, if any) can now be visualized/plotted.'
                            ),
                            React.createElement('div', { className: 'circle error-status help-clearer left-floater' }),
                            React.createElement(
                                'div',
                                { className: 'circle-description left-floater' },
                                'Bad news! The experiment caused an ',
                                React.createElement(
                                    'b',
                                    null,
                                    'error'
                                ),
                                ' while running on the server.'
                            )
                        ),
                        React.createElement(
                            'div',
                            { className: 'modal-footer' },
                            React.createElement(
                                'button',
                                { type: 'button', className: 'btn', 'data-dismiss': 'modal' },
                                'Close'
                            )
                        )
                    )
                )
            );
        }
    });
}.call(exports, __webpack_require__, exports, module),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ 3818:
/***/ (function(module, exports, __webpack_require__) {

// style-loader: Adds some css to the DOM by adding a <style> tag

// load the styles
var content = __webpack_require__(3819);
if(typeof content === 'string') content = [[module.i, content, '']];
// add the styles to the DOM
var update = __webpack_require__(18)(content, {});
if(content.locals) module.exports = content.locals;
// Hot Module Replacement
if(false) {
	// When the styles change, update the <style> tags
	if(!content.locals) {
		module.hot.accept("!!../../../../node_modules/css-loader/index.js!../../../../node_modules/less-loader/dist/cjs.js?{\"modifyVars\":{\"url\":\"'../../../extensions/geppetto-netpyne/css/colors'\"}}!./HelpModal.less", function() {
			var newContent = require("!!../../../../node_modules/css-loader/index.js!../../../../node_modules/less-loader/dist/cjs.js?{\"modifyVars\":{\"url\":\"'../../../extensions/geppetto-netpyne/css/colors'\"}}!./HelpModal.less");
			if(typeof newContent === 'string') newContent = [[module.id, newContent, '']];
			update(newContent);
		});
	}
	// When the module is disposed, remove the <style> tags
	module.hot.dispose(function() { update(); });
}

/***/ }),

/***/ 3819:
/***/ (function(module, exports, __webpack_require__) {

exports = module.exports = __webpack_require__(17)(undefined);
// imports


// module
exports.push([module.i, ".modal {\n  z-index: 9999999;\n}\n.modal input {\n  font-weight: 200;\n}\n.modal .modal-content {\n  background: rgba(255, 255, 255, 0.8);\n  border-radius: 0px!important;\n  color: #f23d7a;\n}\n.modal .modal-header {\n  border: 0;\n  padding: 10px;\n}\n.modal .modal-body {\n  border: 0;\n  max-height: 50%;\n}\n.modal .modal-footer {\n  border: 0;\n  padding: 10px;\n}\n.dark-orange {\n  color: #cc215a;\n}\n.orange {\n  color: #f23d7a;\n}\n.orange-color {\n  color: #f23d7a;\n}\n.orange-color-bg {\n  background-color: #f23d7a;\n}\n#help-modal {\n  top: 10%;\n  font-family: 'Helvetica Neue';\n  font-weight: 200;\n}\n#help-modal h4 {\n  color: #f23d7a;\n}\n#help-modal p {\n  color: white;\n}\n#help-modal .circle {\n  border-radius: 50%;\n  width: 20px;\n  height: 20px;\n  clear: both;\n  float: left;\n  margin-bottom: 10px;\n}\n#help-modal .default {\n  background-color: #0199e8;\n}\n#help-modal .selected {\n  background-color: #ffcc00;\n}\n#help-modal .input {\n  background-color: #ffdfc6;\n}\n#help-modal .output {\n  background-color: #ff5a02;\n}\n#help-modal .inputoutput {\n  background-color: #649615;\n}\n#help-modal .queued-status {\n  background-color: #0199e8;\n}\n#help-modal .running-status {\n  background-color: #ffcc00;\n}\n#help-modal .design-status {\n  background-color: #ff5a02;\n}\n#help-modal .completed-status {\n  background-color: #649615;\n}\n#help-modal .error-status {\n  background-color: red;\n}\n#help-modal h4.modal-title {\n  text-align: center;\n}\n#help-modal .modal-body {\n  overflow-y: auto;\n}\n#help-modal .btn,\n#help-modal .label {\n  margin-left: 3px;\n  margin-right: 3px;\n}\n#help-modal .icon-question-sign {\n  margin-left: 5px;\n  font-size: 20px;\n}\n#help-modal .left-floater {\n  float: left;\n}\n#help-modal .help-spacer {\n  height: 15px;\n}\n#help-modal .help-small-spacer {\n  height: 7.5px;\n}\n#help-modal .help-clearer {\n  clear: both;\n}\n#help-modal .circle-description {\n  margin-left: 20px;\n  margin-top: 2px;\n  max-width: 500px;\n  color: white;\n}\n#help-modal div.circle-description b {\n  color: #f23d7a;\n}\n", ""]);

// exports


/***/ }),

/***/ 3820:
/***/ (function(module, exports, __webpack_require__) {

// style-loader: Adds some css to the DOM by adding a <style> tag

// load the styles
var content = __webpack_require__(3821);
if(typeof content === 'string') content = [[module.i, content, '']];
// add the styles to the DOM
var update = __webpack_require__(18)(content, {});
if(content.locals) module.exports = content.locals;
// Hot Module Replacement
if(false) {
	// When the styles change, update the <style> tags
	if(!content.locals) {
		module.hot.accept("!!../../../../node_modules/css-loader/index.js!../../../../node_modules/less-loader/dist/cjs.js?{\"modifyVars\":{\"url\":\"'../../../extensions/geppetto-netpyne/css/colors'\"}}!./SimulationControls.less", function() {
			var newContent = require("!!../../../../node_modules/css-loader/index.js!../../../../node_modules/less-loader/dist/cjs.js?{\"modifyVars\":{\"url\":\"'../../../extensions/geppetto-netpyne/css/colors'\"}}!./SimulationControls.less");
			if(typeof newContent === 'string') newContent = [[module.id, newContent, '']];
			update(newContent);
		});
	}
	// When the module is disposed, remove the <style> tags
	module.hot.dispose(function() { update(); });
}

/***/ }),

/***/ 3821:
/***/ (function(module, exports, __webpack_require__) {

exports = module.exports = __webpack_require__(17)(undefined);
// imports


// module
exports.push([module.i, ".dark-orange {\n  color: #cc215a;\n}\n.orange {\n  color: #f23d7a;\n}\n.orange-color {\n  color: #f23d7a;\n}\n.orange-color-bg {\n  background-color: #f23d7a;\n}\n#sim-toolbar {\n  position: fixed;\n  right: 5px;\n  top: 5px;\n  margin-right: 0;\n}\n.simulation-controls button {\n  margin: 0px 3px;\n  border: none;\n  height: 27px;\n}\n.SaveButton {\n  position: fixed;\n  top: 5px;\n  right: 539px;\n  height: 27px;\n}\n.SaveButton:disabled {\n  background: 0;\n  color: #f23d7a;\n}\n.tooltip-persist {\n  height: 25px;\n  max-width: 800px;\n  border-radius: 5px;\n  border: 1px solid black;\n  padding: 2px 4px 2px 4px;\n  background: white;\n  opacity: 1;\n  left: 200px;\n}\n.HomeButton {\n  position: fixed;\n  top: 5px;\n  right: 496px;\n  height: 27px;\n}\n.menuBtnListItemDisabled {\n  color: grey !important;\n  pointer-events: none;\n}\n", ""]);

// exports


/***/ })

});
//# sourceMappingURL=4.bundle.js.map