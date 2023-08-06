webpackJsonp([9],{

/***/ 2197:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_RESULT__;
/**
 * Controller class for popup widget. Use to make calls to widget from inside Geppetto.
 *
 * @author Jesus R Martinez (jesus@metacell.us)
 */
!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require) {

    var AWidgetController = __webpack_require__(804);

    /**
     * @exports Widgets/Popup/PopupsController
     */
    return AWidgetController.View.extend({

        initialize: function initialize(config) {
            this.widgets = Array();
            this.history = [];
            if (config != null || undefined) {
                this.buttonBarConfig = config.buttonBarConfiguration;
            }
        },

        /**
         * Creates popup widget
         */
        addWidget: function addWidget(isStateless) {
            if (isStateless == undefined) {
                isStateless = false;
            }
            var that = this;

            return new Promise(function (resolve) {
                __webpack_require__.e/* require.ensure */(22).then((function (require) {

                    var Popup = __webpack_require__(3350);
                    //look for a name and id for the new widget
                    var id = that.getAvailableWidgetId("Popup", that.widgets);
                    var name = id;

                    //create popup widget
                    var p = window[name] = new Popup({
                        id: id, name: name, visible: true, controller: that,
                        widgetType: GEPPETTO.Widgets.POPUP, stateless: isStateless
                    });
                    p.setController(that);
                    p.setSize(394, 490);
                    //create help command for plot
                    p.help = function () {
                        return GEPPETTO.CommandController.getObjectCommands(id);
                    };

                    //store in local stack
                    that.widgets.push(p);

                    GEPPETTO.WidgetsListener.subscribe(that, id);

                    //add commands to console autocomplete and help option
                    GEPPETTO.CommandController.updateHelpCommand(p, id, that.getFileComments("geppetto/js/components/widgets/popup/Popup.js"));

                    //update tags for autocompletion
                    GEPPETTO.CommandController.updateTags(p.getId(), p);

                    resolve(p);
                }).bind(null, __webpack_require__)).catch(__webpack_require__.oe);
            });
        },
        /**
         * Receives updates from widget listener class to update popup widget(s)
         *
         * @param {WIDGET_EVENT_TYPE} event - Event that tells widgets what to do
         */
        update: function update(event) {
            //delete popup widget(s)
            if (event == GEPPETTO.WidgetsListener.WIDGET_EVENT_TYPE.DELETE) {
                this.removeWidgets();
            }
        }
    });
}.call(exports, __webpack_require__, exports, module),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ 2198:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_RESULT__;
/**
 * Controller class for treevisualiser widget. Use to make calls to widget from
 * inside Geppetto.
 *
 * @module Widgets/TreeVisualizerControllerDAT
 *
 * @author Adrian Quintana (adrian.perez@ucl.ac.uk)
 */
!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require) {
    var AWidgetController = __webpack_require__(804);

    /**
     * @exports Widgets/Connectivity/TreeVisualiserControllerDATController
     */
    return AWidgetController.View.extend({

        initialize: function initialize() {
            this.widgets = [];
        },

        /**
         * Adds a new TreeVisualizerDAT Widget to Geppetto
         */
        addWidget: function addWidget(isStateless) {
            if (isStateless == undefined) {
                // stateless by default
                isStateless = true;
            }

            var that = this;

            return new Promise(function (resolve) {
                __webpack_require__.e/* require.ensure */(23).then((function (require) {

                    var TreeVisualiserDAT = __webpack_require__(3364);
                    //look for a name and id for the new widget
                    var id = that.getAvailableWidgetId("TreeVisualiserDAT", that.widgets);
                    var name = id;

                    // create tree visualiser widget
                    var tvdat = window[name] = new TreeVisualiserDAT({
                        id: id, name: name, visible: true, width: 260, height: 350,
                        widgetType: GEPPETTO.Widgets.TREEVISUALISERDAT, stateless: isStateless
                    });
                    // create help command for plot
                    tvdat.help = function () {
                        return GEPPETTO.CommandController.getObjectCommands(id);
                    };
                    // store in local stack
                    that.widgets.push(tvdat);

                    GEPPETTO.WidgetsListener.subscribe(that, id);

                    // updates helpc command output
                    GEPPETTO.CommandController.updateHelpCommand(tvdat, id, that.getFileComments("geppetto/js/components/widgets/treevisualiser/treevisualiserdat/TreeVisualiserDAT.js"));
                    //update tags for autocompletion
                    GEPPETTO.CommandController.updateTags(tvdat.getId(), tvdat);

                    resolve(tvdat);
                }).bind(null, __webpack_require__)).catch(__webpack_require__.oe);
            });
        },

        /**
         * Receives updates from widget listener class to update TreeVisualizerDAT widget(s)
         *
         * @param {WIDGET_EVENT_TYPE} event - Event that tells widgets what to do
         */
        update: function update(event, parameters) {
            var treeVisualisersDAT = this.getWidgets();
            // delete treevisualiser widget(s)
            if (event == GEPPETTO.WidgetsListener.WIDGET_EVENT_TYPE.DELETE) {
                this.removeWidgets();
            } else if (event == GEPPETTO.Events.Select) {
                //loop through all existing widgets
                for (var i = 0; i < this.widgets.length; i++) {
                    var treeVisualiserDAT = this.widgets[i];

                    if (_.find(treeVisualiserDAT.registeredEvents, function (el) {
                        return el.id === event;
                    })) {
                        var selected = GEPPETTO.SceneController.getSelection();
                        treeVisualiserDAT.reset();
                        //update treevisualiser with new data set
                        treeVisualiserDAT.setData(selected[0]);
                    }
                }
            }
            // update treevisualiser widgets
            else if (event == GEPPETTO.Events.Experiment_update) {
                    // loop through all existing widgets
                    for (var i = 0; i < treeVisualisersDAT.length; i++) {
                        var treeVisualiserDAT = treeVisualisersDAT[i];

                        // update treevisualiser with new data set
                        treeVisualiserDAT.updateData(parameters.step);
                    }
                }
                // update treevisualiser widgets
                else if (event == GEPPETTO.Events.ModelTree_populated || event == GEPPETTO.Events.SimulationTree_populated) {
                        // loop through all existing widgets
                        for (var i = 0; i < treeVisualisersDAT.length; i++) {
                            var treeVisualiserDAT = treeVisualisersDAT[i];

                            var ev = _.find(treeVisualiserDAT.registeredEvents, function (el) {
                                return el.id === event;
                            });
                            if (typeof ev !== 'undefined') {
                                if (typeof ev.callback === 'undefined') {
                                    //TODO: We need the event data here so we can decide if we would like to refresh or not
                                    treeVisualiserDAT.refresh();
                                } else {
                                    ev.callback();
                                }
                            }
                        }
                    }
        },

        /**
         * Retrieve commands for a specific variable node
         *
         * @param {Node} node - Geppetto Node used for extracting commands
         * @returns {Array} Set of commands associated with this node
         */
        getCommands: function getCommands(node) {
            var group1 = [{
                label: "Open with DAT Widget",
                action: ["G.addWidget(Widgets.TREEVISUALISERDAT).setData(" + node.getPath() + ")"]
            }];

            var availableWidgets = GEPPETTO.WidgetFactory.getController(GEPPETTO.Widgets.TREEVISUALISERDAT).getWidgets();
            if (availableWidgets.length > 0) {
                var group1Add = {
                    label: "Add to DAT Widget",
                    position: 0
                };

                var subgroups1Add = [];
                for (var availableWidgetIndex in availableWidgets) {
                    var availableWidget = availableWidgets[availableWidgetIndex];
                    subgroups1Add = subgroups1Add.concat([{
                        label: "Add to " + availableWidget.name,
                        action: [availableWidget.id + ".setData(" + node.getPath() + ")"],
                        position: availableWidgetIndex
                    }]);
                }
                group1Add["groups"] = [subgroups1Add];

                group1.push(group1Add);
            }

            var groups = [group1];

            if (node.getMetaType() == GEPPETTO.Resources.COMPOSITE_TYPE_NODE && node.getWrappedObj().getVisualType() != undefined) {
                var entity = [{
                    label: "Select Visual Component",
                    action: ["GEPPETTO.SceneController.deselectAll();", node.getPath() + ".select()"]
                }];

                groups.push(entity);
            }

            if (node.getMetaType() == GEPPETTO.Resources.VISUAL_GROUP_NODE) {
                var visualGroup = [{
                    label: "Show Visual Groups",
                    action: ["GEPPETTO.SceneController.deselectAll();", node.getPath() + ".show(true)"]
                }];

                groups.push(visualGroup);
            }

            if (node.getWrappedObj().capabilities != null && node.getWrappedObj().capabilities.length > 0 && node.getWrappedObj().capabilities.indexOf('VisualGroupCapability') != -1) {
                var visualGroup = [{
                    label: "Show Visual Groups"
                }];

                var subgroups1Add = [];
                for (var visualGroupIndex in node.getWrappedObj().getVisualGroups()) {
                    subgroups1Add = subgroups1Add.concat([{
                        label: "Show " + node.getWrappedObj().getVisualGroups()[visualGroupIndex].getName(),
                        action: ["GEPPETTO.SceneController.deselectAll();", node.getPath() + ".applyVisualGroup(" + node.getPath() + ".getVisualGroups()[" + visualGroupIndex + "], true)"],
                        position: visualGroupIndex
                    }]);
                }
                visualGroup[0]["groups"] = [subgroups1Add];

                groups.push(visualGroup);
            }

            return groups;
        }
    });
}.call(exports, __webpack_require__, exports, module),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ 2199:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_RESULT__;/**
 * Controller class for variables visualiser widget.
 *
 * @author Dan Kruchinin (dkruchinin@acm.org)
 */
