webpackJsonp([36],{

/***/ 1414:
/***/ (function(module, exports, __webpack_require__) {

// style-loader: Adds some css to the DOM by adding a <style> tag

// load the styles
var content = __webpack_require__(1415);
if(typeof content === 'string') content = [[module.i, content, '']];
// add the styles to the DOM
var update = __webpack_require__(18)(content, {});
if(content.locals) module.exports = content.locals;
// Hot Module Replacement
if(false) {
	// When the styles change, update the <style> tags
	if(!content.locals) {
		module.hot.accept("!!../../../../node_modules/css-loader/index.js!../../../../node_modules/less-loader/dist/cjs.js?{\"modifyVars\":{\"url\":\"'../../../extensions/geppetto-netpyne/css/colors'\"}}!./ExperimentsTable.less", function() {
			var newContent = require("!!../../../../node_modules/css-loader/index.js!../../../../node_modules/less-loader/dist/cjs.js?{\"modifyVars\":{\"url\":\"'../../../extensions/geppetto-netpyne/css/colors'\"}}!./ExperimentsTable.less");
			if(typeof newContent === 'string') newContent = [[module.id, newContent, '']];
			update(newContent);
		});
	}
	// When the module is disposed, remove the <style> tags
	module.hot.dispose(function() { update(); });
}

/***/ }),

/***/ 1415:
/***/ (function(module, exports, __webpack_require__) {

exports = module.exports = __webpack_require__(17)(undefined);
// imports


// module
exports.push([module.i, ".dark-orange {\n  color: #cc215a;\n}\n.orange {\n  color: #f23d7a;\n}\n.orange-color {\n  color: #f23d7a;\n}\n.orange-color-bg {\n  background-color: #f23d7a;\n}\n#experimentsButton {\n  margin: 0 auto;\n  margin-bottom: 26px;\n  position: relative;\n  border-width: 1px;\n  border-bottom: 0;\n  border-left: 0;\n  border-style: solid;\n  cursor: pointer!important;\n  box-shadow: none;\n  text-shadow: none;\n  width: 140px;\n  height: 35px;\n  z-index: 3;\n}\n#experimentsButton > a::-moz-focus-inner {\n  border: 0;\n}\n.experimentsResults {\n  background: transparent;\n  color: #ccc;\n  width: 100%;\n  max-height: 90%;\n  height: 87%;\n  border: 0;\n  padding: 0!important;\n  padding-top: 2px!important;\n}\n.experimentsResultsOutput {\n  background: transparent;\n  color: #ccc;\n  height: 100%;\n  width: 100%;\n  max-height: 100%;\n  border: 0;\n  padding: 0!important;\n  padding-top: 2px!important;\n  overflow-y: auto;\n}\n#experiments {\n  background: rgba(255, 255, 255, 0.8) !important;\n  color: #ccc;\n  height: 250px;\n  width: 100%;\n  max-height: 100%;\n  padding: 0px;\n  border: 0;\n  top: 0px;\n  z-index: 1;\n  margin-bottom: 0px;\n  cursor: pointer;\n  border-radius: 0;\n}\n#experiments th {\n  cursor: default;\n}\n.experimentsTable {\n  font-weight: 100;\n}\n.expandableTable {\n  margin-bottom: 7px;\n  width: 100%;\n}\n.expandableTable td {\n  border: 0;\n}\n.expandableTable th {\n  border: 0;\n  font-weight: 200!important;\n}\n.configurationTD {\n  width: 300px;\n}\n.configurationTDLink {\n  width: 300px;\n  color: #f23d7a;\n  cursor: pointer;\n}\n.configurationTDLink:hover {\n  color: #cc215a;\n}\n#experimentsTable td {\n  border: 0;\n  padding-bottom: 0px;\n}\n#experimentsTable th {\n  border: 0;\n  color: #f23d7a;\n  font-weight: 200!important;\n}\n.nthTr {\n  background: #1c1d1f82;\n}\n.experimentsTableColumn {\n  color: white;\n}\n#experimentsButton .glyphicon {\n  font-size: 50px;\n}\n.activeExpLabel {\n  color: #30BDBD;\n  font-weight: 200;\n  font-size: 15px;\n  text-align: right;\n  text-transform: capitalize;\n  position: absolute;\n  right: 500px;\n  top: 3px;\n  width: 350px;\n  display: none;\n}\n.activeExperiment {\n  background-color: #1c1d1f  !important;\n}\n.newExperimentFocus {\n  background: lightslategrey !important;\n}\n.white {\n  color: white;\n}\n.circle {\n  position: relative;\n  width: 16px;\n  height: 16px;\n  border-radius: 50%;\n  background: #f23d7a;\n  margin-top: 2px;\n}\n.QUEUED {\n  background: #0CB0DA;\n}\n.RUNNING {\n  background: #ffd800;\n}\n.ERROR {\n  background: red;\n}\n.COMPLETED {\n  background: #7EC113;\n}\n.iconsDiv {\n  display: none;\n  float: right;\n  padding-right: 12px;\n}\n.visible {\n  display: block;\n}\n.iconsDiv > a > i:hover {\n  color: white;\n}\n.iconsDiv > a > i {\n  padding-right: 10px;\n  padding-top: 5px;\n  color: #FF6700;\n  padding-left: 10px;\n  margin-bottom: -3px;\n  cursor: pointer;\n}\n#deleteRow {\n  float: right;\n  padding-right: 20px;\n  color: #FF6700;\n  padding-left: 10px;\n}\n#deleteRow:hover {\n  color: white;\n}\n.new_experiment_icon {\n  margin-top: -3px;\n}\n.new_experiment {\n  width: 40px;\n  cursor: pointer;\n  position: absolute;\n  right: 0px;\n  top: 5px;\n  height: 22px;\n  padding-top: 8px;\n  text-decoration: none!important;\n}\n.new_experiment:hover {\n  color: white;\n}\n.new_experiment > i {\n  padding-right: 10px;\n}\n.collapse {\n  display: none;\n}\n.extend {\n  display: block;\n}\n.statusHeader {\n  text-align: center;\n  width: 10%;\n}\n.tableHeader {\n  width: 30%;\n}\n.nameHeader {\n  width: 215px;\n}\n.activeIcon > i {\n  padding-right: 10px;\n}\n.enabled {\n  display: inline;\n}\n.tooltip-container-status {\n  height: 25px;\n  max-width: 800px;\n  border-radius: 5px;\n  border: 1px solid black;\n  padding: 2px 4px 2px 4px;\n  background: white;\n  opacity: 1;\n}\n.listVariables {\n  padding-bottom: 5px;\n}\n", ""]);

// exports


/***/ }),

/***/ 655:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_RESULT__;/**
 * React component for displaying a Project's experiments in a table.
 *
 * @author Jesus R. Martinez (jesus@metacell.us)
 */
!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require) {

    var React = __webpack_require__(1),
        $ = __webpack_require__(16);
    var GEPPETTO = __webpack_require__(71);

    __webpack_require__(1414);

    $.widget.bridge('uitooltip', $.ui.tooltip);

    /**
     * Creates a table row html element <tr>, used to display an Experiment's
     * information (name, lastModified) and controls.
     */
    var ExperimentRow = React.createClass({
        displayName: 'ExperimentRow',


        getDefaultProps: function getDefaultProps() {
            return {
                suppressContentEditableWarning: true
            };
        },

        updateIcons: function updateIcons(activeIconVisibility, visible) {
            this.refs.icons.updateIconsState(activeIconVisibility, visible);
        },

        //Requests element with control icons to become visible
        mouseOver: function mouseOver() {
            this.refs.icons.show();
        },

        //Requests element with control icons to become invisible
        mouseOut: function mouseOut() {
            this.refs.icons.hide();
        },

        componentDidMount: function componentDidMount() {
            var row = "#" + this.props.experiment.getId();
            var that = this;

            $(row).parent().find("td[contenteditable='true']").keydown(function (e) {
                if (e.keyCode == 13) {
                    e.preventDefault();
                    $(this).blur();

                    // without this somehow the carriage return makes it into the field
                    window.getSelection().removeAllRanges();
                }
            });

            // Handle edits to editable name field
            $(row).find("td[contenteditable='true']").blur(function (e) {
                //save if user hits enter key
                // get experiment ID for the edited field
                var val = $(this).html();
                var field = $(this).attr("name");

                //remove empty spaces
                val = val.replace(/&nbsp;/g, '').replace(/<br>/g, '').replace(/<br\/>/g, '').trim();

                var setterStr = "setName";

                if (field == "name") {
                    var expID = $(this).parent().attr("id").replace('#', '');
                    GEPPETTO.CommandController.execute("Project.getExperimentById(" + expID + ")." + setterStr + "('" + val + "')", true);
                }
            });
        },

        render: function render() {
            var rowNumber = this.props.rowNumber;
            var rowClasses = "experimentsTableColumn accordion-toggle row-" + this.props.experiment.getId();

            //add different background to every even row
            if (rowNumber % 2 == 1) {
                rowClasses += " nthTr";
            }

            return React.createElement(
                'tr',
                { 'data-rowType': 'main', onClick: this.props.fnClick, onMouseOver: this.mouseOver, onMouseOut: this.mouseOut,
                    className: rowClasses, id: this.props.experiment.getId() },
                React.createElement(StatusElement, { experiment: this.props.experiment, key: this.props.experiment.name + "-statusElement" }),
                React.createElement(
                    'td',
                    { className: 'configurationTD', name: 'name', contentEditable: this.props.editable, suppressContentEditableWarning: true },
                    this.props.experiment.getName()
                ),
                React.createElement(
                    'td',
                    null,
                    this.props.experiment.getLastModified()
                ),
                React.createElement(
                    'td',
                    null,
                    React.createElement(IconsElement, { ref: 'icons', experiment: this.props.experiment, key: this.props.experiment.name + "-iconsRow" })
                )
            );
        }
    });

    /**
     * Creates a table row html element, <tr>, which can be collapsed.
     * Used to display an experiment's simulator configurations
     */
    var ExperimentExpandableRow = React.createClass({
        displayName: 'ExperimentExpandableRow',

        render: function render() {
            var id = "collapsable-" + this.props.experiment.getId();
            var rowNumber = this.props.rowNumber;
            var rowClasses = "nested-experiment-info";

            //add different background to every even row
            if (rowNumber % 2 == 1) {
                rowClasses += " nthTr";
            }
            var rows = [];
            var simulatorConfigurations = [];
            var index = 0;

            //make simulator configurations to array
            for (var key in this.props.experiment.simulatorConfigurations) {
                simulatorConfigurations[index] = this.props.experiment.simulatorConfigurations[key];
                index++;
            }

            //create array of table row elements of type SimulatorRow
            simulatorConfigurations.forEach(function (simulator) {
                if (simulator != null) {
                    var index = 1;
                    rows.push(React.createElement(SimulatorRow, { simulator: simulator, experiment: this.props.experiment,
                        editable: this.props.editable, key: "simulatorRow" + index + "-" + simulator.aspectInstancePath }));
                    index++;
                }
            }.bind(this));

            var collapseClass = "collapse accordian-body collapsable-" + this.props.experiment.getId();

            return React.createElement(
                'tr',
                { className: rowClasses, id: id },
                React.createElement(
                    'td',
                    { colSpan: '12', className: 'hiddenRow' },
                    React.createElement(
                        'div',
                        { className: collapseClass },
                        React.createElement(
                            'table',
                            { className: 'table-condensed expandableTable' },
                            React.createElement(
                                'thead',
                                { className: 'experimentsTableColumn' },
                                React.createElement(
                                    'tr',
                                    null,
                                    React.createElement('th', { className: 'nameHeader' }),
                                    React.createElement(
                                        'th',
                                        null,
                                        'Aspect'
                                    ),
                                    React.createElement(
                                        'th',
                                        null,
                                        'Simulator'
                                    ),
                                    React.createElement(
                                        'th',
                                        null,
                                        'Recorded variables'
                                    ),
                                    React.createElement(
                                        'th',
                                        null,
                                        'Set parameters'
                                    ),
                                    React.createElement(
                                        'th',
                                        null,
                                        'Timestep (s)'
                                    ),
                                    React.createElement(
                                        'th',
                                        null,
                                        'Length (s)'
                                    )
                                )
                            ),
                            React.createElement(
                                'tbody',
                                null,
                                rows
                            )
                        )
                    )
                )
            );
        }
    });

    /**
     * Creates table row for displaying an experiment's simulator configurations
     */
    var SimulatorRow = React.createClass({
        displayName: 'SimulatorRow',

        refresh: function refresh() {
            if (window.Project.getActiveExperiment()) {
                if (this.props.experiment.getId() == window.Project.getActiveExperiment().getId()) {
                    this.forceUpdate();
                }
            } else {
                this.forceUpdate();
            }
        },

        componentWillUnmount: function componentWillUnmount() {
            GEPPETTO.off(GEPPETTO.Events.Experiment_updated, this.refresh, this);
        },

        componentDidMount: function componentDidMount() {
            var row = "#simulatorRowId-" + this.props.experiment.getId();

            GEPPETTO.on(GEPPETTO.Events.Experiment_updated, this.refresh, this);

            // Handle edits to editable fields
            $(row).parent().find("td[contenteditable='true']").keydown(function (e) {
                if (e.keyCode == 13) {
                    e.preventDefault();
                    $(this).blur();

                    // without this somehow the carriage return makes it into the field
                    window.getSelection().removeAllRanges();
                }
            });

            $(row).parent().find("td[contenteditable='true']").blur(function (e) {
                // get experiment ID for the edited field
                var val = $(this).html();
                var field = $(this).attr("name");

                //remove empty spaces
                val = val.replace(/&nbsp;/g, '').replace(/<br>/g, '').replace(/<br\/>/g, '').trim();

                var setterStr = "";

                switch (field) {
                    case "simulatorId":
                        setterStr = "setSimulator";
                        break;
                    case "timeStep":
                        setterStr = "setTimeStep";
                        break;
                    case "length":
                        setterStr = "setLength";
                        break;
                    case "conversionId":
                        setterStr = "setConversionService";
                        break;
                    default:
                        break;
                }

                if (setterStr != "") {
                    var expID = $(this).parents().closest("tr.nested-experiment-info").attr("id").replace('collapsable-', '');

                    // get aspect instance path
                    var aspect = $(this).parent().find("td[name='aspect']").html();
                    GEPPETTO.CommandController.execute("Project.getExperimentById(" + expID + ").simulatorConfigurations['" + aspect + "']." + setterStr + "('" + val + "')", true);
                }
            });
        },

        watchedVariablesWindow: function watchedVariablesWindow() {
            if (this.props.experiment.getWatchedVariables() != null || undefined) {
                var watchedVariables = "<ul class='listVariables'>";

                for (var i = 0; i < this.props.experiment.getWatchedVariables().length; i++) {
                    watchedVariables = watchedVariables + '<li>' + this.props.experiment.getWatchedVariables()[i] + '</li>';
                }

                watchedVariables += "</ul>";

                GEPPETTO.ModalFactory.infoDialog("Recorded variables ", watchedVariables);
            }
        },

        parametersWindow: function parametersWindow() {
            var modifiedParameters = "<ul class='listVariables'>";
            var parameters = this.props.experiment.getSetParameters();

            for (var key in parameters) {
                if (parameters.hasOwnProperty(key)) {
                    modifiedParameters += '<li>' + key + "=" + parameters[key] + '</li>';
                }
            }

            modifiedParameters += "</ul>";
            GEPPETTO.ModalFactory.infoDialog("Set Parameters ", modifiedParameters);
        },

        render: function render() {
            var editable = false;

            var writePermission = GEPPETTO.UserController.hasPermission(GEPPETTO.Resources.WRITE_PROJECT);
            var projectPersisted = this.props.experiment.getParent().persisted;
            var readOnly = window.Project.isReadOnly();

            if (!writePermission || !projectPersisted || readOnly || !(GEPPETTO.UserController.isLoggedIn() && GEPPETTO.UserController.hasPersistence())) {
                editable = false;
            } else {
                if (this.props.experiment.getStatus() == GEPPETTO.Resources.ExperimentStatus.DESIGN || this.props.experiment.getStatus() == GEPPETTO.Resources.ExperimentStatus.ERROR) {
                    editable = true;
                }
            }

            var watchedVariables = this.props.experiment.getWatchedVariables();
            var watchedVariablesClick = null;
            var variablesMessage = "None";
            if (watchedVariables.length > 0) {
                variablesMessage = watchedVariables.length + " variables recorded";
                watchedVariablesClick = this.watchedVariablesWindow;
            }

            var parameterMessage = "None";
            var parametersClick = null;
            var modifiedParameters = Object.keys(this.props.experiment.getSetParameters()).length;

            if (modifiedParameters > 0) {
                parameterMessage = modifiedParameters + " parameters set";
                parametersClick = this.parametersWindow;
            }

            var simulatorRowId = "simulatorRowId-" + this.props.experiment.getId();
            return React.createElement(
                'tr',
                { id: simulatorRowId },
                React.createElement('td', null),
                React.createElement(
                    'td',
                    { className: 'configurationTD', name: 'aspect' },
                    this.props.simulator["aspectInstancePath"]
                ),
                React.createElement(
                    'td',
                    { className: 'configurationTD', name: 'simulatorId', contentEditable: editable, suppressContentEditableWarning: true },
                    this.props.simulator["simulatorId"]
                ),
                React.createElement(
                    'td',
                    { className: 'configurationTDLink', name: 'variables', onClick: watchedVariablesClick },
                    variablesMessage
                ),
                React.createElement(
                    'td',
                    { className: 'configurationTDLink', name: 'parameters', onClick: parametersClick },
                    parameterMessage
                ),
                React.createElement(
                    'td',
                    { className: 'configurationTD', name: 'timeStep', contentEditable: editable, suppressContentEditableWarning: true },
                    this.props.simulator["timeStep"]
                ),
                React.createElement(
                    'td',
                    { className: 'configurationTD', name: 'length', contentEditable: editable, suppressContentEditableWarning: true },
                    this.props.simulator["length"]
                )
            );
        }
    });

    /**
     * Creates <td> element to display the status of an experiment
     */
    var StatusElement = React.createClass({
        displayName: 'StatusElement',

        attachTooltip: function attachTooltip() {
            $('div.circle[rel="tooltip"]').uitooltip({
                position: { my: "left+15 center", at: "right center" },
                tooltipClass: "tooltip-container-status",
                show: {
                    effect: "slide",
                    direction: "left",
                    delay: 200
                },
                hide: {
                    effect: "slide",
                    direction: "left",
                    delay: 200
                },
                content: function content() {
                    return $(this).attr("data-custom-title");
                },
                relative: true
            });
        },

        componentDidMount: function componentDidMount() {
            this.attachTooltip();
        },

        clickStatus: function clickStatus(e) {
            if (this.props.experiment.getStatus() == GEPPETTO.Resources.ExperimentStatus.ERROR || this.props.experiment.getStatus() == GEPPETTO.Resources.ExperimentStatus.DESIGN) {
                var error = this.props.experiment.getDetails();
                if (error != null || undefined) {
                    e.stopPropagation();
                    e.nativeEvent.stopImmediatePropagation();
                    GEPPETTO.ModalFactory.infoDialog("Experiment Failed ", error.exception);
                }
            }
        },

        render: function render() {
            var experiment = this.props.experiment;

            // IMPORTANT NOTE: empty title tag in the markup below is needed or the tooltip stops working
            var tdStatus = React.createElement(
                'td',
                { className: 'statusIcon' },
                React.createElement('div', { className: "circle center-block " + experiment.getStatus(),
                    'data-status': experiment.getStatus(),
                    title: '', onClick: this.clickStatus,
                    'data-custom-title': GEPPETTO.Resources.ExperimentStatus.Descriptions[experiment.getStatus()],
                    rel: 'tooltip' })
            );

            return tdStatus;
        }
    });

    /**
     * Creates html element holding set of icons used for experiment controls within table
     */
    var IconsElement = React.createClass({
        displayName: 'IconsElement',

        getInitialState: function getInitialState() {
            return {
                rowVisible: false,
                cloneIconVisible: true,
                deleteIconVisible: true,
                activeIconVisible: true
            };
        },

        show: function show() {
            this.setState({ rowVisible: true });
        },

        hide: function hide() {
            this.setState({ rowVisible: false });
        },

        activeExperiment: function activeExperiment(e) {
            var experiment = this.props.experiment;
            var index = window.Project.getExperiments().indexOf(experiment);
            GEPPETTO.CommandController.execute("Project.getExperiments()[" + index + "].setActive();", true);
            e.stopPropagation();
            e.nativeEvent.stopImmediatePropagation();

            var login = GEPPETTO.UserController.isLoggedIn();
            if (login) {
                GEPPETTO.trigger(GEPPETTO.Events.Show_spinner, GEPPETTO.Resources.LOADING_EXPERIMENT);
            } else {
                GEPPETTO.ModalFactory.infoDialog(GEPPETTO.Resources.ERROR, GEPPETTO.Resources.OPERATION_NOT_SUPPORTED + GEPPETTO.Resources.USER_NOT_LOGIN);
            }
        },

        deleteExperiment: function deleteExperiment(e) {
            var experiment = this.props.experiment;
            var index = window.Project.getExperiments().indexOf(experiment);
            GEPPETTO.ModalFactory.inputDialog("Are you sure?", "Delete " + experiment.name + "?", "Yes", function () {
                GEPPETTO.CommandController.execute("Project.getExperiments()[" + index + "].deleteExperiment();", true);
            }, "Cancel", function () {});
            e.stopPropagation();
            e.nativeEvent.stopImmediatePropagation();
        },

        cloneExperiment: function cloneExperiment(e) {
            var experiment = this.props.experiment;
            var index = window.Project.getExperiments().indexOf(experiment);
            GEPPETTO.CommandController.execute("Project.getExperiments()[" + index + "].clone();", true);
            e.stopPropagation();
            e.nativeEvent.stopImmediatePropagation();
        },
        downloadModels: function downloadModels(e) {
            var experiment = this.props.experiment;

            var simulatorConfigurations = experiment.simulatorConfigurations;
            for (var config in simulatorConfigurations) {
                var simulatorConfig = simulatorConfigurations[config];
                GEPPETTO.CommandController.execute('Project.downloadModel("' + simulatorConfig["aspectInstancePath"] + '");', true);
            }
            e.stopPropagation();
            e.nativeEvent.stopImmediatePropagation();
        },

        downloadResults: function downloadResults(e) {
            var experiment = this.props.experiment;
            var index = window.Project.getExperiments().indexOf(experiment);
            var simulatorConfigurations = experiment.simulatorConfigurations;
            for (var config in simulatorConfigurations) {
                var simulatorConfig = simulatorConfigurations[config];
                GEPPETTO.CommandController.execute("Project.getExperiments()[" + index + "].downloadResults('" + simulatorConfig["aspectInstancePath"] + "'," + "'RAW');", true);
            }
            e.stopPropagation();
            e.nativeEvent.stopImmediatePropagation();
        },

        updateIconsState: function updateIconsState(activeIconVisibility, visible) {
            this.setState({ activeIconVisible: activeIconVisibility, deleteIconVisible: visible, cloneIconVisible: visible });
        },

        componentDidMount: function componentDidMount() {
            //hide download icons 
            $(".downloadModelsIcon").hide();
            $(".downloadResultsIcon").hide();
        },

        render: function render() {
            //Create IDs for icons
            var activeIconId = "activeIcon-" + this.props.experiment.getId();
            var deleteIconId = "deleteIcon-" + this.props.experiment.getId();
            var downloadResultsIconId = "downloadResultsIcon-" + this.props.experiment.getId();
            var downloadModelsIconId = "downloadModelsIcon-" + this.props.experiment.getId();
            var cloneIconId = "cloneIcon-" + this.props.experiment.getId();

            return React.createElement(
                'div',
                { className: (this.state.rowVisible ? "visible " : "") + 'iconsDiv' },
                React.createElement(
                    'a',
                    { className: (this.state.activeIconVisible ? "enabled " : "hide ") + 'activeIcon', onClick: this.activeExperiment,
                        'data-experimentId': this.props.experiment.getId(), id: activeIconId },
                    React.createElement('i', { className: 'fa fa-check-circle fa-lg', rel: 'tooltip', title: 'Activate experiment' })
                ),
                React.createElement(
                    'a',
                    { className: (this.state.deleteIconVisible ? "enabled " : "hide ") + 'deleteIcon', onClick: this.deleteExperiment,
                        'data-experimentId': this.props.experiment.getId(), id: deleteIconId },
                    React.createElement('i', { className: 'fa fa-remove fa-lg', rel: 'tooltip', title: 'Delete Experiment' })
                ),
                React.createElement(
                    'a',
                    { className: 'downloadResultsIcon', onClick: this.downloadResults, 'data-experimentId': this.props.experiment.getId(), id: downloadResultsIconId },
                    React.createElement('i', { className: 'fa fa-download fa-lg', rel: 'tooltip', title: 'Download Results' })
                ),
                React.createElement(
                    'a',
                    { className: 'downloadModelsIcon', onClick: this.downloadModels, 'data-experimentId': this.props.experiment.getId(), id: downloadModelsIconId },
                    React.createElement('i', { className: 'fa fa-cloud-download fa-lg', rel: 'tooltip', title: 'Download Models' })
                ),
                React.createElement(
                    'a',
                    { className: (this.state.cloneIconVisible ? "enabled " : "hide ") + 'cloneIcon', onClick: this.cloneExperiment,
                        'data-experimentId': this.props.experiment.getId(), id: cloneIconId },
                    React.createElement('i', { className: 'fa fa-clone fa-lg', rel: 'tooltip', title: 'Clone Experiment' })
                )
            );
        }
    });

    /**
     * Creates a table html component used to dipslay the experiments
     */
    var ExperimentsTable = React.createClass({
        displayName: 'ExperimentsTable',

        componentDidMount: function componentDidMount() {
            var self = this;
            // Handles new experiment button click
            $("#new_experiment").click(function () {
                //retrieve last created experiment and used it to clone new one
                var experiments = window.Project.getExperiments();
                var experiment = window.Project.getActiveExperiment();
                if (experiments.length == 0) {
                    GEPPETTO.CommandController.execute("Project.newExperiment();", true);
                } else {
                    var index = 0;
                    if (experiment != null || undefined) {
                        for (var e in experiments) {
                            if (experiments[e].getId() > experiment.getId()) {
                                experiment = experiments[e];
                            }
                        }
                        index = window.Project.getExperiments().indexOf(experiment);
                    }
                    GEPPETTO.CommandController.execute("Project.getExperiments()[" + index + "].clone();", true);
                }
            });

            GEPPETTO.on(GEPPETTO.Events.Project_loaded, function () {
                self.populate();
                self.updateStatus();
            });

            GEPPETTO.on(GEPPETTO.Events.Project_persisted, function () {
                self.refresh();
            });

            GEPPETTO.on(GEPPETTO.Events.Experiment_status_check, function () {
                self.updateExperimentsTableStatus();
            });

            GEPPETTO.on(GEPPETTO.Events.Experiment_loaded, function () {
                self.updateExperimentStatus();
            });

            GEPPETTO.on(GEPPETTO.Events.Experiment_created, function (experiment) {
                self.newExperiment(experiment);
            });

            GEPPETTO.on(GEPPETTO.Events.Experiment_renamed, function (experiment) {
                self.refresh();
            });

            GEPPETTO.on(GEPPETTO.Events.Experiment_deleted, function (experiment) {
                self.deleteExperiment(experiment);
                if (!GEPPETTO.ExperimentsController.suppressDeleteExperimentConfirmation) {
                    GEPPETTO.ModalFactory.infoDialog(GEPPETTO.Resources.EXPERIMENT_DELETED, "Experiment " + experiment.name + " with id " + experiment.id + " was deleted successfully");
                }
            });

            $("#experiments").resizable({
                handles: 'n',
                minHeight: 100,
                autoHide: true,
                maxHeight: 400,
                resize: function (event, ui) {
                    if (ui.size.height > $("#footerHeader").height() * .75) {
                        $("#experiments").height($("#footerHeader").height() * .75);
                        event.preventDefault();
                    }
                    $('#experiments').resize();
                    $("#experiments").get(0).style.top = "0px";
                }.bind(this)
            });

            //As every other component this could be loaded after the project has been loaded so when we mount it we populate it with whatever is present
            if (window.Project != undefined) {
                this.populate();
                this.updateStatus();
            }

            $("#experimentsButton").show();
        },

        refresh: function refresh() {
            this.forceUpdate();
            this.updateExperimentStatus();
            this.updateStatus();
        },

        updateStatus: function updateStatus() {
            var visible = true;
            if (!GEPPETTO.UserController.hasPermission(GEPPETTO.Resources.WRITE_PROJECT) || !window.Project.persisted || !GEPPETTO.UserController.isLoggedIn() || window.Project.isReadOnly()) {
                visible = false;
            }

            this.setState({ newExperimentIconVisible: visible });
            for (var property in this.refs) {
                if (this.refs.hasOwnProperty(property)) {
                    this.refs[property].updateIcons(GEPPETTO.UserController.isLoggedIn(), visible);
                }
            }
        },

        newExperiment: function newExperiment(experiment) {
            var experiments = this.state.experiments;
            var rows = [];
            rows[0] = experiment;

            var index = 1;
            for (var key in experiments) {
                rows[index] = experiments[key];
                index++;
            }

            this.setState({ experiments: rows });
            this.state.counter++;
        },

        deleteExperiment: function deleteExperiment(experiment) {
            //this.state.experiments.pop(experiment);

            var experiments = this.state.experiments;
            var rows = [];

            var index = 0;
            for (var key in experiments) {
                if (experiment.getId() != experiments[key].getId()) {
                    rows[index] = experiments[key];
                    index++;
                }
            }

            this.state.counter--;

            this.setState({
                experiments: rows
            });

            // loop through each row of experiments table and remove
            $('#experimentsTable tbody tr').each(function () {
                // id of row that matches experiment to be deleted
                if (this.id == experiment.getId() || this.id == "collapsable-" + experiment.getId() || this.id == "#" + experiment.getId() || this.id == "#collapsable-" + experiment.getId()) {
                    $(this).remove();
                }
            });
        },

        updateExperimentStatus: function updateExperimentStatus() {
            var experiment = window.Project.getActiveExperiment();

            $(".activeIcon").show();
            // hide download icons for non active experiments
            $(".downloadModelsIcon").hide();
            $(".downloadResultsIcon").hide();

            if (experiment != null || undefined) {
                $("#activeIcon-" + experiment.getId()).hide();

                var downloadPermission = GEPPETTO.UserController.hasPermission(GEPPETTO.Resources.DOWNLOAD);

                if (downloadPermission) {
                    $("#downloadModelsIcon-" + experiment.getId()).show();
                    if (experiment.getStatus() == "COMPLETED") {
                        $("#downloadResultsIcon-" + experiment.getId()).show();
                    }
                }

                // loop through each row of experiments table
                $('#experimentsTable tbody tr').each(function () {
                    // id of row matches that of active experiment
                    if (this.id == experiment.getId() || this.id == "collapsable-" + experiment.getId()) {
                        // add class to make it clear it's active
                        $(this).addClass("activeExperiment");
                    } else {
                        // remove class from active experiment
                        $(this).removeClass("activeExperiment");
                    }
                });
            }
        },

        //Determines if an element inside the experiments table is in view
        isInView: function isInView(el) {
            // grab vanilla dom element from jquery element
            el = el[0];
            var rect = el.getBoundingClientRect(),
                top = rect.top,
                height = rect.height,
                el = el.parentNode;
            do {
                rect = el.getBoundingClientRect();
                if (top <= rect.bottom === false) return false;
                // Check if the element is out of view due to a container scrolling
                if (top + height <= rect.top) return false;
                el = el.parentNode;
            } while (el != document.body);
            // Check its within the document viewport
            return top <= document.documentElement.clientHeight;
        },

        /**
         * Update experiment status of those in table
         */
        updateExperimentsTableStatus: function updateExperimentsTableStatus() {
            var self = this;
            // loop through each row of experiments table
            $('#experimentsTable tbody tr').each(function () {
                var experiments = window.Project.getExperiments();
                var active = window.Project.getActiveExperiment();
                for (var e in experiments) {
                    var experiment = experiments[e];
                    if (this.id == "#" + experiment.getId() || this.id == experiment.getId()) {
                        var tdStatus = $(this).find(".circle");
                        var tdStatusId = tdStatus.attr("data-status");

                        if (tdStatusId != experiment.getStatus()) {
                            tdStatus.removeClass(tdStatusId);
                            tdStatus.addClass(experiment.getStatus());
                            tdStatus.attr("data-status", experiment.getStatus());
                            tdStatus.attr("data-custom-title", GEPPETTO.Resources.ExperimentStatus.Descriptions[experiment.getStatus()]);

                            if (self.isInView(tdStatus)) {
                                // make the tooltip pop-out for a bit to attract attention
                                tdStatus.mouseover().delay(2000).queue(function () {
                                    $(this).mouseout().dequeue();
                                });
                            }

                            if (experiment.getStatus() == GEPPETTO.Resources.ExperimentStatus.COMPLETED) {
                                if (active != null) {
                                    if (active.getId() == experiment.getId()) {
                                        var downloadPermission = GEPPETTO.UserController.hasPermission(GEPPETTO.Resources.DOWNLOAD);
                                        if (downloadPermission) {
                                            $("#downloadResultsIcon-" + experiment.getId()).show();
                                        }
                                    }
                                }
                                var editableFields = $(this).find(".configurationTD");
                                for (var i = 0; i < editableFields.length; i++) {
                                    if (editableFields[i].getAttribute("contentEditable") != "false") {
                                        var td = editableFields[i].setAttribute("contentEditable", false);
                                    }
                                }
                            }
                        }
                    }
                    if (this.id == "#simulatorRowId-" + experiment.getId() || this.id == "simulatorRowId-" + experiment.getId()) {
                        if (experiment.getStatus() == GEPPETTO.Resources.ExperimentStatus.COMPLETED) {
                            var editableFields = $(this).find(".configurationTD");
                            for (var i = 0; i < editableFields.length; i++) {
                                if (editableFields[i].getAttribute("contentEditable") != "false") {
                                    var td = editableFields[i].setAttribute("contentEditable", false);
                                }
                            }
                        }
                    }
                }
            });
        },

        populate: function populate() {
            var self = this;
            var experiments = window.Project.getExperiments();
            var rows = [];

            var index = 0;
            for (var key in experiments) {
                var experiment = experiments[key];
                rows[index] = experiment;
                index++;
            }

            self.state.counter = rows.length;

            self.setState({ experiments: rows });
        },

        getInitialState: function getInitialState() {
            var tabledata = [];
            return { experiments: tabledata, counter: 1, newExperimentIconVisible: true };
        },

        onClick: function onClick(rowID, e) {
            var targetRowId = "." + rowID;
            if ($(targetRowId).is(':visible')) {
                $(targetRowId).hide();
            } else {
                $(targetRowId).show();
            }
        },

        render: function render() {
            var rows = [];
            var rownumber = 1;
            this.state.experiments.forEach(function (experiment) {
                if (experiment != null) {
                    var editablePermissions = GEPPETTO.UserController.hasWritePermissions();
                    var editable = false;

                    if (!editablePermissions) {
                        editable = false;
                    } else {
                        if (experiment.getStatus() == GEPPETTO.Resources.ExperimentStatus.DESIGN || experiment.getStatus() == GEPPETTO.Resources.ExperimentStatus.ERROR) {
                            editable = true;
                        }
                    }

                    var expandableRowId = "collapsable-" + experiment.getId();
                    rows.push(React.createElement(ExperimentRow, { experiment: experiment, rowNumber: rownumber, editable: editable,
                        ref: expandableRowId, key: experiment.name + "-" + experiment.getId(), fnClick: this.onClick.bind(this, expandableRowId) }));
                    rows.push(React.createElement(ExperimentExpandableRow, { experiment: experiment, rowNumber: rownumber,
                        key: expandableRowId, editable: editable }));
                    rownumber++;
                }
            }.bind(this));

            return React.createElement(
                'div',
                { className: 'col-lg-6 experimentsResults panel-body experimentsResultsOutput', id: 'experimentsOutput' },
                React.createElement(
                    'table',
                    { id: 'experimentsTable', className: 'table table-condensed experimentsTable',
                        style: { borderCollapse: "collapse" } },
                    React.createElement(
                        'thead',
                        { className: 'experimentsTableColumn' },
                        React.createElement(
                            'tr',
                            null,
                            React.createElement(
                                'th',
                                { className: 'statusHeader' },
                                'Status'
                            ),
                            React.createElement(
                                'th',
                                { className: 'tableHeader' },
                                'Name'
                            ),
                            React.createElement(
                                'th',
                                { className: 'tableHeader' },
                                'Date'
                            ),
                            React.createElement(
                                'th',
                                { className: 'tableHeader' },
                                React.createElement(
                                    'div',
                                    { className: (this.state.newExperimentIconVisible ? "visible " : "hide ") + "new_experiment", id: 'new_experiment', title: 'New experiment' },
                                    React.createElement('i', { className: 'new_experiment_icon fa fa-plus fa-lg' })
                                )
                            )
                        )
                    ),
                    React.createElement(
                        'tbody',
                        null,
                        rows
                    )
                )
            );
        }
    });

    return ExperimentsTable;
}.call(exports, __webpack_require__, exports, module),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ })

});
//# sourceMappingURL=36.bundle.js.map