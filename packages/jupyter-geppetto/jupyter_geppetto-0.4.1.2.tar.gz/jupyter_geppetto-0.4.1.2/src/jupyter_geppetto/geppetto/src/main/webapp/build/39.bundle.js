webpackJsonp([39],{

/***/ 1411:
/***/ (function(module, exports, __webpack_require__) {

// style-loader: Adds some css to the DOM by adding a <style> tag

// load the styles
var content = __webpack_require__(1412);
if(typeof content === 'string') content = [[module.i, content, '']];
// add the styles to the DOM
var update = __webpack_require__(18)(content, {});
if(content.locals) module.exports = content.locals;
// Hot Module Replacement
if(false) {
	// When the styles change, update the <style> tags
	if(!content.locals) {
		module.hot.accept("!!../../../../node_modules/css-loader/index.js!../../../../node_modules/less-loader/dist/cjs.js?{\"modifyVars\":{\"url\":\"'../../../extensions/geppetto-netpyne/css/colors'\"}}!./MenuButton.less", function() {
			var newContent = require("!!../../../../node_modules/css-loader/index.js!../../../../node_modules/less-loader/dist/cjs.js?{\"modifyVars\":{\"url\":\"'../../../extensions/geppetto-netpyne/css/colors'\"}}!./MenuButton.less");
			if(typeof newContent === 'string') newContent = [[module.id, newContent, '']];
			update(newContent);
		});
	}
	// When the module is disposed, remove the <style> tags
	module.hot.dispose(function() { update(); });
}

/***/ }),

/***/ 1412:
/***/ (function(module, exports, __webpack_require__) {

exports = module.exports = __webpack_require__(17)(undefined);
// imports


// module
exports.push([module.i, ".dark-orange {\n  color: #cc215a;\n}\n.orange {\n  color: #f23d7a;\n}\n.orange-color {\n  color: #f23d7a;\n}\n.orange-color-bg {\n  background-color: #f23d7a;\n}\n.menuButtonIcon {\n  padding-right: 5px;\n}\n.menuListContainer {\n  z-index: 100 !important;\n}\n.dropDownButtonContainer {\n  position: fixed;\n  z-index: 99;\n  height: auto;\n  width: auto;\n  background-color: #ffffff;\n}\n.dropDownButtonContainer:disabled {\n  background: 0;\n  color: #f23d7a;\n}\n.dropDownTable {\n  color: #f23d7a;\n  float: left;\n  padding-right: 10px;\n  white-space: nowrap;\n  width: 100%;\n  height: auto;\n  overflow: hidden;\n}\n.dropDownTable label {\n  float: left;\n  display: inline-block;\n  margin-top: 0;\n  margin-bottom: 0;\n  font-weight: normal;\n  text-align: center;\n  vertical-align: middle;\n  cursor: pointer;\n  font-size: 14px;\n}\n.dropDownTable label:hover {\n  color: white;\n}\n.dropDownTable tr {\n  cursor: pointer;\n}\n.dropDownTable tr:not(:hover) label {\n  color: #f23d7a;\n}\n.dropDownTable tr:hover {\n  background-color: #f23d7a;\n  color: white;\n}\n.dropDownTable tr:hover label {\n  color: white;\n}\n.dropDownItem {\n  display: inline-block;\n}\n.selectedStatus {\n  width: 50px;\n  padding-left: 15px;\n}\n.menuBtnListItem {\n  text-align: left;\n}\n.dropDownLabel {\n  padding: 5px 20px 5px 0;\n}\n", ""]);

// exports


/***/ }),

/***/ 489:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_RESULT__;/**
 * Reusable drop down button React component. 
 * Takes in a configuration with properties and data, uses it 
 * to create button and drop down.
 * 
 * @author Jesus R Martinez (jesus@metacell.us) 
 * 
 * @param require
 * @returns
 */
!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require) {
    var React = __webpack_require__(1);
    var GEPPETTO = __webpack_require__(71);
    __webpack_require__(1411);

    var ListItem = React.createClass({
        displayName: 'ListItem',


        updateIcon: false,
        icons: {
            checked: "fa fa-check-circle-o",
            unchecked: "fa fa-circle-o",
            default: "fa fa-bolt"
        },

        getInitialState: function getInitialState() {
            return {
                icon: ""
            };
        },

        select: function select() {
            this.props.handleSelect(this.props.item.value, this.props.item.radio);

            var iconState = this.icons.default;
            var action = null;

            if (this.props.item.condition != undefined) {
                // evaluate condition
                var condition = null;
                try {
                    condition = eval(this.props.item.condition);
                } catch (e) {
                    throw "Could not evaluate condition [" + this.props.item.condition + "]";
                }

                if (typeof condition === "boolean") {
                    // assign action
                    action = condition ? this.props.item.true.action : this.props.item.false.action;
                    // assign icon status
                    iconState = condition ? this.icons.unchecked : this.icons.checked;
                } else {
                    throw "The condition [" + this.props.item.condition + "] doesn't resolve to a boolean";
                }
            } else {
                // if condition does not exist, simply assign action
                action = this.props.item.action;
            }

            // execute action
            if (action != null) {
                GEPPETTO.CommandController.execute(action, true);
            }

            this.setState({ icon: iconState });
        },

        componentDidMount: function componentDidMount() {
            var iconState = this.getIconState();
            this.setState({ icon: iconState });
        },

        getIconState: function getIconState() {
            // figure out icon for this item
            var iconState = this.icons.default;
            if (this.props.item.condition != undefined) {
                // evaluate condition
                var condition = null;
                try {
                    condition = eval(this.props.item.condition);
                } catch (e) {
                    throw "Could not evaluate condition [" + this.props.item.condition + "]";
                }

                if (typeof condition === "boolean") {
                    // assign icon status
                    iconState = condition ? this.icons.checked : this.icons.unchecked;
                } else {
                    throw "The condition [" + this.props.item.condition + "] doesn't resolve to a boolean";
                }
            }

            return iconState;
        },

        render: function render() {
            var iconState = this.getIconState();
            this.state.icon = iconState;

            var outerClass = "menuBtnListItem";
            var innerClass = "";
            if (this.props.parentDisabled && this.props.item.disabled) {
                outerClass += " menuBtnListItemDisabled";
                innerClass += " menuBtnListItemDisabled";
            }

            return React.createElement(
                'tr',
                { className: outerClass, onClick: this.select },
                React.createElement(
                    'td',
                    { className: 'selectedStatus' },
                    React.createElement('i', { className: "iconSelectionStatus " + this.state.icon })
                ),
                React.createElement(
                    'td',
                    { className: 'dropDownLabel' },
                    React.createElement(
                        'label',
                        { className: innerClass },
                        React.createElement(
                            'span',
                            null,
                            this.props.item.label
                        )
                    )
                )
            );
        }
    });

    var DropDownControlComp = React.createClass({
        displayName: 'DropDownControlComp',

        onClickHandler: null,
        menuPosition: null,

        getInitialState: function getInitialState() {
            return {
                visible: this.props.configuration.openByDefault,
                configuration: null
            };
        },

        componentDidMount: function componentDidMount() {
            var self = this;

            var selector = $("#" + this.props.configuration.id + "-dropDown");

            window.addEventListener('resize', function (event) {
                if (selector != null && selector != undefined) {
                    if (self.state.visible) {
                        self.menuPosition = self.getMenuPosition();
                        selector.css({
                            top: self.menuPosition.top, right: self.menuPosition.right,
                            bottom: self.menuPosition.bottom, left: self.menuPosition.left, position: 'fixed'
                        });
                    }
                }
            });
        },

        renderListItems: function renderListItems() {
            var items = [];
            if (this.props.configuration.menuItems != undefined || null) {
                for (var i = 0; i < this.props.configuration.menuItems.length; i++) {
                    var item = this.props.configuration.menuItems[i];
                    if (item.radio) {
                        // include a ref for every radio item so we can call their select method from other items
                        items.push(React.createElement(ListItem, { key: i, item: item, ref: item.value, handleSelect: this.handleSelect, parentDisabled: this.props.configuration.buttonDisabled }));
                    } else {
                        items.push(React.createElement(ListItem, { key: i, item: item, handleSelect: this.handleSelect, parentDisabled: this.props.configuration.buttonDisabled }));
                    }
                }
            }
            return items;
        },

        handleSelect: function handleSelect(value, radio) {
            // call select on any other 'checked' radio items to deselect them
            if (radio) {
                for (var key in this.refs) {
                    var ref = this.refs[key];
                    if (ref.props.item.value != value && ref.state.icon == ref.icons.checked && ref.props.item.radio) {
                        ref.select();
                    }
                }
            }
            this.props.handleSelect(value);

            if (this.props.configuration.autoFormatMenu) {
                for (var i = 0; i < this.props.configuration.menuItems.length; i++) {
                    var item = this.props.configuration.menuItems[i];
                    if (item.value == value) {
                        this.props.configuration.menuItems.splice(i, 1);
                        this.props.configuration.menuItems.unshift(item);
                    }
                }

                this.forceUpdate();
            }
        },

        getMenuPosition: function getMenuPosition() {
            var selector = $("#" + this.props.configuration.id);
            var horizontalOffset = this.props.configuration.horizontalOffset != undefined ? this.props.configuration.horizontalOffset : 0;
            return {
                top: selector.offset().top + selector.outerHeight(),
                left: selector.offset().left - (selector.outerHeight() - selector.innerHeight()) - horizontalOffset
            };
        },

        close: function close() {
            this.setState({ visible: false });
        },

        calculateSizeandPosition: function calculateSizeandPosition() {
            var menuSize = null;
            var self = this;
            //if position wasn't specify for location of menu list
            if (self.props.configuration.menuPosition == null || self.props.configuration.menuPosition == undefined) {
                //compute best spot for menu to show up by getting the button's top
                //and left values, and considering padding values as well
                this.menuPosition = self.getMenuPosition();
            } else {
                //assign position of menu to what it is in configuration passed
                this.menuPosition = self.props.configuration.menuPosition;
            }

            if (self.props.configuration.menuSize != null && self.props.configuration.menuSize != undefined) {
                menuSize = {
                    width: self.props.configuration.menuSize.width,
                    height: self.props.configuration.menuSize.height
                };
            }

            var selector = $("#" + this.props.configuration.id + "-dropDown");
            selector.css({
                top: self.menuPosition.top, right: self.menuPosition.right,
                bottom: self.menuPosition.bottom, left: self.menuPosition.left, position: 'fixed'
            });

            var table = $("#" + this.props.configuration.id + "-dropDownTable");
            if (menuSize != null) {
                if (menuSize.width != undefined && menuSize.height != undefined) {
                    table.css({
                        width: menuSize.width,
                        height: menuSize.height
                    });
                }
            }
        },

        open: function open() {
            this.calculateSizeandPosition();

            //makes sure that menu position is not offscreen or at 0,0
            if (this.menuPosition.top <= 0 && this.menuPosition.left <= 0) {
                this.menuPosition = this.getMenuPosition();
                var selector = $("#" + this.props.configuration.id + "-dropDown");

                if (this.menuPosition != null && this.menuPosition != undefined) {
                    var that = this;
                    selector.css({
                        top: that.menuPosition.top, right: that.menuPosition.right,
                        bottom: that.menuPosition.bottom, left: that.menuPosition.left, position: 'fixed'
                    });
                }
            }
            this.setState({ visible: true });
        },

        render: function render() {
            return React.createElement(
                'div',
                { id: this.props.configuration.id + "-dropDownTable", className: (this.state.visible ? 'show' : 'hide') + " dropDownButtonContainer" },
                React.createElement(
                    'table',
                    { className: this.props.configuration.menuCSS + " dropDownTable", id: 'dropDownTable' },
                    React.createElement(
                        'tbody',
                        null,
                        this.renderListItems()
                    )
                )
            );
        }
    });

    var MenuButton = React.createClass({
        displayName: 'MenuButton',

        menu: null,
        onLoadHandler: null,
        positionUpdated: false,

        getInitialState: function getInitialState() {
            return {
                icon: this.props.configuration.iconOff,
                open: false,
                menuItems: this.props.configuration.menuItems
            };
        },

        refresh: function refresh() {
            this.forceUpdate();
        },

        updateMenuItems: function updateMenuItems(items) {
            this.setState({ menuItems: items });
        },

        addMenuItem: function addMenuItem(item) {
            if (this.props.configuration.menuItems == null || this.props.configuration.menuItems == undefined) {
                this.props.configuration.menuItems = new Array();
            }
            this.props.configuration.menuItems.push(item);
            this.refresh();
        },

        //Makes the drop down menu visible
        showMenu: function showMenu() {
            var self = this;
            if (self.props.configuration.menuItems.length > 0) {
                self.refs.dropDown.open();
            }

            if (typeof self.props.configuration.menuItems.then === "function") {
                self.props.configuration.menuItems.then(function (val) {
                    self.props.configuration.menuItems = val;
                    self.refs.dropDown.open();
                });
            }

            var showIcon = this.props.configuration.iconOn;
            this.setState({ open: true, icon: showIcon });
        },

        hideMenu: function hideMenu() {
            this.refs.dropDown.close();
            var showIcon = this.props.configuration.iconOff;
            this.setState({ open: false, icon: showIcon });
        },

        //Adds external handler for click events, notifies it when a drop down item is clicked
        selectionChanged: function selectionChanged(value) {
            if (this.props.configuration.closeOnClick) {
                this.toggleMenu();
                if (this.onClickHandler != undefined && this.onClickHandler != null) {
                    this.onClickHandler(value);
                }
            }
        },

        //Adds external load handler, gets notified when component is mounted and ready
        addExternalLoadHandler: function addExternalLoadHandler() {
            var self = this;
            self.onLoadHandler = self.props.configuration.onLoadHandler;
            if (self.onLoadHandler != null || undefined) {
                self.onLoadHandler(self);
            }
        },

        componentWillUnmount: function componentWillUnmount() {
            this.onLoadHandler = null;
            this.onClickHandler = null;
        },

        componentDidMount: function componentDidMount() {
            var self = this;

            //attach external handler for loading events
            self.onClickHandler = self.props.configuration.onClickHandler;

            //attach external handler for clicking events
            self.addExternalLoadHandler();
            if (this.props.configuration.closeOnClick) {
                var container = $('#' + this.props.configuration.id + "-container");
                $('body').click(function (e) {
                    // if the target of the click isn't the container nor a descendant of the container
                    if (!container.is(e.target) && container.has(e.target).length === 0) {
                        if (self.props.configuration.closeOnClick) {
                            if (self.state.open) {
                                if (self.isMounted()) {
                                    self.hideMenu();
                                }
                            }
                        }
                    }
                });
            }
        },

        //toggles visibility of drop down menu
        toggleMenu: function toggleMenu() {
            if (this.state.open) {
                this.hideMenu();
            } else {
                this.showMenu();
            }
        },

        render: function render() {
            return React.createElement(
                'div',
                { id: this.props.configuration.id + "-container", className: 'menuButtonContainer' },
                React.createElement(
                    'button',
                    { className: this.props.configuration.id + " btn " + this.props.configuration.buttonClassName, type: 'button', title: '',
                        id: this.props.configuration.id, onClick: this.toggleMenu,
                        disabled: this.props.configuration.buttonDisabled && this.props.configuration.disableable, ref: 'menuButton' },
                    React.createElement('i', { className: this.state.icon + " menuButtonIcon" }),
                    this.props.configuration.label
                ),
                React.createElement(
                    'div',
                    { id: this.props.configuration.id + "-dropDown", className: 'menuListContainer' },
                    React.createElement(DropDownControlComp, { handleSelect: this.selectionChanged, ref: 'dropDown', configuration: this.props.configuration, parentDisabled: this.props.configuration.buttonDisabled })
                )
            );
        }
    });

    return MenuButton;
}.call(exports, __webpack_require__, exports, module),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ })

});
//# sourceMappingURL=39.bundle.js.map