!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require) {

    var AWidgetController = __webpack_require__(804);

    /**
     * @exports Widgets/VariableVisualiser/VariableVisualiserController
     */
    return AWidgetController.View.extend({

        initialize: function initialize() {
            this.widgets = [];
        },

        /**
         * Creates new variable visualiser widget
         */
        addWidget: function addWidget(isStateless) {
            if (isStateless == undefined) {
                isStateless = false;
            }

            var that = this;

            return new Promise(function (resolve) {
                __webpack_require__.e/* require.ensure */(24).then((function (require) {
                    var VarVis = __webpack_require__(3372);

                    //look for a name and id for the new widget
                    var id = that.getAvailableWidgetId("VarVis", that.widgets);
                    var name = id;
                    var vv = window[name] = new VarVis({
                        id: id, name: name, visible: true,
                        widgetType: GEPPETTO.Widgets.VARIABLEVISUALISER, stateless: isStateless
                    });

                    vv.help = function () {
                        return GEPPETTO.CommandController.getObjectCommands(id);
                    };

                    // store in local stack
                    that.widgets.push(vv);

                    GEPPETTO.WidgetsListener.subscribe(that, id);

                    //updates help command options
                    GEPPETTO.CommandController.updateHelpCommand(vv, id, that.getFileComments("geppetto/js/components/widgets/variablevisualiser/VariableVisualiser.js"));
                    //update tags for autocompletion
                    GEPPETTO.CommandController.updateTags(vv.getId(), vv);
                    resolve(vv);
                }).bind(null, __webpack_require__)).catch(__webpack_require__.oe);
            });
        },

        /**
         * Receives updates from widget listener class to update variable visualiser widget(s)
         *
         * @param {WIDGET_EVENT_TYPE} event - Event that tells widgets what to do
         */
        update: function update(event, parameters) {
            //delete a widget(s)
            if (event == GEPPETTO.WidgetsListener.WIDGET_EVENT_TYPE.DELETE) {
                this.removeWidgets();
            }
            //update widgets
            else if (event == GEPPETTO.Events.Experiment_update) {
                    var step = parameters.step;
                    for (var i = 0; i < this.widgets.length; i++) {
                        this.widgets[i].updateVariable(step);
                    }
                }
        }
    });
}.call(exports, __webpack_require__, exports, module),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ 2200:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_RESULT__;/**
 * Controller class for connectivity widget. Use to make calls to widget from inside Geppetto.
 *
 * @constructor
 *
 * @module Widgets/Connectivity
 * @author Adrian Quintana (adrian.perez@ucl.ac.uk)
 * @author Boris Marin
 */
