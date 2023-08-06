webpackJsonp([19],{

/***/ 2192:
/***/ (function(module, exports, __webpack_require__) {

/* WEBPACK VAR INJECTION */(function(global) {var __WEBPACK_AMD_DEFINE_RESULT__;/**
 * @class The Geppetto admin console
 */
!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require) {

	window.$ = __webpack_require__(16);
	global.GEPPETTO_CONFIGURATION = __webpack_require__(493);
	var React = __webpack_require__(1);
	var ReactDOM = __webpack_require__(13);
	var adminPanel = React.createFactory(__webpack_require__(2193));

	var height = window.innerHeight - 100;

	ReactDOM.render(React.createFactory(adminPanel)({ height: height }), document.getElementById('adminPanel'));
}.call(exports, __webpack_require__, exports, module),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));
/* WEBPACK VAR INJECTION */}.call(exports, __webpack_require__(26)))

/***/ }),

/***/ 2193:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_RESULT__;!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require) {

    __webpack_require__(2194);

    var React = __webpack_require__(1);
    var Griddle = __webpack_require__(492);

    var LinkComponent = React.createClass({
        displayName: 'LinkComponent',

        render: function render() {

            var displayText = this.props.data;
            var that = this;

            var action = function action(e) {
                e.preventDefault();
            };

            var linkDisabled = "";
            if (displayText != "Show Size" && displayText != "ERROR") {
                linkDisabled = "linkDisabled";
            }

            return React.createElement(
                'div',
                null,
                React.createElement(
                    'a',
                    { href: '#', onClick: action, className: linkDisabled },
                    displayText
                )
            );
        }
    });

    var ButtonComponent = React.createClass({
        displayName: 'ButtonComponent',


        render: function render() {
            var addClass = "";
            if (this.props.selectedState) {
                addClass = "selected ";
            }
            return React.createElement(
                'button',
                { id: this.props.id, type: 'button', className: addClass + "button",
                    onClick: this.props.onClick },
                this.props.id
            );
        }
    });

    var DateDisplay = React.createClass({
        displayName: 'DateDisplay',

        render: function render() {
            var options = { year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC', timeZoneName: 'short' };
            var formattedDate = new Date(this.props.data).toLocaleString('en-US', options);
            return React.createElement(
                'div',
                null,
                formattedDate
            );
        }
    });

    var adminPanelComponent = React.createClass({
        displayName: 'adminPanelComponent',

        user: "admin",
        resultsPerPage: 20,
        usersViewSelected: true,
        simulationsViewSelected: false,
        lastDaySelected: false,
        lastWeekSelected: true,
        lastMonthSelected: false,
        allTimeSelected: false,
        currentView: null,
        timeFrame: "week",
        storedData: [],
        views: ["Users", "Simulations"],
        usersColumnMeta: [{
            "columnName": "login",
            "order": 1,
            "locked": false,
            "displayName": "User Name"
        }, {
            "columnName": "name",
            "order": 2,
            "locked": false,
            "displayName": "Name"
        }, {
            "columnName": "loginCount",
            "order": 4,
            "locked": false,
            "displayName": "Login Count"
        }, {
            "columnName": "lastLogin",
            "order": 3,
            "locked": false,
            "sortDirectionCycle": ["desc", "asc"],
            "displayName": "Last Login"
        }, {
            "columnName": "projects",
            "order": 5,
            "locked": false,
            "displayName": "Number of Projects"
        }, {
            "columnName": "experiments",
            "order": 6,
            "locked": false,
            "displayName": "Number of Experiments"
        }, {
            "columnName": "storage",
            "customComponent": LinkComponent,
            "order": 7,
            "locked": false,
            "displayName": "Storage Size"
        }],
        simulationsColumnMeta: [{
            "columnName": "login",
            "order": 1,
            "locked": false,
            "displayName": "Username"
        }, {
            "columnName": "name",
            "order": 2,
            "locked": false,
            "displayName": "Name"
        }, {
            "columnName": "project",
            "order": 3,
            "locked": false,
            "displayName": "Project Name"
        }, {
            "columnName": "experiment",
            "order": 4,
            "locked": false,
            "displayName": "Experiment Name"
        }, {
            "columnName": "experimentLastRun",
            "customComponent": DateDisplay,
            "order": 5,
            "locked": false,
            "displayName": "Experiment Last Time Run"
        }, {
            "columnName": "simulator",
            "order": 6,
            "locked": false,
            "displayName": "Simulator Name"
        }, {
            "columnName": "status",
            "customComponent": LinkComponent,
            "order": 7,
            "locked": false,
            "displayName": "Experiment Status"
        }, {
            "columnName": "error",
            "order": 8,
            "locked": false,
            "visible": false,
            "displayName": "Experiment Error"
        }],
        errorColumns: ['login', 'name', 'project', 'experiment', 'experimentLastRun', 'simulator', 'status'],
        columnMeta: [],

        getInitialState: function getInitialState() {
            return {
                columns: [],
                data: [],
                loaded: false
            };
        },

        setPanelView: function setPanelView() {
            this.forceUpdate();
        },

        componentDidMount: function componentDidMount() {
            this.setInitialData();
        },

        //sets initial data view when component mounts
        setInitialData: function setInitialData() {
            var that = this;
            var urlData = window.location.href.replace("admin", "");
            urlData += "user/admin/users/" + this.timeFrame;
            $.ajax({
                url: urlData, success: function success(result) {
                    that.setDataSet(that.views[0]);
                }
            });
        },

        //switches the data set to show in component
        setDataSet: function setDataSet(mode) {
            var that = this;
            var urlData = window.location.href.replace("admin", "");
            var newColumns;

            if (mode == this.views[0]) {
                urlData += "user/" + this.user + "/users/" + this.timeFrame;
                this.setDataViewFlags(true, false);
                this.columnMeta = this.usersColumnMeta;
                newColumns = [];
            } else if (mode == this.views[1]) {
                urlData += "user/" + this.user + "/simulations/" + this.timeFrame;
                this.setDataViewFlags(false, true);
                this.columnMeta = this.simulationsColumnMeta;
                newColumns = this.errorColumns;
            }

            this.currentView = mode;
            this.setState({ loaded: false });

            var timeFrame = this.timeFrame;
            if (this.storedData[this.currentView + "/" + timeFrame] == null) {
                $.ajax({
                    url: urlData, success: function success(result) {
                        that.storedData[that.currentView + "/" + timeFrame] = result;
                        that.setState({ data: result, columnMeta: that.columnMeta, loaded: true, columns: newColumns });
                    }
                });
            } else {
                this.setState({
                    data: this.storedData[this.currentView + "/" + timeFrame],
                    columnMeta: this.columnMeta,
                    loaded: true,
                    columns: newColumns
                });
            }
        },

        //toggle flags that keep track of what's being displayed
        setDataViewFlags: function setDataViewFlags(user, simulation) {
            this.usersViewSelected = user;
            this.simulationsViewSelected = simulation;
        },

        //toggle flags that keep track of what's being displayed
        setDataTimeFlags: function setDataTimeFlags(day, week, month, allTime) {
            this.lastDaySelected = day;
            this.lastWeekSelected = week;
            this.lastMonthSelected = month;
            this.allTimeSelected = allTime;
        },

        changeViewData: function changeViewData(view) {
            this.setDataSet(view);
        },

        changeTimeData: function changeTimeData(timeFrame) {
            this.timeFrame = timeFrame;
            if (timeFrame == "all") {
                this.setDataTimeFlags(false, false, false, true);
            } else if (timeFrame == "day") {
                this.setDataTimeFlags(true, false, false, false);
            } else if (timeFrame == "week") {
                this.setDataTimeFlags(false, true, false, false);
            } else if (timeFrame == "month") {
                this.setDataTimeFlags(false, false, true, false);
            }

            //uncheck all previously selected checked boxes
            this.setDataSet(this.currentView);
            // uncheck all other checked boxes
            $("input:checkbox").on('click', function () {
                // in the handler, 'this' refers to the box clicked on
                var $box = $(this);
                if ($box.is(":checked")) {
                    // the name of the box is retrieved using the .attr() method
                    // as it is assumed and expected to be immutable
                    var group = "input:checkbox[name='" + $box.attr("name") + "']";
                    // the checked state of the group/box on the other hand will change
                    // and the current value is retrieved using .prop() method
                    $(group).prop("checked", false);
                    $box.prop("checked", true);
                } else {
                    $box.prop("checked", false);
                }
                $box.prop("disabled", true);
            });
        },

        sortData: function sortData(sort, sortAscending, data) {
            //sorting should generally happen wherever the data is coming from
            sortedData = _.sortBy(data, function (item) {
                return item[sort];
            });

            if (sortAscending === false) {
                sortedData.reverse();
            }
            return {
                "currentPage": 0,
                "externalSortColumn": sort,
                "externalSortAscending": sortAscending,
                "pretendServerData": sortedData,
                "results": sortedData.slice(0, this.state.externalResultsPerPage)
            };
        },

        sort: function sort(_sort, sortAscending) {
            this.setState(this.sortData(_sort, sortAscending, this.state.data));
        },

        onRowClick: function onRowClick(rowData, event) {
            var td = event.target;
            if (td.textContent == "Show Size") {
                var login = rowData.props.data.login;

                var urlData = window.location.href.replace("admin", "");
                urlData += "user/" + this.user + "/storage/" + login;

                td.textContent = "Fetching Data";
                var self = this;
                $.ajax({
                    url: urlData, success: function success(result) {
                        var data = self.state.data;
                        if (self.storedData[self.currentView + "/" + self.timeFrame] != null) {
                            for (var key in data) {
                                var object = data[key];
                                if (object.login == login) {
                                    object.storage = result;
                                }
                            }
                        }
                        td.textContent = result;
                        self.setState({ data: data });
                        alert("Storage size for user " + login + " is: " + result);
                    }
                });
            }
            if (td.textContent == "ERROR") {
                var login = rowData.props.data.login;
                var project = rowData.props.data.project;
                var experiment = rowData.props.data.experiment;
                var data = this.state.data;
                if (this.storedData[this.currentView + "/" + this.timeFrame] != null) {
                    for (var key in data) {
                        var object = data[key];
                        if (object.login == login && object.project == project && object.experiment == experiment) {
                            alert(object.error);
                            break;
                        }
                    }
                }
            }
        },

        render: function render() {
            return React.createElement(
                'div',
                null,
                React.createElement(
                    'div',
                    { id: 'adminButtonHeader', className: 'adminButtonHeadverDiv' },
                    React.createElement(ButtonComponent, { id: "Users", selectedState: this.usersViewSelected,
                        onClick: this.changeViewData.bind(this, "Users") }),
                    React.createElement(ButtonComponent, { id: "Simulations", selectedState: this.simulationsViewSelected,
                        onClick: this.changeViewData.bind(this, "Simulations") })
                ),
                React.createElement(
                    'div',
                    { id: 'timeFrameButtonHeader', className: 'timeFrameButtonHeadverDiv' },
                    React.createElement(
                        'label',
                        null,
                        React.createElement('input', { type: 'checkbox', className: 'radio', name: 'checkbox', value: '1',
                            disabled: this.lastDaySelected ? "disabled" : "",
                            checked: this.lastDaySelected ? "checked" : "",
                            onClick: this.changeTimeData.bind(this, "day") }),
                        'Day'
                    ),
                    React.createElement(
                        'label',
                        null,
                        React.createElement('input', { type: 'checkbox', className: 'radio', name: 'checkbox', value: '1',
                            disabled: this.lastWeekSelected ? "disabled" : "",
                            checked: this.lastWeekSelected ? "checked" : "",
                            onClick: this.changeTimeData.bind(this, "week") }),
                        'Week'
                    ),
                    React.createElement(
                        'label',
                        null,
                        React.createElement('input', { type: 'checkbox', className: 'radio', name: 'checkbox', value: '1',
                            disabled: this.lastMonthSelected ? "disabled" : "",
                            checked: this.lastMonthSelected ? "checked" : "",
                            onClick: this.changeTimeData.bind(this, "month") }),
                        'Month'
                    ),
                    React.createElement(
                        'label',
                        null,
                        React.createElement('input', { type: 'checkbox', className: 'radio', name: 'checkbox', value: '1',
                            checked: this.allTimeSelected ? "checked" : "",
                            disabled: this.allTimeSelected ? "disabled" : "",
                            onClick: this.changeTimeData.bind(this, "all") }),
                        'All Time'
                    )
                ),
                this.state.loaded ? React.createElement(Griddle, { results: this.state.data, columnMetadata: this.state.columnMeta,
                    bodyHeight: this.props.height,
                    enableInfinteScroll: true, useGriddleStyles: false,
                    resultsPerPage: this.resultsPerPage, showPager: false,
                    showFilter: true, onRowClick: this.onRowClick, initialSort: "lastLogin",
                    initialSortAscending: false,
                    columns: this.state.columns }) : React.createElement(
                    'div',
                    { id: 'loading-container' },
                    React.createElement('div', { className: 'gpt-gpt_logo fa-spin' }),
                    React.createElement(
                        'p',
                        { className: 'orange loadingText' },
                        'Fetching data (might take a few seconds depending on your network)'
                    )
                )
            );
        }
    });

    return adminPanelComponent;
}.call(exports, __webpack_require__, exports, module),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ 2194:
/***/ (function(module, exports, __webpack_require__) {

// style-loader: Adds some css to the DOM by adding a <style> tag

// load the styles
var content = __webpack_require__(2195);
if(typeof content === 'string') content = [[module.i, content, '']];
// add the styles to the DOM
var update = __webpack_require__(18)(content, {});
if(content.locals) module.exports = content.locals;
// Hot Module Replacement
if(false) {
	// When the styles change, update the <style> tags
	if(!content.locals) {
		module.hot.accept("!!../../../node_modules/css-loader/index.js!../../../node_modules/less-loader/dist/cjs.js?{\"modifyVars\":{\"url\":\"'../../../extensions/geppetto-netpyne/css/colors'\"}}!./AdminPanel.less", function() {
			var newContent = require("!!../../../node_modules/css-loader/index.js!../../../node_modules/less-loader/dist/cjs.js?{\"modifyVars\":{\"url\":\"'../../../extensions/geppetto-netpyne/css/colors'\"}}!./AdminPanel.less");
			if(typeof newContent === 'string') newContent = [[module.id, newContent, '']];
			update(newContent);
		});
	}
	// When the module is disposed, remove the <style> tags
	module.hot.dispose(function() { update(); });
}

/***/ }),

/***/ 2195:
/***/ (function(module, exports, __webpack_require__) {

exports = module.exports = __webpack_require__(17)(undefined);
// imports


// module
exports.push([module.i, ".dark-orange {\n  color: #cc215a;\n}\n.orange {\n  color: #f23d7a;\n}\n.orange-color {\n  color: #f23d7a;\n}\n.orange-color-bg {\n  background-color: #f23d7a;\n}\n#adminPanel {\n  padding-top: 10px;\n  width: 100%;\n  height: 100%;\n}\n#adminButtonHeader {\n  height: 70px;\n  width: 350px;\n  margin: 0 auto;\n  text-align: center;\n}\n.timeFrameButtonHeadverDiv {\n  height: 70px;\n  width: 500px;\n  margin: 0 auto;\n  padding-left: 100px;\n}\n.griddle-filter input {\n  height: 30px;\n  font-size: 20px;\n  width: 100%;\n}\n.timeFrameButtonHeadverDiv label {\n  text-align: center;\n  font-size: 18px;\n  margin-right: 10px;\n}\nbody {\n  background-color: #f5f5f5;\n  font-family: Helvetica Neue;\n  font-weight: 200;\n}\ntable {\n  margin: 0 auto;\n  margin-top: 10px;\n  width: 100%;\n  table-layout: fixed;\n}\n.button {\n  margin-right: 10px;\n  color: white;\n  font-size: 18px;\n  border-radius: 0px;\n  border: 0;\n  height: 40px;\n  float: left;\n  background: #3f3f3f;\n  cursor: pointer;\n  width: 120px;\n}\n.selected {\n  background: #f23d7a;\n}\n.griddle th {\n  background-color: rgba(173, 158, 158, 0.7);\n  border: 0px;\n  color: ##000;\n  padding: 5px;\n  text-align: center;\n}\n.griddle td {\n  padding: 5px;\n  background-color: rgba(204, 185, 185, 0.7);\n  color: #000;\n  border-bottom: 1px dashed;\n  border-color: rgba(255, 255, 255, 0.2);\n  text-align: center;\n  overflow: hidden;\n  text-overflow: ellipsis;\n}\n.griddle {\n  width: 90%;\n  margin: 0 auto;\n}\n.gpt-gpt_logo {\n  width: 100px;\n  font-size: 100px;\n  margin: 0 auto;\n  margin-bottom: 30px;\n  color: #f23d7a;\n}\n.loadingText {\n  text-align: center;\n  font-size: 18px;\n}\n#loading-container {\n  padding-top: 100px;\n  padding-right: 100px;\n}\n.linkDisabled {\n  pointer-events: none;\n  text-decoration: none;\n  color: black;\n}\n", ""]);

// exports


/***/ })

},[2192]);
//# sourceMappingURL=admin.bundle.js.map