!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require) {
    var AWidgetController = __webpack_require__(804);

    /**
     * @exports Widgets/Connectivity/ConnectivityController
     */
    return AWidgetController.View.extend({

        initialize: function initialize() {
            this.widgets = Array();
            this.history = [];
        },

        configureConnectivityWidget: function configureConnectivityWidget() {
            Connectivity.prototype.configViaGUI();
        },

        /**
         * Adds a new Connectivity Widget to Geppetto
         */
        addWidget: function addWidget(isStateless) {
            if (isStateless == undefined) {
                isStateless = false;
            }
            var that = this;

            return new Promise(function (resolve) {
                __webpack_require__.e/* require.ensure */(20).then((function (require) {
                    var Connectivity = __webpack_require__(3375);
                    //look for a name and id for the new widget
                    var id = that.getAvailableWidgetId("Connectivity", that.widgets);
                    var name = id;

                    //create tree visualiser widget
                    var cnt = window[name] = new Connectivity({
                        id: id, name: name, visible: false, width: 500, height: 500, controller: that,
                        widgetType: GEPPETTO.Widgets.CONNECTIVITY, stateless: isStateless
                    });

                    //create help command for connw
                    cnt.help = function () {
                        return GEPPETTO.CommandController.getObjectCommands(id);
                    };

                    //store in local stack
                    that.widgets.push(cnt);

                    GEPPETTO.WidgetsListener.subscribe(that, id);

                    //add commands help option
                    GEPPETTO.CommandController.updateHelpCommand(cnt, id, that.getFileComments("geppetto/js/components/widgets/connectivity/Connectivity.js"));

                    //update tags for autocompletion
                    GEPPETTO.CommandController.updateTags(cnt.getId(), cnt);

                    resolve(cnt);
                }).bind(null, __webpack_require__)).catch(__webpack_require__.oe);
            });
        },

        /**
         * Receives updates from widget listener class to update TreeVisualizer3D widget(s)
         *
         * @param {WIDGET_EVENT_TYPE} event - Event that tells widgets what to do
         */
        update: function update(event) {
            //delete connectivity widget(s)
            if (event == GEPPETTO.WidgetsListener.WIDGET_EVENT_TYPE.DELETE) {
                this.removeWidgets();
            }
            //update connectivity widgets
            else if (event == GEPPETTO.WidgetsListener.WIDGET_EVENT_TYPE.UPDATE) {
                    //loop through all existing widgets
                    for (var i = 0; i < this.widgets.length; i++) {
                        var cnt = this.widgets[i];
                        //update connectivity with new data set
                        cnt.updateData();
                    }
                }
        }
    });
}.call(exports, __webpack_require__, exports, module),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ 2201:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_RESULT__;/**
 * Controller class for the stackViewer widget.
 *
 * @author Robbie1977
 */
!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require) {

    var AWidgetController = __webpack_require__(804);

    /**
     * @exports Widgets/stackViewer/stackViewerController
     */
    return AWidgetController.View.extend({

        initialize: function initialize() {
            this.widgets = Array();
            this.history = [];
        },

        /**
         * Creates new stack viewer widget
         */
        addWidget: function addWidget(isStateless) {
            if (isStateless == undefined) {
                // stateless by default
                isStateless = true;
            }

            var that = this;

            return new Promise(function (resolve) {
                __webpack_require__.e/* require.ensure */(21).then((function (require) {
                    var Stack = __webpack_require__(3674);
                    //look for a name and id for the new widget
                    var id = that.getAvailableWidgetId("StackViewer", that.widgets);
                    var name = id;
                    var vv = window[name] = new Stack({
                        id: id, name: name, visible: true,
                        widgetType: GEPPETTO.Widgets.STACKVIEWER, stateless: isStateless
                    });
                    vv.help = function () {
                        return GEPPETTO.CommandController.getObjectCommands(id);
                    };
                    that.widgets.push(vv);

                    GEPPETTO.WidgetsListener.subscribe(that, id);

                    //updates help command options
                    GEPPETTO.CommandController.updateHelpCommand(vv, id, that.getFileComments("geppetto/js/components/widgets/stackViewer/StackViewer.js"));

                    //update tags for autocompletion
                    GEPPETTO.CommandController.updateTags(vv.getId(), vv);
                    resolve(vv);
                }).bind(null, __webpack_require__)).catch(__webpack_require__.oe);
            });
        },

        /**
         * Receives updates from widget listener class to update Button Bar widget(s)
         *
         * @param {WIDGET_EVENT_TYPE} event - Event that tells widgets what to do
         */
        update: function update(event) {
            //delete a widget(s)
            if (event == GEPPETTO.WidgetsListener.WIDGET_EVENT_TYPE.DELETE) {
                this.removeWidgets();
            }

            //reset widget's datasets
            else if (event == GEPPETTO.WidgetsListener.WIDGET_EVENT_TYPE.RESET_DATA) {}
                //pass


                //update widgets
                else if (event == GEPPETTO.WidgetsListener.WIDGET_EVENT_TYPE.UPDATE) {
                        //pass
                    }
        }
    });
}.call(exports, __webpack_require__, exports, module),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ })

});
//# sourceMappingURL=9.bundle.js.map