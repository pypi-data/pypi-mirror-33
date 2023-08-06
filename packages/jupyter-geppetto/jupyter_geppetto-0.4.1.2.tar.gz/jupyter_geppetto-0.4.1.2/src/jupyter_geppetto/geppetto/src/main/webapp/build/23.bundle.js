webpackJsonp([23],{

/***/ 2272:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_RESULT__;function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

/**
 *
 * Base Widget Class, all widgets extend this class.
 * @module Widgets/Widget
 * @author  Jesus R. Martinez (jesus@metacell.us)
 */
!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require) {
    var _Backbone$View$extend;

    var Backbone = __webpack_require__(94);
    var $ = __webpack_require__(16);
    __webpack_require__(803);

    var zIndex = {
        min: 1,
        max: 9999,
        restore: 10
    };

    return {

        /**
         * Not yet implemented, used for local storage and history.
         */
        Model: Backbone.Model.extend({}),

        /**
         * Creates base view for widget
         */
        View: Backbone.View.extend((_Backbone$View$extend = {

            id: null,
            dialog: null,
            visible: true,
            destroyed: false,
            size: {},
            position: {},
            registeredEvents: null,
            executedAction: 0,
            lastExecutedAction: 0,
            title: null,
            previousMaxTransparency: false,
            previousMaxSize: {},
            maximize: false,
            collapsed: false,
            widgetType: null,
            stateless: false,
            showTitleBar: true,
            transparentBackground: false,
            dirtyView: false,
            updateHistoryPosition: true,
            helpInfo: '### Inline help not yet available for this widget! \n\n' + 'Try the <a href="http://docs.geppetto.org/en/latest/usingwidgets.html"' + 'target="_blank">online documentation</a> instead.',

            defaultSize: function defaultSize() {
                return { height: 300, width: 350 };
            },
            defaultPosition: function defaultPosition() {
                return { left: "50%", top: "50%" };
            },
            /**
             * Initializes the widget
             *
             * @param {String} id - id of widget
             * @param {String} name - name of widget
             * @param {String} visibility - visibility of widget window
             */
            initialize: function initialize(options) {
                this.id = options.id;
                this.name = options.name;
                this.visible = options.visible;
                this.size = this.defaultSize();
                this.position = this.defaultPosition();
                this.contextMenu = new GEPPETTO.ContextMenuView();
                this.historyMenu = new GEPPETTO.ContextMenuView();
                this.widgetType = options.widgetType;
                this.stateless = options.stateless != undefined ? options.stateless : false;
                this.registeredEvents = [];
                this.dirtyView = false;

                var self = this;
                $(self.historyMenu.el).on('click', function (event) {
                    var itemId = $(event.target).attr('id');
                    var registeredItem = self.historyMenu.getClickedItem(itemId);
                    if (registeredItem != null || registeredItem != undefined) {
                        var label = registeredItem["label"];
                        self.title = label;
                        $("#" + self.id).parent().find(".ui-dialog-title").html(self.title);
                    }
                });
                window.addEventListener('resize', function (event) {
                    if (self.maximize) {
                        self.maximize = false;
                        self.setSize(window.innerHeight, window.innerWidth);
                        self.$el.trigger('resizeEnd', ["maximize"]);
                        self.maximize = true;
                    }
                });

                //this.setSize(this.defaultSize.height, this.defaultSize.width);
            },

            /**
             * Destroy the widget, remove it from DOM
             *
             * @command destroy()
             * @returns {String} - Action Message
             */
            destroy: function destroy() {
                this.$el.remove();
                this.destroyed = true;
                return this.name + " destroyed";
            },

            /**
             * Hides the widget
             *
             * @command hide()
             * @returns {String} - Action Message
             */
            hide: function hide() {
                this.$el.dialog('close').dialogExtend();

                this.visible = false;

                return "Hiding " + this.name + " widget";
            },

            /**
             *  Opens widget dialog
             *
             * @command show()
             * @returns {Object} - Action Message
             */
            show: function show() {
                this.$el.dialog('open').dialogExtend();
                this.visible = true;

                //Unfocused close button
                $(".ui-dialog-titlebar-close").blur();

                return this;
            },

            /**
             * Returns widget type as defined in GEPPETTO.Widgets
             *
             * @returns {int}
             */
            getComponentType: function getComponentType() {
                return this.widgetType;
            },

            /**
             * Gets the name of the widget
             *
             * @command getName()
             * @returns {String} - Name of widget
             */
            getName: function getName() {
                return this.name;
            },

            /**
             * Sets the name of the widget
             * @command setName(name)
             * @param {String} name - Name of widget
             */
            setName: function setName(name) {
                this.name = name;

                // set name to widget window
                this.$el.dialog("option", "title", this.name).dialogExtend();

                // set flag to indicate something changed
                this.dirtyView = true;

                return this;
            },

            /**
             * @command setPosition(left,top)
             * @param {Integer} left -Left position of the widget
             * @param {Integer} top - Top position of the widget
             */
            setPosition: function setPosition(left, top) {
                if (left != null && left != undefined) {
                    this.position.left = left;
                }
                if (top != null && top != undefined) {
                    this.position.top = top;
                }

                this.$el.dialog('option', 'position', {
                    my: "left+" + this.position.left + " top+" + this.position.top,
                    at: "left top",
                    of: $(window)
                }).dialogExtend();

                // set flag to indicate something changed
                this.dirtyView = true;

                return this;
            },

            /**
             * Sets the size of the widget
             * @command setSize(h,w)
             * @param {Integer} h - Height of the widget
             * @param {Integer} w - Width of the widget
             */
            setSize: function setSize(h, w) {
                if (h != null && h != undefined && h != -1) {
                    this.size.height = h;
                }
                if (w != null && w != undefined && w != -1) {
                    this.size.width = w;
                }
                this.$el.dialog({ height: this.size.height, width: this.size.width }).dialogExtend();

                this.$el.trigger('resizeEnd');

                // set flag to indicate something changed
                this.dirtyView = true;

                return this;
            },

            /**
             * @command setMinHeight(h)
             * @param {Integer} h - Minimum Height of the widget
             */
            setMinHeight: function setMinHeight(h) {
                this.$el.dialog('option', 'minHeight', h).dialogExtend();
                return this;
            },

            /**
             * @command setMinWidth(w)
             * @param {Integer} w - Minimum Width of the widget
             */
            setMinWidth: function setMinWidth(w) {
                this.$el.dialog('option', 'minWidth', w).dialogExtend();
                return this;
            },

            /**
             * @command setMinSize(h,w)
             * @param {Integer} h - Minimum Height of the widget
             * @param {Integer} w - Minimum Width of the widget
             */
            setMinSize: function setMinSize(h, w) {
                this.setMinHeight(h);
                this.setMinWidth(w);
                return this;
            },

            /**
             * @command setResizable(true|false)
             * @param {Boolean} true|false - enables / disables resizability
             */
            setResizable: function setResizable(resize) {
                this.$el.dialog('option', 'resizable', resize).dialogExtend();
                return this;
            },

            /**
             * @command setAutoWidth()
             */
            setAutoWidth: function setAutoWidth() {
                this.$el.dialog('option', 'width', 'auto').dialogExtend();
                return this;
            },

            /**
             * @command setAutoHeigth()
             */
            setAutoHeight: function setAutoHeight() {
                this.$el.dialog('option', 'height', 'auto').dialogExtend();
                return this;
            },

            /**
             * Returns the position of the widget
             * @command getPosition()
             * @returns {Object} - Position of the widget
             */
            getPosition: function getPosition() {
                return this.position;
            },

            /**
             * Returns the size of the widget
             * @command getSize()
             * @returns {Object} - Size of the widget
             */
            getSize: function getSize() {
                return this.size;
            },

            /**
             * Gets the ID of the widget
             *
             * @command getId()
             * @returns {String} - ID of widget
             */
            getId: function getId() {
                return this.id;
            },

            /**
             * Did something change in the state of the widget?
             *
             * @command isDirty()
             * @returns {boolean} - ID of widget
             */
            isDirty: function isDirty() {
                return this.dirtyView;
            },

            /**
             * Explicitly sets status of view
             * NOTE: we need to be able to control this from outside the component
             *
             * @command setDirty()
             * @param {boolean} dirty
             */
            setDirty: function setDirty(dirty) {
                this.dirtyView = dirty;
            },

            /**
             * Returns whether widget is visible or not
             *
             * @command isVisible()
             * @returns {Boolean} - Widget visibility state
             */
            isVisible: function isVisible() {
                return this.visible;
            },

            /**
             * Search obj for the value of node within using path.
             * E.g. If obj = {"tree":{"v":1}} and path is "tree.v", it will
             * search within the obj to find the value of "tree.v", returning object
             * containing {value : val, unit : unit, scale : scale}.
             */
            getState: function getState(tree, state) {
                var paths = state.split('.'),
                    current = tree,
                    i;

                for (i = 0; i < paths.length; ++i) {
                    //get index from node if it's array
                    var index = paths[i].match(/[^[\]]+(?=])/g);

                    if (index == null) {
                        if (current[paths[i]] == undefined) {
                            return undefined;
                        } else {
                            current = current[paths[i]];
                        }
                    } else {
                        var iNumber = index[0].replace(/[\[\]']+/g, "");

                        //take index and brackets out of the equation for now
                        var node = paths[i].replace(/ *\[[^]]*\] */g, "");

                        if (current[node][parseInt(iNumber)] == undefined) {
                            return undefined;
                        } else {
                            current = current[node][parseInt(iNumber)];
                        }
                    }
                }
                return current;
            },

            getItems: function getItems(history, name) {
                var data = [];
                for (var i = 0; i < history.length; i++) {
                    var action = this.getId() + "[" + this.getId() + "." + name + "[" + i + "].method].apply(" + this.getId() + ", " + this.getId() + "." + name + "[" + i + "].arguments)";
                    data.push({
                        "label": history[i].label,
                        "action": [action],
                        "icon": null,
                        "position": i
                    });
                }
                return data;
            },

            showHistoryMenu: function showHistoryMenu(event) {
                var that = this;
                if (this.controller.history.length > 0) {
                    that.updateHistoryPosition = true;
                    this.historyMenu.show({
                        top: event.pageY,
                        left: event.pageX + 1,
                        groups: that.getItems(that.controller.history, "controller.history"),
                        data: that
                    });
                }

                if (event != null) {
                    event.preventDefault();
                }
                return false;
            },

            showContextMenu: function showContextMenu(event, data) {
                var handlers = GEPPETTO.MenuManager.getCommandsProvidersFor(data.getMetaType());

                if (handlers.length > 0) {
                    var groups = [];
                    for (var handlerIndex = 0; handlerIndex < handlers.length; handlerIndex++) {
                        groups = groups.concat(handlers[handlerIndex](data));
                    }

                    this.contextMenu.show({
                        top: event.pageY,
                        left: event.pageX + 1,
                        groups: groups,
                        //registeredItems: registeredItems,
                        data: data
                    });
                }

                if (event != null) {
                    event.preventDefault();
                }

                return false;
            }

        }, _defineProperty(_Backbone$View$extend, 'showTitleBar', function showTitleBar(show) {
            this.hasTitleBar = show;

            if (show) {
                this.$el.parent().find(".ui-dialog-titlebar").show();
            } else {
                this.$el.parent().find(".ui-dialog-titlebar").hide();
            }

            // set flag to indicate something changed
            this.dirtyView = true;

            return this;
        }), _defineProperty(_Backbone$View$extend, 'updateNavigationHistoryBar', function updateNavigationHistoryBar() {
            var disabled = "arrow-disabled";
            if (this.getItems(this.controller.staticHistoryMenu, "controller.staticHistoryMenu").length <= 1) {
                if (!$("#" + this.id + "-left-nav").hasClass(disabled)) {
                    $("#" + this.id + "-left-nav").addClass(disabled);
                    $("#" + this.id + "-right-nav").addClass(disabled);
                }
            } else {
                if ($("#" + this.id + "-left-nav").hasClass(disabled)) {
                    $("#" + this.id + "-left-nav").removeClass(disabled);
                    $("#" + this.id + "-right-nav").removeClass(disabled);
                }
            }
        }), _defineProperty(_Backbone$View$extend, 'showHistoryNavigationBar', function showHistoryNavigationBar(show) {
            this.hasHistoryNavigationBar = show;
            var leftNav = $("#" + this.id + "-left-nav");
            var rightNav = $("#" + this.id + "-right-nav");

            if (show) {
                if (leftNav.length == 0 && rightNav.length == 0) {

                    var disabled = "";
                    if (this.getItems(this.controller.staticHistoryMenu, "controller.staticHistoryMenu").length <= 1) {
                        disabled = "arrow-disabled ";
                    }

                    var that = this;
                    var button = $("<div id='" + this.id + "-left-nav' class='" + disabled + "fa fa-arrow-left'></div>" + "<div id='" + this.id + "-right-nav' class='" + disabled + "fa fa-arrow-right'></div>").click(function (event) {
                        var historyItems = that.getItems(that.controller.staticHistoryMenu, "controller.staticHistoryMenu");
                        var item;
                        that.lastExecutedAction = $("#" + that.id).parent().find(".ui-dialog-title").html();
                        if (event.target.id == that.id + "-right-nav") {
                            that.executedAction = that.executedAction + 1;
                            if (that.executedAction >= historyItems.length) {
                                that.executedAction = 0;
                            }

                            var match = that.executedAction;
                            for (var i = 0; i < historyItems.length; i++) {
                                var currentItem = historyItems[i];
                                if (that.lastExecutedAction == currentItem.label) {
                                    match = i;
                                }
                            }

                            if (that.lastExecutedAction == historyItems[that.executedAction].label) {
                                that.executedAction = match + 1;
                            }

                            if (that.executedAction <= match) {
                                that.executedAction = match + 1;
                                if (that.executedAction >= historyItems.length) {
                                    that.executedAction = 0;
                                }
                            }
                        }
                        if (event.target.id == that.id + "-left-nav") {
                            that.executedAction = that.executedAction - 1;
                            if (that.executedAction <= -1) {
                                that.executedAction = historyItems.length - 1;
                            }

                            var match = that.executedAction;
                            for (var i = 0; i < historyItems.length; i++) {
                                var currentItem = historyItems[i];
                                if (that.lastExecutedAction == currentItem.label) {
                                    match = i;
                                }
                            }

                            if (that.lastExecutedAction == historyItems[that.executedAction].label) {
                                that.executedAction = match - 1;
                            }

                            if (that.executedAction <= -1) {
                                that.executedAction = historyItems.length - 1;
                            }

                            if (that.executedAction > match) {
                                that.executedAction = match - 1;
                                if (that.executedAction <= -1) {
                                    that.executedAction = historyItems.length - 1;
                                }
                            }
                        }
                        that.updateHistoryPosition = false;
                        item = historyItems[that.executedAction].action[0];
                        GEPPETTO.CommandController.execute(item, true);
                        $("#" + that.id).parent().find(".ui-dialog-title").html(historyItems[that.executedAction].label);
                        event.stopPropagation();
                    });

                    button.insertBefore(this.dialogParent.find("span.ui-dialog-title"));
                    $(button).addClass("widget-title-bar-button");
                }
            } else {
                if (leftNav.is(":visible") && rightNav.is(":visible")) {
                    leftNav.remove();
                    rightNav.remove();
                    this.executedAction = 0;
                }
            }
        }), _defineProperty(_Backbone$View$extend, 'showCloseButton', function showCloseButton(show) {
            if (show) {
                this.$el.parent().find(".ui-dialog-titlebar-close").show();
            } else {
                this.$el.parent().find(".ui-dialog-titlebar-close").hide();
            }
        }), _defineProperty(_Backbone$View$extend, 'addButtonToTitleBar', function addButtonToTitleBar(button) {
            this.dialogParent.find("div.ui-dialog-titlebar").prepend(button);
            $(button).addClass("widget-title-bar-button");
        }), _defineProperty(_Backbone$View$extend, 'setDraggable', function setDraggable(draggable) {
            if (draggable) {
                this.$el.parent().draggable({ disabled: false });
                // NOTE: this will wipe any class applied to the widget...
                this.setClass('');
            } else {
                this.$el.parent().draggable({ disabled: true });
                this.setClass('noStyleDisableDrag');
            }
        }), _defineProperty(_Backbone$View$extend, 'setTransparentBackground', function setTransparentBackground(isTransparent) {
            this.transparentBackground = isTransparent;

            if (isTransparent) {
                this.$el.parent().addClass('transparent-back');
                this.previousMaxTransparency = true;
            } else {
                this.$el.parent().removeClass('transparent-back');
            }
            return this;
        }), _defineProperty(_Backbone$View$extend, 'setClass', function setClass(className) {
            this.$el.dialog({ dialogClass: className }).dialogExtend();
        }), _defineProperty(_Backbone$View$extend, 'perfomEffect', function perfomEffect(effect, options, speed) {
            this.$el.parent().effect(effect, options, speed);
        }), _defineProperty(_Backbone$View$extend, 'shake', function shake(options, speed) {
            if (options === undefined) {
                options = { distance: 5, times: 3 };
            }
            if (speed === undefined) {
                speed = 500;
            }

            this.$el.parent().effect('shake', options, speed);
        }), _defineProperty(_Backbone$View$extend, 'render', function render() {
            var _$$dialog$dialogExten;

            var that = this;

            //create the dialog window for the widget
            this.dialog = $("<div id=" + this.id + " class='dialog' title='" + this.name + " Widget'></div>").dialog({
                resizable: true,
                draggable: true,
                top: 10,
                height: 300,
                width: 350,
                closeOnEscape: false,
                close: function close(event, ui) {
                    if (event.originalEvent && $(event.originalEvent.target).closest(".ui-dialog-titlebar-close").length) {
                        that.destroy();
                    }
                }
            }).dialogExtend((_$$dialog$dialogExten = {
                "closable": true,
                "maximizable": true,
                "minimizable": true,
                "collapsable": true,
                "restore": true,
                "minimizeLocation": "right",
                "icons": {
                    "maximize": "fa fa-expand",
                    "minimize": "fa fa-window-minimize",
                    "collapse": "fa  fa-chevron-circle-up",
                    "restore": "fa fa-compress"
                },
                "load": function load(evt, dlg) {
                    var icons = $("#" + that.id).parent().find(".ui-icon");
                    for (var i = 0; i < icons.length; i++) {
                        //remove text from span added by vendor library
                        $(icons[i]).text("");
                    }
                },
                "beforeMinimize": function beforeMinimize(evt, dlg) {
                    var label = that.name;
                    if (label != undefined) {
                        label = label.substring(0, 6);
                    }
                    that.$el.dialog({ title: label });
                },
                "beforeMaximize": function beforeMaximize(evt, dlg) {
                    var divheight = that.size.height;
                    var divwidth = that.size.width;
                    that.previousMaxSize = { width: divwidth, height: divheight };
                },
                "minimize": function minimize(evt, dlg) {
                    that.$el.dialog({ title: that.name });
                    $(".ui-dialog-titlebar-restore span").removeClass("fa-chevron-circle-down");
                    $(".ui-dialog-titlebar-restore span").removeClass("fa-compress");
                    $(".ui-dialog-titlebar-restore span").addClass("fa-window-restore");
                    that.$el.parent().css("z-index", zIndex.min);
                },
                "maximize": function maximize(evt, dlg) {
                    that.setTransparentBackground(false);
                    $(this).trigger('resizeEnd');
                    var divheight = $(window).height();
                    var divwidth = $(window).width();
                    that.$el.dialog({ height: divheight, width: divwidth });
                    $(".ui-dialog-titlebar-restore span").removeClass("fa-chevron-circle-down");
                    $(".ui-dialog-titlebar-restore span").removeClass("fa-window-restore");
                    $(".ui-dialog-titlebar-restore span").addClass("fa-compress");
                    that.maximize = true;
                    that.$el.parent().css("z-index", zIndex.max);
                    that.size = {
                        height: divheight,
                        width: divwidth
                    };
                }
            }, _defineProperty(_$$dialog$dialogExten, 'restore', function restore(evt, dlg) {
                if (that.maximize) {
                    that.setSize(that.previousMaxSize.height, that.previousMaxSize.width);
                    $(this).trigger('restored', [that.id]);
                }
                that.setTransparentBackground(that.previousMaxTransparency);
                $(this).trigger('resizeEnd');
                that.maximize = false;
                that.collapsed = false;
                that.$el.parent().css("z-index", zIndex.restore);
            }), _defineProperty(_$$dialog$dialogExten, "collapse", function collapse(evt, dlg) {
                $(".ui-dialog-titlebar-restore span").removeClass("fa-compress");
                $(".ui-dialog-titlebar-restore span").removeClass("fa-window-restore");
                $(".ui-dialog-titlebar-restore span").addClass("fa-chevron-circle-down");
                that.collapsed = true;
                that.$el.parent().css("z-index", zIndex.min);
            }), _$$dialog$dialogExten));

            this.$el = $("#" + this.id);
            this.dialogParent = this.$el.parent();

            //add history
            this.showHistoryIcon(true);

            //remove the jQuery UI icon
            this.dialogParent.find("button.ui-dialog-titlebar-close").html("");
            this.dialogParent.find("button").append("<i class='fa fa-close'></i>");

            //Take focus away from close button
            this.dialogParent.find("button.ui-dialog-titlebar-close").blur();

            //add help button
            this.showHelpIcon(true);
        }), _defineProperty(_Backbone$View$extend, 'registerEvent', function registerEvent(event, callback) {
            this.registeredEvents.push({ id: event, callback: callback });
        }), _defineProperty(_Backbone$View$extend, 'unregisterEvent', function unregisterEvent(event) {
            this.registeredEvents = _.reject(this.registeredEvents, function (el) {
                return el.id === event;
            });
        }), _defineProperty(_Backbone$View$extend, 'setHelpInfo', function setHelpInfo(helpInfo) {
            this.helpInfo = helpInfo;
        }), _defineProperty(_Backbone$View$extend, 'getHelp', function getHelp() {
            return this.helpInfo;
        }), _defineProperty(_Backbone$View$extend, 'setController', function setController(controller) {
            this.controller = controller;
        }), _defineProperty(_Backbone$View$extend, 'showHelpIcon', function showHelpIcon(show) {
            var that = this;
            if (show && this.$el.parent().find(".history-icon").length == 0) {
                this.addButtonToTitleBar($("<div class='fa fa-question help-icon' title='Widget Help'></div>").click(function () {
                    GEPPETTO.ComponentFactory.addComponent('MDMODAL', {
                        title: that.id.slice(0, -1) + ' help',
                        content: that.getHelp(),
                        show: true
                    }, document.getElementById("modal-region"));
                }));
            } else {
                this.$el.parent().find(".help-icon").remove();
            }
        }), _defineProperty(_Backbone$View$extend, 'showHistoryIcon', function showHistoryIcon(show) {
            var that = this;
            if (show && this.$el.parent().find(".history-icon").length == 0) {
                this.addButtonToTitleBar($("<div class='fa fa-history history-icon' title='Show Navigation History'></div>").click(function (event) {
                    that.showHistoryMenu(event);
                    event.stopPropagation();
                }));
            } else {
                this.$el.parent().find(".history-icon").remove();
            }
        }), _defineProperty(_Backbone$View$extend, 'getView', function getView() {
            // get default stuff such as id, position and size
            return {
                widgetType: this.widgetType,
                isWidget: this.isWidget(),
                showTitleBar: this.hasTitleBar,
                showHistoryNavigationBar: this.hasHistoryNavigationBar,
                transparentBackground: this.transparentBackground,
                name: this.name,
                size: {
                    height: this.size.height,
                    width: this.size.width
                },
                position: {
                    left: this.position.left,
                    top: this.position.top
                }
            };
        }), _defineProperty(_Backbone$View$extend, 'setView', function setView(view) {
            // set default stuff such as position and size
            if (view.size != undefined && view.size.height != 0 && view.size.width != 0) {
                this.setSize(view.size.height, view.size.width);
            } else {
                // trigger auto size if we have no size info
                this.setAutoWidth();
                this.setAutoHeight();
            }

            if (view.position != undefined) {
                this.setPosition(view.position.left, view.position.top);
            }

            if (view.name != undefined) {
                this.setName(view.name);
            }

            if (view.showTitleBar != undefined) {
                this.showTitleBar(view.showTitleBar);
            }

            if (view.showHistoryNavigationBar != undefined) {
                this.showHistoryNavigationBar(view.showHistoryNavigationBar);
            }

            if (view.transparentBackground != undefined) {
                this.setTransparentBackground(view.transparentBackground);
            }

            // after setting view through setView, reset dirty flag
            this.dirtyView = false;
        }), _defineProperty(_Backbone$View$extend, 'isStateLess', function isStateLess() {
            return this.stateless;
        }), _defineProperty(_Backbone$View$extend, 'isWidget', function isWidget() {
            return true;
        }), _Backbone$View$extend))
    };
}.call(exports, __webpack_require__, exports, module),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ 3364:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_RESULT__;
/**
 * Tree Visualiser Widget
 *
 * @module Widgets/TreeVisualizerDAT
 * @author Adrian Quintana (adrian.perez@ucl.ac.uk)
 */

!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require) {

    var TreeVisualiser = __webpack_require__(3365);
    __webpack_require__(3369);
    var dat = __webpack_require__(3371);
    var $ = __webpack_require__(16);

    // Icons to display on hover
    var aIcons = $("<a id='tvIcons'><icon class='fa fa-sign-in'/></a>");
    // div to verify if textfield should be change to textarea
    var testingSizeElement = $('<div></div>').css({ 'position': 'absolute', 'float': 'left', 'white-space': 'nowrap', 'visibility': 'hidden' }).appendTo($('body'));

    return TreeVisualiser.TreeVisualiser.extend({

        /**
         * Initializes the TreeVisualiserDAT given a set of options
         *
         * @param {Object} options - Object with options for the TreeVisualiserDAT widget
         */
        initialize: function initialize(options) {
            TreeVisualiser.TreeVisualiser.prototype.initialize.call(this, options);

            // Initialise default options
            this.options = { width: "auto", autoPlace: false, expandNodes: false };

            //This function allows to access a node by its data attribute (this function is required is the data property has been added by jquery)
            $.fn.filterByData = function (prop, val) {
                return this.filter(function () {
                    return $(this).data(prop) == val;
                });
            };
            this.initDATGUI();
        },

        /**
         * Action events associated with this widget
         */
        events: {
            'contextmenu .title': 'manageRightClickEvent',
            'contextmenu .cr.string': 'manageRightClickEvent',
            'contextmenu .cr.number': 'manageRightClickEvent',
            'click .title': 'manageLeftClickEvent',
            'click .cr.string': 'manageLeftClickEvent',
            'click .cr.number': 'manageLeftClickEvent',
            'mouseenter .title': 'manageHover',
            'mouseenter .cr.string': 'manageHover',
            'mouseenter .cr.number': 'manageHover',
            'mouseleave .title': 'manageUnhover',
            'mouseleave .cr.string': 'manageUnhover',
            'mouseleave .cr.number': 'manageUnhover'

        },

        getTriggeredElement: function getTriggeredElement(event) {
            if ($(event.target).is('li')) {
                return $(event.target);
            } else {
                return $(event.target).closest('li');
            }
        },

        manageHover: function manageHover(event) {
            var liElement = this.getTriggeredElement(event);
            var nodeInstancePath = liElement.data("instancepath");
            if (nodeInstancePath != null || undefined) {
                var node = this.dataset.valueDict[nodeInstancePath]["model"];
                var that = this;
                aIcons.click(function (event) {
                    that.showContextMenu(event, node);event.stopPropagation();
                });
                liElement.prepend(aIcons);
            }
        },

        manageUnhover: function manageUnhover(event) {
            var liElement = this.getTriggeredElement(event);
            var nodeInstancePath = liElement.data("instancepath");
            aIcons.remove();
        },

        /**
         * Register right click event with widget
         *
         * @param {WIDGET_EVENT_TYPE} event - Handles right click event on widget
         */
        manageLeftClickEvent: function manageLeftClickEvent(event) {
            var liElement = this.getTriggeredElement(event);
            var nodeInstancePath = liElement.data("instancepath");

            if (nodeInstancePath != null || undefined) {
                //Read node from instancepath data property attached to dom element

                var node = this.dataset.valueDict[nodeInstancePath]["model"];
                if (node.getMetaType() == GEPPETTO.Resources.VARIABLE_NODE && node.getWrappedObj().getType().getMetaType() == GEPPETTO.Resources.POINTER_TYPE) {
                    GEPPETTO.CommandController.execute("G.addWidget(Widgets.TREEVISUALISERDAT).setData(" + node.getPath() + ")");
                } else {
                    this.dataset.isDisplayed = false;
                    if (node.getChildren().length == 0 && node.getHiddenChildren().length > 0) {
                        node.set({ "children": node.getHiddenChildren() });
                        for (var childIndex in node.getChildren()) {
                            var nodeChild = node.getChildren()[childIndex];
                            if (nodeChild.getChildren().length > 0) {
                                nodeChild.set({ "_children": nodeChild.getChildren() });
                            }
                            nodeChild.set({ "children": [] });
                            this.prepareTree(this.dataset.valueDict[nodeInstancePath]["folder"], nodeChild, 0);
                        }

                        this.customiseLayout(this.dataset.valueDict[nodeInstancePath]["folder"].domElement);
                    }
                    this.dataset.isDisplayed = true;
                }
            }
        },

        /**
         * Register right click event with widget
         *
         * @param {WIDGET_EVENT_TYPE} event - Handles right click event on widget
         */
        manageRightClickEvent: function manageRightClickEvent(event) {
            var liElement = this.getTriggeredElement(event);
            var nodeInstancePath = liElement.data("instancepath");
            if (nodeInstancePath != null || undefined) {
                var node = this.dataset.valueDict[nodeInstancePath]["model"];

                //Read node from instancepath data property attached to dom element
                this.showContextMenu(event, node);
            }
        },

        /**
         * Sets the data used inside the TreeVisualiserDAT for rendering.
         *
         * @param {Array} state - Array of variables used to display inside TreeVisualiserDAT
         * @param {Object} options - Set of options passed to widget to customise it
         */
        setData: function setData(state, options) {
            if (state == undefined) {
                return "Data can not be added to " + this.name + ". Data does not exist in current experiment.";
            }
            labelsInTV = {};

            // If data is an array, let's iterate and call setdata
            if (state instanceof Array) {
                var that = this;
                $.each(state, function (d) {
                    that.setData(state[d], options);
                });
            } else {
                //Call setData for parent class (TreeVisualiser)
                var currentDataset = TreeVisualiser.TreeVisualiser.prototype.setData.call(this, state, options);

                //Initialise nodes
                this.initialiseGUIElements(currentDataset);
            }

            return this;
        },

        initialiseGUIElements: function initialiseGUIElements(currentDataset) {
            //Add to data variable
            this.dataset.data.push(currentDataset);

            //Generate DAT nodes
            this.dataset.isDisplayed = false;
            this.prepareTree(this.gui, currentDataset, 0);
            this.dataset.isDisplayed = true;

            // Customise layout: make text field non-editable, convert text field into text area...
            this.customiseLayout($(this.dialog));
        },

        customiseLayout: function customiseLayout(folder) {
            //Disable input elements
            $(folder).find("input").prop('disabled', true);

            //Change textfield to textarea if it is too big
            $(folder).find('.texttypetv').find('div > div > input[type="text"]').each(function () {
                testingSizeElement.text($(this).val());
                if (testingSizeElement.width() > $(this).width()) {
                    $(this).closest('.texttypetv').addClass('textarea');
                    var textarea = $(document.createElement('textarea')).attr('readonly', true).attr('rows', 2);
                    textarea.val($(this).val());
                    $(this).replaceWith(textarea);
                }
            });
        },

        /**
         * Prepares the tree for painting it on the widget
         *
         * @param {Object} parent - Parent tree to paint
         * @param {Array} data - Data to paint
         */
        prepareTree: function prepareTree(parent, data, step) {

            if ('labelName' in this.options) {
                // We need to verify if this is working
                label = data.getWrappedObj().get(this.options.labelName);
            } else {
                label = data.getName();
            }

            var children = data.getChildren();
            var _children = data.getHiddenChildren();

            if (!this.dataset.isDisplayed) {

                //Ugly hack: DAT doesn't allow nodes with the same name
                var isDuplicated = true;
                while (isDuplicated) {
                    isDuplicated = false;
                    for (var key in labelsInTV) {
                        if (labelsInTV[key] == label) {
                            label = label + " ";
                            isDuplicated = true;
                            break;
                        }
                    }
                }
                labelsInTV[data.getPath()] = label;

                if (children.length > 0 || _children.length > 0) {
                    this.dataset.valueDict[data.getPath()] = new function () {}();
                    this.dataset.valueDict[data.getPath()]["folder"] = parent.addFolder(labelsInTV[data.getPath()]);

                    //Add class to dom element depending on node metatype
                    $(this.dataset.valueDict[data.getPath()]["folder"].domElement).find("li").addClass(data.getStyle());
                    //Add instancepath as data attribute. This attribute will be used in the event framework
                    $(this.dataset.valueDict[data.getPath()]["folder"].domElement).find("li").data("instancepath", data.getPath());

                    var parentFolderTmp = this.dataset.valueDict[data.getPath()]["folder"];
                    for (var childIndex in children) {
                        if (!this.dataset.isDisplayed || this.dataset.isDisplayed && children[childIndex].name != "ModelTree") {
                            this.prepareTree(parentFolderTmp, children[childIndex], step);
                        }
                    }

                    if (data.getBackgroundColors().length > 0) {
                        $(this.dataset.valueDict[data.getPath()]["folder"].domElement).find("li").append($('<a id="backgroundSections">').css({ "z-index": 1, "float": "right", "width": "60%", "height": "90%", "color": "black", "position": "absolute", "top": 0, "right": 0 }));
                        for (var index in data.getBackgroundColors()) {
                            var color = data.getBackgroundColors()[index].replace("0X", "#");
                            $(this.dataset.valueDict[data.getPath()]["folder"].domElement).find("li").find('#backgroundSections').append($('<span>').css({ "float": "left", "width": 100 / data.getBackgroundColors().length + "%", "background-color": color, "height": "90%" }).html("&nbsp"));
                        }
                    }

                    if (data.getValue().length > 0) {
                        $(this.dataset.valueDict[data.getPath()]["folder"].domElement).find("li").css({ "position": "relative" });
                        $(this.dataset.valueDict[data.getPath()]["folder"].domElement).find("li").append($('<a id="contentSections">').css({ "z-index": 2, "text-align": "center", "float": "right", "width": "60%", "height": "90%", "color": "black", "position": "absolute", "top": 0, "right": 0 }));
                        for (var index in data.getValue()) {
                            $(this.dataset.valueDict[data.getPath()]["folder"].domElement).find("li").find('#contentSections').append($('<span>').css({ "float": "left", "width": 100 / data.getBackgroundColors().length + "%", "height": "90%" }).html(data.getValue()[index]));
                        }
                    }
                } else {
                    this.dataset.valueDict[data.getPath()] = new function () {}();
                    this.dataset.valueDict[data.getPath()][labelsInTV[data.getPath()]] = data.getValue();
                    this.dataset.valueDict[data.getPath()]["controller"] = parent.add(this.dataset.valueDict[data.getPath()], labelsInTV[data.getPath()]).listen();

                    //Add class to dom element depending on node metatype
                    $(this.dataset.valueDict[data.getPath()]["controller"].__li).addClass(data.getStyle());
                    //Add instancepath as data attribute. This attribute will be used in the event framework
                    $(this.dataset.valueDict[data.getPath()]["controller"].__li).data("instancepath", data.getPath());

                    // Execute set value if it is a parameter specification
                    if (data.getMetaType() == GEPPETTO.Resources.PARAMETER_TYPE) {
                        $(dataset.valueDict[data.getPath()]["controller"].__li).find('div > div > input[type="text"]').change(function () {
                            GEPPETTO.CommandController.execute(data.getPath() + ".setValue(" + $(this).val().split(" ")[0] + ")");
                        });
                    }

                    if (data.getBackgroundColors().length > 0) {
                        var color = data.getBackgroundColors()[0].replace("0X", "#");
                        $(this.dataset.valueDict[data.getPath()]["controller"].__li).find(".c").css({ "background-color": color, "height": "90%" });
                    }
                }

                if (this.options.expandNodes) {
                    parent.open();
                }
                this.dataset.valueDict[data.getPath()]["model"] = data;
            } else {
                if (children.length > 0 || _children.length > 0) {
                    for (var childIndex in children) {
                        this.prepareTree(parent, children[childIndex], step);
                    }
                } else if (data.getMetaType() == GEPPETTO.Resources.INSTANCE_NODE) {
                    var set = this.dataset.valueDict[data.getPath()]["controller"].__gui;
                    if (!set.__ul.closed) {
                        this.dataset.valueDict[data.getPath()][labelsInTV[data.getPath()]] = this.treeVisualiserController.getFormattedValue(data.getWrappedObj(), data.getWrappedObj().capabilities[0], step);
                    }
                }
            }
        },

        /**
         * Updates the data that the TreeVisualiserDAT is rendering
         */
        updateData: function updateData(step) {
            for (var i = 0; i < this.dataset.data.length; i++) {
                this.prepareTree(this.gui, this.dataset.data[i], step);
            }
        },

        /**
         * Clear Widget
         */
        reset: function reset() {
            this.dataset = { data: [], isDisplayed: false, valueDict: {} };
            $(this.dialog).children().remove();
            this.initDATGUI();
        },

        /**
         * Refresh data in tree visualiser
         */
        refresh: function refresh() {
            var currentDatasets = this.dataset.data;
            this.reset();
            for (var i = 0; i < currentDatasets.length; i++) {
                this.initialiseGUIElements(currentDatasets[i]);
            }
        },

        /**
         * Initialising GUI with default values
         */
        initDATGUI: function initDATGUI() {
            this.gui = new dat.GUI({
                width: this.options.width,
                autoPlace: this.options.autoPlace
            });

            this.dialog.append(this.gui.domElement);
        }

    });
}.call(exports, __webpack_require__, exports, module),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ 3365:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_RESULT__;/**
 * Tree Visualiser Widget
 *
 * @author Adrian Quintana (adrian.perez@ucl.ac.uk)
 */
!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require) {

    var Widget = __webpack_require__(2272);
    var TreeVisualiserController = __webpack_require__(3366);

    return {
        TreeVisualiser: Widget.View.extend({

            treeVisualiserController: null,

            initialize: function initialize(options) {
                Widget.View.prototype.initialize.call(this, options);

                this.dataset = { data: [], isDisplayed: false, valueDict: {} };
                this.visible = options.visible;
                this.render();
                this.setSize(options.width, options.height);
            },

            setData: function setData(state, options, dataset) {
                // If no options specify by user, use default options
                if (options != null) {
                    $.extend(this.options, options);
                }

                if (state != null) {
                    this.treeVisualiserController = new TreeVisualiserController(this.options);
                    return this.treeVisualiserController.convertNodeToTreeVisualiserNode(state);
                }
                return null;
            },

            getDatasets: function getDatasets() {
                return this.datasets;
            }

        })
    };
}.call(exports, __webpack_require__, exports, module),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ 3366:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_RESULT__;
/**
 * Tree Visualiser Widget
 *
 * @author Adrian Quintana (adrian.perez@ucl.ac.uk)
 */
!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require) {

    var TreeVisualiserNode = __webpack_require__(3367);
    var TreeVisualiserWrappedObject = __webpack_require__(3368);

    return Backbone.Model.extend({
        expandNodes: false,

        initialize: function initialize(options) {
            this.expandNodes = options.expandNodes;
            this.filterTypes = options.filterTypes;
        },

        /**
            * Create formatted value for any kind of node
            */
        getFormattedValue: function getFormattedValue(node, type, step) {
            var formattedValue = "";
            switch (type) {
                case GEPPETTO.Resources.PARAMETER_TYPE:
                case GEPPETTO.Resources.STATE_VARIABLE_TYPE:
                    formattedValue = node.getInitialValues()[0].value.value + " " + node.getInitialValues()[0].value.unit.unit;
                    break;
                case GEPPETTO.Resources.VISUAL_GROUP_ELEMENT_NODE:
                    formattedValue = node.getValue() != null ? node.getValue() + " " + node.getUnit() : "";
                    break;
                case GEPPETTO.Resources.VISUAL_GROUP_NODE:
                    formattedValue = [];
                    if (node.getMinDensity() != undefined) {
                        formattedValue.push(Math.floor(node.getMinDensity() * 1000) / 1000);
                    }
                    if (node.getMaxDensity() != undefined && node.getMinDensity() != node.getMaxDensity()) {
                        formattedValue.push(Math.floor(node.getMaxDensity() * 1000) / 1000);
                    }
                    break;
                case GEPPETTO.Resources.DYNAMICS_TYPE:
                    formattedValue = node.getInitialValues()[0].value.dynamics.expression.expression;
                    break;
                //            		case GEPPETTO.Resources.FUNCTION_TYPE:
                //            			formattedValue = "";
                //            			break;
                case GEPPETTO.Resources.TEXT_TYPE:
                    formattedValue = node.getInitialValues()[0].value.text;
                    break;
                case GEPPETTO.Resources.POINTER_TYPE:
                    //AQP: Add sth! A button?
                    formattedValue = "> " + node.getInitialValues()[0].getElements()[0].getType().getName();
                    break;
                case GEPPETTO.Resources.STATE_VARIABLE_CAPABILITY:
                    if (node.getTimeSeries() != null && node.getTimeSeries().length > 0) formattedValue = node.getTimeSeries()[step] + " " + (node.getUnit() != null && node.getUnit() != "null" ? " " + node.getUnit() : "");
                    break;
                case GEPPETTO.Resources.VISUAL_CAPABILITY:
                    formattedValue = "";
                    break;
                case GEPPETTO.Resources.PARAMETER_CAPABILITY:
                    formattedValue = "";
                    break;
                case GEPPETTO.Resources.CONNECTION_CAPABILITY:
                    formattedValue = "";
                    break;
                case GEPPETTO.Resources.IMPORT_TYPE:
                    //AQP: Add sth! A button?
                    formattedValue = "> Type not yet resolved";
                    break;
                default:
                    throw "Unknown type";
            }
            return formattedValue;
        },

        /**
            * Generate style depending on kind of node
            */
        getStyle: function getStyle(type) {
            var formattedValue = "";
            switch (type) {
                case GEPPETTO.Resources.PARAMETER_TYPE:
                    return "parametertypetv";
                case GEPPETTO.Resources.STATE_VARIABLE_TYPE:
                    return "statevariabletypetv";
                //            		case GEPPETTO.Resources.CONNECTION_TYPE:
                //            			return null;
                case GEPPETTO.Resources.DYNAMICS_TYPE:
                    return "dynamicstypetv";
                case GEPPETTO.Resources.FUNCTION_TYPE:
                    return "functiontypetv";
                case GEPPETTO.Resources.TEXT_TYPE:
                    return "texttypetv";
                case GEPPETTO.Resources.POINTER_TYPE:
                    return "pointertypetv";
                case GEPPETTO.Resources.STATE_VARIABLE_CAPABILITY:
                    return "stateinstancetv";
                case GEPPETTO.Resources.VISUAL_CAPABILITY:
                    //AQP: currently no css for this
                    return "visualinstancetv";
                case GEPPETTO.Resources.PARAMETER_CAPABILITY:
                    //AQP: currently no css for this
                    return "parameterinstancetv";
                case GEPPETTO.Resources.CONNECTION_CAPABILITY:
                    //AQP: currently no css for this
                    return "connectioninstancetv";
                case GEPPETTO.Resources.COMPOSITE_TYPE_NODE:
                    return "foldertv";
                case GEPPETTO.Resources.ARRAY_INSTANCE_NODE:
                    return "arrayinstancetv";
                case GEPPETTO.Resources.INSTANCE_NODE:
                    return "instancefoldertv";
                case GEPPETTO.Resources.ARRAY_TYPE_NODE:
                    return "arraytypetv";
                case GEPPETTO.Resources.VISUAL_GROUP_ELEMENT_NODE:
                    return "visualgroupelementtv";

            }
            return null;
        },

        /**
         * Create visualisation subtree (visual groups and visual elements) 
         */
        createVisualisationSubTree: function createVisualisationSubTree(compositeVisualType) {
            var tagsNode = {};
            var children = [];
            if (compositeVisualType.getVisualGroups() != undefined) {
                for (var i = 0; i < compositeVisualType.getVisualGroups().length; i++) {
                    var visualGroup = compositeVisualType.getVisualGroups()[i];

                    //Create Visual Group Elements for Visual Group
                    var nodeChildren = [];
                    for (var j = 0; j < visualGroup.getVisualGroupElements().length; j++) {
                        var visualGroupElement = visualGroup.getVisualGroupElements()[j];

                        var nodeChild = this.createTreeVisualiserNode({ wrappedObj: visualGroupElement, formattedValue: this.getFormattedValue(visualGroupElement, visualGroupElement.getMetaType()),
                            style: this.getStyle(visualGroupElement.getMetaType()) });

                        if (visualGroupElement.getColor() != undefined) {
                            nodeChild.set({ "backgroundColors": [visualGroupElement.getColor()] });
                        }

                        nodeChildren.push(nodeChild);
                    }

                    //Create Visual Group and background colors if needed
                    var node = this.createTreeVisualiserNode({ wrappedObj: visualGroup, _children: nodeChildren, style: this.getStyle(visualGroup.getMetaType()), formattedValue: this.getFormattedValue(visualGroup, visualGroup.getMetaType()) });
                    var backgroundColors = [];
                    if (visualGroup.getLowSpectrumColor() != undefined) {
                        backgroundColors.push(visualGroup.getLowSpectrumColor());
                    }
                    if (visualGroup.getHighSpectrumColor() != undefined && visualGroup.getMaxDensity() != undefined && visualGroup.getMinDensity() != visualGroup.getMaxDensity()) {
                        backgroundColors.push(visualGroup.getHighSpectrumColor());
                    }
                    if (backgroundColors.length > 0) {
                        node.set({ "backgroundColors": backgroundColors });
                    }

                    // Add to tags folder
                    if (visualGroup.getTags().length > 0) {
                        for (var j = 0; j < visualGroup.getTags().length; j++) {
                            var tag = visualGroup.getTags()[j];
                            if (!(tag in tagsNode)) {
                                var treeVisualiserWrappedObject = new TreeVisualiserWrappedObject({
                                    name: tag,
                                    id: tag,
                                    _metaType: "",
                                    path: visualGroup.getPath() + "." + tag
                                });
                                //AQP: style?
                                tagsNode[tag] = this.createTreeVisualiserNode({ wrappedObj: treeVisualiserWrappedObject, _children: [] });
                                children.push(tagsNode[tag]);
                            }
                            tagsNode[tag].getHiddenChildren().push(node);
                        }
                    } else {
                        children.push(node);
                    }
                }
            }
            return children;
        },

        /**
         * Create tree visualiser node 
         */
        createTreeVisualiserNode: function createTreeVisualiserNode(options) {
            if (this.expandNodes) {
                options["children"] = options._children;
                options._children = [];
            }
            return new TreeVisualiserNode(options);
        },

        /**
         * Generate tree visualiser node from geppetto node 
         */
        convertNodeToTreeVisualiserNode: function convertNodeToTreeVisualiserNode(node) {

            if (node.getMetaType() == GEPPETTO.Resources.VARIABLE_NODE && node.getType().getMetaType() != GEPPETTO.Resources.HTML_TYPE) {
                if (node.getType().getMetaType() == GEPPETTO.Resources.COMPOSITE_TYPE_NODE || node.getType().getMetaType() == GEPPETTO.Resources.ARRAY_TYPE_NODE) {
                    if (node.getType().getSuperType() != undefined && !(node.getType().getSuperType() instanceof Array) && node.getType().getSuperType().getId() == 'projection') {
                        var projectionChildren = node.getType().getChildren();
                        var numConnections = 0;
                        var projectionsChildrenNode = [];
                        for (var j = 0; j < projectionChildren.length; j++) {
                            if (projectionChildren[j].getTypes()[0].getSuperType() != undefined && projectionChildren[j].getTypes()[0].getSuperType().getId() == 'connection') {
                                numConnections++;
                            } else {
                                projectionsChildrenNode.push(this.convertNodeToTreeVisualiserNode(projectionChildren[j]));
                            }
                        }

                        var treeVisualiserWrappedObject = new TreeVisualiserWrappedObject({ name: "Number of Connections", id: "numberConnections", _metaType: "", path: node.getType().getPath() + ".numberConnections" });
                        projectionsChildrenNode.push(this.createTreeVisualiserNode({ wrappedObj: treeVisualiserWrappedObject, formattedValue: numConnections, style: this.getStyle(GEPPETTO.Resources.TEXT_TYPE) }));

                        return this.createTreeVisualiserNode({ wrappedObj: node.getType(), _children: projectionsChildrenNode, style: this.getStyle(node.getType().getMetaType()) });
                    } else {
                        return this.createTreeVisualiserNode({ wrappedObj: node, style: this.getStyle(node.getType().getMetaType()), _children: this.createTreeVisualiserNodeChildren(node.getType()) });
                    }
                } else {
                    if (this.filterTypes == undefined || this.filterTypes.indexOf(node.getType().getMetaType()) == -1) {
                        return this.createTreeVisualiserNode({ wrappedObj: node, formattedValue: this.getFormattedValue(node, node.getType().getMetaType()), style: this.getStyle(node.getType().getMetaType()) });
                    }
                    return null;
                }
            } else if (node.getMetaType() == GEPPETTO.Resources.INSTANCE_NODE || node.getMetaType() == GEPPETTO.Resources.ARRAY_INSTANCE_NODE) {
                var formattedValue = undefined;
                var style = this.getStyle(node.getMetaType());
                //AQP: Do we want to do sth with every single capability?
                if (node.capabilities != undefined && node.capabilities.length > 0) {
                    formattedValue = this.getFormattedValue(node, node.capabilities[0], 0);
                    style = this.getStyle(node.capabilities[0]);
                }
                return this.createTreeVisualiserNode({ wrappedObj: node, formattedValue: formattedValue, style: style, _children: this.createTreeVisualiserNodeChildren(node) });
            } else if (node.getMetaType() != GEPPETTO.Resources.VARIABLE_NODE && node.getMetaType() != GEPPETTO.Resources.HTML_TYPE) {
                return this.createTreeVisualiserNode({ wrappedObj: node, _children: this.createTreeVisualiserNodeChildren(node), style: this.getStyle(node.getMetaType()) });
            }
        },

        /**
         * Create tree visualiser nodes for geppetto node children 
         */
        createTreeVisualiserNodeChildren: function createTreeVisualiserNodeChildren(state) {
            var children = [];
            if (state.getMetaType() == GEPPETTO.Resources.COMPOSITE_TYPE_NODE || state.getMetaType() == GEPPETTO.Resources.INSTANCE_NODE || state.getMetaType() == GEPPETTO.Resources.ARRAY_ELEMENT_INSTANCE_NODE) {
                var numberCompartments = 0;
                for (var i = 0; i < state.getChildren().length; i++) {
                    var child = state.getChildren()[i];
                    if (child.getType() != undefined && child.getType().getId() == 'compartment') {
                        numberCompartments++;
                    } else {
                        var node = this.convertNodeToTreeVisualiserNode(child);
                        if (node != undefined) children.push(node);
                    }
                }
                if (numberCompartments > 0) {
                    var treeVisualiserWrappedObject = new TreeVisualiserWrappedObject({ "name": "Number of Compartments", "id": "numberCompartments", "_metaType": "", "path": state.getPath() + ".numberCompartments" });
                    children.push(this.createTreeVisualiserNode({ wrappedObj: treeVisualiserWrappedObject, formattedValue: numberCompartments, style: this.getStyle(GEPPETTO.Resources.TEXT_TYPE) }));
                }

                if (state.getVisualType() != null) {
                    children.push(this.createTreeVisualiserNode({ wrappedObj: state.getVisualType(), _children: this.createTreeVisualiserNodeChildren(state.getVisualType()) }));
                }
            } else if (state.getMetaType() == GEPPETTO.Resources.COMPOSITE_VISUAL_TYPE_NODE) {
                children = this.createVisualisationSubTree(state);
            } else if (state.getMetaType() == GEPPETTO.Resources.ARRAY_INSTANCE_NODE) {
                for (var i = 0; i < state.getChildren().length; i++) {
                    var child = state.getChildren()[i];
                    children.push(this.createTreeVisualiserNode({ wrappedObj: child, formattedValue: "", style: "", _children: this.createTreeVisualiserNodeChildren(child) }));
                }
            } else if (state.getMetaType() == GEPPETTO.Resources.ARRAY_TYPE_NODE) {
                // Size
                var treeVisualiserWrappedObject = new TreeVisualiserWrappedObject({ "name": "Size", "id": "size", "_metaType": "", "path": state.getPath() + ".size" });
                children.push(this.createTreeVisualiserNode({ wrappedObj: treeVisualiserWrappedObject, formattedValue: state.getSize(), style: this.getStyle(GEPPETTO.Resources.TEXT_TYPE) }));

                //Extracting Cell
                children.push(this.createTreeVisualiserNode({ wrappedObj: state.getType(), style: this.getStyle(state.getType().getMetaType()), _children: this.createTreeVisualiserNodeChildren(state.getType()) }));
            } else if (state.getMetaType() == GEPPETTO.Resources.VARIABLE_NODE) {
                var node = this.convertNodeToTreeVisualiserNode(state);
                if (node != undefined) children.push(node);
            }

            return children;
        }
    });
}.call(exports, __webpack_require__, exports, module),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ 3367:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_ARRAY__, __WEBPACK_AMD_DEFINE_RESULT__;/**
 * Base class that provides wrapping functionality for a generic underlying object (with id and name).
 *
 * @module widgets/treevisualiser/TreeVisualiserNode.js
 * @author Adrian Quintana (adrian.perez@ucl.ac.uk)
 */

!(__WEBPACK_AMD_DEFINE_ARRAY__ = [__webpack_require__(16), __webpack_require__(29), __webpack_require__(94)], __WEBPACK_AMD_DEFINE_RESULT__ = function (require) {
  return Backbone.Model.extend({
    wrappedObj: null,
    children: [],
    _children: [],
    formattedValue: "",
    style: "",
    backgroundColors: [],

    /**
     * Initializes this node with passed attributes
     *
     * @param {Object} options - Object with options attributes to initialize node
     */
    initialize: function initialize(options) {
      this.set({ "wrappedObj": options.wrappedObj });
      this.set({ "children": options.children != undefined ? options.children : [] });
      this.set({ "_children": options._children != undefined ? options._children : [] });
      this.set({ "formattedValue": options.formattedValue != undefined ? options.formattedValue : "" });
      this.set({ "style": options.style != undefined ? options.style : "" });
      this.set({ "backgroundColors": options.backgroundColors != undefined ? options.backgroundColors : [] });
    },

    /**
     * Gets the name of the node
     *
     * @command Node.getName()
     * @returns {String} Name of the node
     *
     */
    getName: function getName() {
      return this.get('wrappedObj').getName();
    },

    /**
     * Get the id associated with node
     *
     * @command Node.getId()
     * @returns {String} ID of node
     */
    getId: function getId() {
      return this.get('wrappedObj').getId();
    },

    /**
     * Get the metatype associated with node
     *
     * @command Node.getMetaType()
     * @returns {String} MetaType of node
     */
    getMetaType: function getMetaType() {
      return this.get('wrappedObj').getMetaType();
    },

    /**
     * Get the metatype associated with node
     *
     * @command Node.getMetaType()
     * @returns {String} formatted value of node
     */
    getValue: function getValue() {
      return this.get('formattedValue');
    },

    /**
     * Get the children of the node
     *
     * @command Node.getChildren()
     * @returns {Object} Children of node
     */
    getChildren: function getChildren() {
      return this.get('children');
    },

    /**
     * Get the hidden children of the node
     *
     * @command Node.getHiddenChildren()
     * @returns {Object} Hidden children of node
     */
    getHiddenChildren: function getHiddenChildren() {
      return this.get('_children');
    },

    /**
     * Get the backgroundColors of the node
     *
     * @command Node.getBackgroundColors()
     * @returns {Object} Children of node
     */
    getBackgroundColors: function getBackgroundColors() {
      return this.get('backgroundColors');
    },

    /**
     * Get the wrapped object
     *
     * @command Node.getWrappedObj()
     * @returns {Object} - Wrapped object
     */
    getWrappedObj: function getWrappedObj() {
      return this.get('wrappedObj');
    },

    /**
     * Get the style of the node
     *
     * @command Node.getStyle()
     * @returns {String} - Wrapped object
     */
    getStyle: function getStyle() {
      return this.get('style');
    },

    /**
     * Get the unique path
     *
     * @command Node.getPath()
     * @returns {String} - Wrapped object
     */
    getPath: function getPath() {
      if (typeof this.get('wrappedObj').getInstancePath === "function") {
        return this.get('wrappedObj').getInstancePath();
      } else if (typeof this.get('wrappedObj').getPath === "function") {
        return this.get('wrappedObj').getPath();
      } else {
        return this.getId();
      }
    }

  });
}.apply(exports, __WEBPACK_AMD_DEFINE_ARRAY__),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ 3368:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_RESULT__;

/**
 * Client class use to represent a composite variable node, used for simulation
 * tree state variables.
 *
 * @author Jesus R. Martinez (jesus@metacell.us)
 * @author Adrian Quintana (adrian.perez@ucl.ac.uk)
 */
!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require) {

    return Backbone.Model.extend({
        children: [],
        id: "",
        name: "",
        _metaType: "",
        value: "",
        path: "",

        /**
         * Initializes this node with passed attributes
         *
         * @param {Object} options - Object with options attributes to initialize
         *                           node
         */
        initialize: function initialize(options) {
            this.set({ "children": options.children != 'undefined' ? options.children : [] });
            this.set({ "id": options.id });
            this.set({ "name": options.name });
            this.set({ "_metaType": options._metaType });
            this.set({ "value": options.value });
            this.set({ "path": options.path });
        },

        /**
         * Get this entity's aspects
         *
         * @command CompositeType.getChildren()
         *
         * @returns {List<Variable>} - List of variables
         *
         */
        getChildren: function getChildren() {
            return this.get('children');
        },

        /**
         * Get meta type
         *
         * @command Instance.getMetaType()
         *
         * @returns {String} - meta type
         *
         */
        getMetaType: function getMetaType() {
            return this.get('_metaType');
        },

        /**
         * Gets the name of the node
         *
         * @command Node.getName()
         * @returns {String} Name of the node
         *
         */
        getName: function getName() {
            return this.get('name');
        },

        /**
         * Get the id associated with node
         *
         * @command Node.getId()
         * @returns {String} ID of node
         */
        getId: function getId() {
            return this.get('id');
        },

        /**
         * Get the list of values for this variable
         *
         * @command Variable.getInitialValues()
         *
         * @returns {List<Value>} - array of values
         *
         */
        getInitialValues: function getInitialValues() {
            var values = [];
            values.push({ value: { value: this.get('value') } });
            return values;
        },

        getPath: function getPath() {
            return this.get('path');
        }
    });
}.call(exports, __webpack_require__, exports, module),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ }),

/***/ 3369:
/***/ (function(module, exports, __webpack_require__) {

// style-loader: Adds some css to the DOM by adding a <style> tag

// load the styles
var content = __webpack_require__(3370);
if(typeof content === 'string') content = [[module.i, content, '']];
// add the styles to the DOM
var update = __webpack_require__(18)(content, {});
if(content.locals) module.exports = content.locals;
// Hot Module Replacement
if(false) {
	// When the styles change, update the <style> tags
	if(!content.locals) {
		module.hot.accept("!!../../../../../node_modules/css-loader/index.js!../../../../../node_modules/less-loader/dist/cjs.js?{\"modifyVars\":{\"url\":\"'../../../extensions/geppetto-netpyne/css/colors'\"}}!./TreeVisualiserDAT.less", function() {
			var newContent = require("!!../../../../../node_modules/css-loader/index.js!../../../../../node_modules/less-loader/dist/cjs.js?{\"modifyVars\":{\"url\":\"'../../../extensions/geppetto-netpyne/css/colors'\"}}!./TreeVisualiserDAT.less");
			if(typeof newContent === 'string') newContent = [[module.id, newContent, '']];
			update(newContent);
		});
	}
	// When the module is disposed, remove the <style> tags
	module.hot.dispose(function() { update(); });
}

/***/ }),

/***/ 3370:
/***/ (function(module, exports, __webpack_require__) {

exports = module.exports = __webpack_require__(17)(undefined);
// imports


// module
exports.push([module.i, ".dark-orange {\n  color: #cc215a;\n}\n.orange {\n  color: #f23d7a;\n}\n.orange-color {\n  color: #f23d7a;\n}\n.orange-color-bg {\n  background-color: #f23d7a;\n}\ndiv[id^='TreeVisualiserDAT'] {\n  overflow-y: auto !important;\n  font-family: \"Helvetica Neue\", Helvetica, Arial, sans-serif !important;\n  font-weight: 200 !important;\n}\n.ui-widget-content .dg.main.taller-than-window .close-button {\n  border-top: 1px solid #ddd;\n}\n.ui-widget-content .dg.main .close-button {\n  background: rgba(255, 255, 255, 0);\n}\n.ui-widget-content .dg.main .close-button:hover {\n  background: rgba(33, 29, 29, 0.4);\n}\n.ui-widget-content .dg {\n  color: #e9e9e9;\n  text-shadow: none !important;\n}\n.ui-widget-content .dg.main::-webkit-scrollbar {\n  background: #fafafa;\n}\n.ui-widget-content .dg.main::-webkit-scrollbar-thumb {\n  background: #bbb;\n}\n.ui-widget-content .dg li:not(.folder) {\n  background: rgba(255, 255, 255, 0);\n}\n.ui-widget-content .dg li.save-row .button {\n  text-shadow: none !important;\n}\n.ui-widget-content .dg li.title {\n  background: rgba(255, 255, 255, 0) url(data:image/gif;base64,R0lGODlhBQAFAJEAAP////Pz8////////yH5BAEAAAIALAAAAAAFAAUAAAIIlI+hKgFxoCgAOw==) 6px 10px no-repeat;\n}\n.ui-widget-content .dg .cr.function:hover,\n.dg .cr.boolean:hover {\n  background: #fff;\n}\n.ui-widget-content .dg .c input[type=text],\n.ui-widget-content .dg .c textarea {\n  background: rgba(255, 255, 255, 0);\n  box-shadow: none !important;\n  webkit-box-shadow: none !important;\n}\n.ui-widget-content .dg .c input[type=text]:hover,\n.ui-widget-content .dg .c textarea:hover {\n  background: rgba(33, 29, 29, 0.4);\n  cursor: pointer;\n}\n.ui-widget-content .dg .c input[type=text]:focus,\n.ui-widget-content .dg .c textarea:focus {\n  background: rgba(33, 29, 29, 0.4);\n  cursor: pointer;\n}\n.ui-widget-content .dg .c .slider {\n  background: #e9e9e9;\n}\n.ui-widget-content .dg .c .slider:hover {\n  background: #eee;\n}\n/*  GENERIC NODE STYLE */\n.ui-widget-content .dg .cr.string {\n  border-left: 3px solid #85ea0e;\n}\n.ui-widget-content .dg .cr.string input[type=text],\n.ui-widget-content .dg .cr.string textarea {\n  color: #85ea0e;\n}\n.ui-widget-content .dg .cr.string textarea {\n  width: 100%;\n  border: 0px;\n  margin-top: 5px;\n  line-height: 20px;\n  resize: none;\n  height: 60px;\n}\n/*  NODE STYLE BY METATYPE*/\n.instancefoldertv {\n  border-left: 3px solid #0499e6;\n  background-color: #231f1f!important;\n}\n.arrayinstancetv {\n  border-left: 3px solid #ff5a02;\n  background-color: #231f1f!important;\n}\n.arraytypetv {\n  border-left: 3px solid #fe4807;\n  background-color: #fe4807 !important;\n}\n.foldertv {\n  border-left: 3px solid #2e2a2a;\n  background-color: #2e2a2a !important;\n}\n.dg .cr.string.dynamicstypetv {\n  border-left: 3px solid #00cc66;\n}\n.dg .cr.string.dynamicstypetv input[type=text] {\n  color: #00cc66;\n}\n.dg .cr.string.functiontypetv {\n  border-left: 3px solid #00cccc;\n}\n.dg .cr.string.functiontypetv input[type=text] {\n  color: #00cccc;\n}\n.dg .cr.string.parametertypetv {\n  border-left: 3px solid #0066cc;\n}\n.dg .cr.string.parametertypetv input[type=text] {\n  color: #0066cc;\n}\n.dg .cr.string.statevariabletypetv {\n  border-left: 3px solid #42b6ff;\n}\n.dg .cr.string.statevariabletypetv input[type=text] {\n  color: #42b6ff;\n}\n.dg .cr.string.texttypetv {\n  border-left: 3px solid #10b7bd;\n}\n.dg .cr.string.texttypetv input[type=text],\n.dg .cr.string.texttypetv textarea {\n  color: #10b7bd;\n}\n.dg .cr.string.pointertypetv {\n  border-left: 3px solid #10b7bd;\n}\n.dg .cr.string.pointertypetv input[type=text],\n.dg .cr.string.pointertypetv textarea {\n  color: #10b7bd;\n}\n.ui-widget-content .dg ul:not(.closed) > li.textarea {\n  height: 100%;\n}\n.dg .cr.string.stateinstancetv {\n  border-left: 3px solid #cc00cc;\n}\n.dg .cr.string.stateinstancetv input[type=text] {\n  color: #cc00cc;\n}\n.dg .cr.string.visualgroupelementtv {\n  border-left: 3px solid #FFA500;\n}\n.dg .cr.string.visualgroupelementtv input[type=text] {\n  text-align: center;\n}\n#tvIcons {\n  z-index: 9999;\n  width: 5%;\n  right: 0;\n  margin-right: 10px;\n  margin-top: 7px;\n  position: absolute;\n}\n#tvIcons:hover {\n  color: #FF6700;\n}\n", ""]);

// exports


/***/ }),

/***/ 3371:
/***/ (function(module, exports, __webpack_require__) {

var __WEBPACK_AMD_DEFINE_RESULT__;var _typeof = typeof Symbol === "function" && typeof Symbol.iterator === "symbol" ? function (obj) { return typeof obj; } : function (obj) { return obj && typeof Symbol === "function" && obj.constructor === Symbol && obj !== Symbol.prototype ? "symbol" : typeof obj; };

/**
 * dat-gui JavaScript Controller Library
 * http://code.google.com/p/dat-gui
 *
 * Copyright 2011 Data Arts Team, Google Creative Lab
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * http://www.apache.org/licenses/LICENSE-2.0
 */
!(__WEBPACK_AMD_DEFINE_RESULT__ = function (require) {

	var dat = dat || {};
	dat.gui = dat.gui || {};
	dat.utils = dat.utils || {};
	dat.controllers = dat.controllers || {};
	dat.dom = dat.dom || {};
	dat.color = dat.color || {};
	dat.utils.css = function () {
		return {
			load: function load(e, a) {
				var a = a || document,
				    c = a.createElement("link");
				c.type = "text/css";
				c.rel = "stylesheet";
				c.href = e;
				a.getElementsByTagName("head")[0].appendChild(c);
			}, inject: function inject(e, a) {
				var a = a || document,
				    c = document.createElement("style");
				c.type = "text/css";
				c.innerHTML = e;
				a.getElementsByTagName("head")[0].appendChild(c);
			}
		};
	}();
	dat.utils.common = function () {
		var e = Array.prototype.forEach,
		    a = Array.prototype.slice;
		return {
			BREAK: {}, extend: function extend(c) {
				this.each(a.call(arguments, 1), function (a) {
					for (var f in a) {
						this.isUndefined(a[f]) || (c[f] = a[f]);
					}
				}, this);
				return c;
			}, defaults: function defaults(c) {
				this.each(a.call(arguments, 1), function (a) {
					for (var f in a) {
						this.isUndefined(c[f]) && (c[f] = a[f]);
					}
				}, this);
				return c;
			}, compose: function compose() {
				var c = a.call(arguments);
				return function () {
					for (var d = a.call(arguments), f = c.length - 1; f >= 0; f--) {
						d = [c[f].apply(this, d)];
					}return d[0];
				};
			},
			each: function each(a, d, f) {
				if (e && a.forEach === e) a.forEach(d, f);else if (a.length === a.length + 0) for (var b = 0, n = a.length; b < n; b++) {
					if (b in a && d.call(f, a[b], b) === this.BREAK) break;
				} else for (b in a) {
					if (d.call(f, a[b], b) === this.BREAK) break;
				}
			}, defer: function defer(a) {
				setTimeout(a, 0);
			}, toArray: function toArray(c) {
				return c.toArray ? c.toArray() : a.call(c);
			}, isUndefined: function isUndefined(a) {
				return a === void 0;
			}, isNull: function isNull(a) {
				return a === null;
			}, isNaN: function isNaN(a) {
				return a !== a;
			}, isArray: Array.isArray || function (a) {
				return a.constructor === Array;
			}, isObject: function isObject(a) {
				return a === Object(a);
			}, isNumber: function isNumber(a) {
				return a === a + 0;
			}, isString: function isString(a) {
				return a === a + "";
			}, isBoolean: function isBoolean(a) {
				return a === false || a === true;
			}, isFunction: function isFunction(a) {
				return Object.prototype.toString.call(a) === "[object Function]";
			}
		};
	}();
	dat.controllers.Controller = function (e) {
		var a = function a(_a, d) {
			this.initialValue = _a[d];
			this.domElement = document.createElement("div");
			this.object = _a;
			this.property = d;
			this.__onFinishChange = this.__onChange = void 0;
		};
		e.extend(a.prototype, {
			onChange: function onChange(a) {
				this.__onChange = a;
				return this;
			}, onFinishChange: function onFinishChange(a) {
				this.__onFinishChange = a;
				return this;
			}, setValue: function setValue(a) {
				this.object[this.property] = a;
				this.__onChange && this.__onChange.call(this, a);
				this.updateDisplay();
				return this;
			}, getValue: function getValue() {
				return this.object[this.property];
			},
			updateDisplay: function updateDisplay() {
				return this;
			}, isModified: function isModified() {
				return this.initialValue !== this.getValue();
			}
		});
		return a;
	}(dat.utils.common);
	dat.dom.dom = function (e) {
		function a(b) {
			if (b === "0" || e.isUndefined(b)) return 0;
			b = b.match(d);
			return !e.isNull(b) ? parseFloat(b[1]) : 0;
		}

		var c = {};
		e.each({
			HTMLEvents: ["change"],
			MouseEvents: ["click", "mousemove", "mousedown", "mouseup", "mouseover"],
			KeyboardEvents: ["keydown"]
		}, function (b, a) {
			e.each(b, function (b) {
				c[b] = a;
			});
		});
		var d = /(\d+(\.\d+)?)px/,
		    f = {
			makeSelectable: function makeSelectable(b, a) {
				if (!(b === void 0 || b.style === void 0)) b.onselectstart = a ? function () {
					return false;
				} : function () {}, b.style.MozUserSelect = a ? "auto" : "none", b.style.KhtmlUserSelect = a ? "auto" : "none", b.unselectable = a ? "on" : "off";
			}, makeFullscreen: function makeFullscreen(b, a, d) {
				e.isUndefined(a) && (a = true);
				e.isUndefined(d) && (d = true);
				b.style.position = "absolute";
				if (a) b.style.left = 0, b.style.right = 0;
				if (d) b.style.top = 0, b.style.bottom = 0;
			}, fakeEvent: function fakeEvent(b, a, d, f) {
				var d = d || {},
				    m = c[a];
				if (!m) throw Error("Event type " + a + " not supported.");
				var l = document.createEvent(m);
				switch (m) {
					case "MouseEvents":
						l.initMouseEvent(a, d.bubbles || false, d.cancelable || true, window, d.clickCount || 1, 0, 0, d.x || d.clientX || 0, d.y || d.clientY || 0, false, false, false, false, 0, null);
						break;
					case "KeyboardEvents":
						m = l.initKeyboardEvent || l.initKeyEvent;
						e.defaults(d, {
							cancelable: true,
							ctrlKey: false,
							altKey: false,
							shiftKey: false,
							metaKey: false,
							keyCode: void 0,
							charCode: void 0
						});
						m(a, d.bubbles || false, d.cancelable, window, d.ctrlKey, d.altKey, d.shiftKey, d.metaKey, d.keyCode, d.charCode);
						break;
					default:
						l.initEvent(a, d.bubbles || false, d.cancelable || true);
				}
				e.defaults(l, f);
				b.dispatchEvent(l);
			}, bind: function bind(b, a, d, c) {
				b.addEventListener ? b.addEventListener(a, d, c || false) : b.attachEvent && b.attachEvent("on" + a, d);
				return f;
			}, unbind: function unbind(b, a, d, c) {
				b.removeEventListener ? b.removeEventListener(a, d, c || false) : b.detachEvent && b.detachEvent("on" + a, d);
				return f;
			}, addClass: function addClass(b, a) {
				if (b.className === void 0) b.className = a;else if (b.className !== a) {
					var d = b.className.split(/ +/);
					if (d.indexOf(a) == -1) d.push(a), b.className = d.join(" ").replace(/^\s+/, "").replace(/\s+$/, "");
				}
				return f;
			}, removeClass: function removeClass(b, a) {
				if (a) {
					if (b.className !== void 0) if (b.className === a) b.removeAttribute("class");else {
						var d = b.className.split(/ +/),
						    c = d.indexOf(a);
						if (c != -1) d.splice(c, 1), b.className = d.join(" ");
					}
				} else b.className = void 0;
				return f;
			}, hasClass: function hasClass(a, d) {
				return RegExp("(?:^|\\s+)" + d + "(?:\\s+|$)").test(a.className) || false;
			}, getWidth: function getWidth(b) {
				b = getComputedStyle(b);
				return a(b["border-left-width"]) + a(b["border-right-width"]) + a(b["padding-left"]) + a(b["padding-right"]) + a(b.width);
			}, getHeight: function getHeight(b) {
				b = getComputedStyle(b);
				return a(b["border-top-width"]) + a(b["border-bottom-width"]) + a(b["padding-top"]) + a(b["padding-bottom"]) + a(b.height);
			},
			getOffset: function getOffset(a) {
				var d = { left: 0, top: 0 };
				if (a.offsetParent) {
					do {
						d.left += a.offsetLeft, d.top += a.offsetTop;
					} while (a = a.offsetParent);
				}
				return d;
			}, isActive: function isActive(a) {
				return a === document.activeElement && (a.type || a.href);
			}
		};
		return f;
	}(dat.utils.common);
	dat.controllers.OptionController = function (e, a, c) {
		var d = function d(f, b, e) {
			d.superclass.call(this, f, b);
			var h = this;
			this.__select = document.createElement("select");
			if (c.isArray(e)) {
				var j = {};
				c.each(e, function (a) {
					j[a] = a;
				});
				e = j;
			}
			c.each(e, function (a, b) {
				var d = document.createElement("option");
				d.innerHTML = b;
				d.setAttribute("value", a);
				h.__select.appendChild(d);
			});
			this.updateDisplay();
			a.bind(this.__select, "change", function () {
				h.setValue(this.options[this.selectedIndex].value);
			});
			this.domElement.appendChild(this.__select);
		};
		d.superclass = e;
		c.extend(d.prototype, e.prototype, {
			setValue: function setValue(a) {
				a = d.superclass.prototype.setValue.call(this, a);
				this.__onFinishChange && this.__onFinishChange.call(this, this.getValue());
				return a;
			}, updateDisplay: function updateDisplay() {
				this.__select.value = this.getValue();
				return d.superclass.prototype.updateDisplay.call(this);
			}
		});
		return d;
	}(dat.controllers.Controller, dat.dom.dom, dat.utils.common);
	dat.controllers.NumberController = function (e, a) {
		var c = function c(d, f, b) {
			c.superclass.call(this, d, f);
			b = b || {};
			this.__min = b.min;
			this.__max = b.max;
			this.__step = b.step;
			d = this.__impliedStep = a.isUndefined(this.__step) ? this.initialValue == 0 ? 1 : Math.pow(10, Math.floor(Math.log(this.initialValue) / Math.LN10)) / 10 : this.__step;
			d = d.toString();
			this.__precision = d.indexOf(".") > -1 ? d.length - d.indexOf(".") - 1 : 0;
		};
		c.superclass = e;
		a.extend(c.prototype, e.prototype, {
			setValue: function setValue(a) {
				if (this.__min !== void 0 && a < this.__min) a = this.__min;else if (this.__max !== void 0 && a > this.__max) a = this.__max;
				this.__step !== void 0 && a % this.__step != 0 && (a = Math.round(a / this.__step) * this.__step);
				return c.superclass.prototype.setValue.call(this, a);
			}, min: function min(a) {
				this.__min = a;
				return this;
			}, max: function max(a) {
				this.__max = a;
				return this;
			}, step: function step(a) {
				this.__step = a;
				return this;
			}
		});
		return c;
	}(dat.controllers.Controller, dat.utils.common);
	dat.controllers.NumberControllerBox = function (e, a, c) {
		var d = function d(f, b, e) {
			function h() {
				var a = parseFloat(l.__input.value);
				c.isNaN(a) || l.setValue(a);
			}

			function j(a) {
				var b = o - a.clientY;
				l.setValue(l.getValue() + b * l.__impliedStep);
				o = a.clientY;
			}

			function m() {
				a.unbind(window, "mousemove", j);
				a.unbind(window, "mouseup", m);
			}

			this.__truncationSuspended = false;
			d.superclass.call(this, f, b, e);
			var l = this,
			    o;
			this.__input = document.createElement("input");
			this.__input.setAttribute("type", "text");
			a.bind(this.__input, "change", h);
			a.bind(this.__input, "blur", function () {
				h();
				l.__onFinishChange && l.__onFinishChange.call(l, l.getValue());
			});
			a.bind(this.__input, "mousedown", function (b) {
				a.bind(window, "mousemove", j);
				a.bind(window, "mouseup", m);
				o = b.clientY;
			});
			a.bind(this.__input, "keydown", function (a) {
				if (a.keyCode === 13) l.__truncationSuspended = true, this.blur(), l.__truncationSuspended = false;
			});
			this.updateDisplay();
			this.domElement.appendChild(this.__input);
		};
		d.superclass = e;
		c.extend(d.prototype, e.prototype, {
			updateDisplay: function updateDisplay() {
				var a = this.__input,
				    b;
				if (this.__truncationSuspended) b = this.getValue();else {
					b = this.getValue();
					var c = Math.pow(10, this.__precision);
					b = Math.round(b * c) / c;
				}
				a.value = b;
				return d.superclass.prototype.updateDisplay.call(this);
			}
		});
		return d;
	}(dat.controllers.NumberController, dat.dom.dom, dat.utils.common);
	dat.controllers.NumberControllerSlider = function (e, a, c, d, f) {
		var b = function b(d, c, f, e, l) {
			function o(b) {
				b.preventDefault();
				var d = a.getOffset(g.__background),
				    c = a.getWidth(g.__background);
				g.setValue(g.__min + (g.__max - g.__min) * ((b.clientX - d.left) / (d.left + c - d.left)));
				return false;
			}

			function y() {
				a.unbind(window, "mousemove", o);
				a.unbind(window, "mouseup", y);
				g.__onFinishChange && g.__onFinishChange.call(g, g.getValue());
			}

			b.superclass.call(this, d, c, { min: f, max: e, step: l });
			var g = this;
			this.__background = document.createElement("div");
			this.__foreground = document.createElement("div");
			a.bind(this.__background, "mousedown", function (b) {
				a.bind(window, "mousemove", o);
				a.bind(window, "mouseup", y);
				o(b);
			});
			a.addClass(this.__background, "slider");
			a.addClass(this.__foreground, "slider-fg");
			this.updateDisplay();
			this.__background.appendChild(this.__foreground);
			this.domElement.appendChild(this.__background);
		};
		b.superclass = e;
		b.useDefaultStyles = function () {
			c.inject(f);
		};
		d.extend(b.prototype, e.prototype, {
			updateDisplay: function updateDisplay() {
				this.__foreground.style.width = (this.getValue() - this.__min) / (this.__max - this.__min) * 100 + "%";
				return b.superclass.prototype.updateDisplay.call(this);
			}
		});
		return b;
	}(dat.controllers.NumberController, dat.dom.dom, dat.utils.css, dat.utils.common, ".slider {\n  box-shadow: inset 0 2px 4px rgba(0,0,0,0.15);\n  height: 1em;\n  border-radius: 1em;\n  background-color: #eee;\n  padding: 0 0.5em;\n  overflow: hidden;\n}\n\n.slider-fg {\n  padding: 1px 0 2px 0;\n  background-color: #aaa;\n  height: 1em;\n  margin-left: -0.5em;\n  padding-right: 0.5em;\n  border-radius: 1em 0 0 1em;\n}\n\n.slider-fg:after {\n  display: inline-block;\n  border-radius: 1em;\n  background-color: #fff;\n  border:  1px solid #aaa;\n  content: '';\n  float: right;\n  margin-right: -1em;\n  margin-top: -1px;\n  height: 0.9em;\n  width: 0.9em;\n}");
	dat.controllers.FunctionController = function (e, a, c) {
		var d = function d(c, b, e) {
			d.superclass.call(this, c, b);
			var h = this;
			this.__button = document.createElement("div");
			this.__button.innerHTML = e === void 0 ? "Fire" : e;
			a.bind(this.__button, "click", function (a) {
				a.preventDefault();
				h.fire();
				return false;
			});
			a.addClass(this.__button, "button");
			this.domElement.appendChild(this.__button);
		};
		d.superclass = e;
		c.extend(d.prototype, e.prototype, {
			fire: function fire() {
				this.__onChange && this.__onChange.call(this);
				this.__onFinishChange && this.__onFinishChange.call(this, this.getValue());
				this.getValue().call(this.object);
			}
		});
		return d;
	}(dat.controllers.Controller, dat.dom.dom, dat.utils.common);
	dat.controllers.BooleanController = function (e, a, c) {
		var d = function d(c, b) {
			d.superclass.call(this, c, b);
			var e = this;
			this.__prev = this.getValue();
			this.__checkbox = document.createElement("input");
			this.__checkbox.setAttribute("type", "checkbox");
			a.bind(this.__checkbox, "change", function () {
				e.setValue(!e.__prev);
			}, false);
			this.domElement.appendChild(this.__checkbox);
			this.updateDisplay();
		};
		d.superclass = e;
		c.extend(d.prototype, e.prototype, {
			setValue: function setValue(a) {
				a = d.superclass.prototype.setValue.call(this, a);
				this.__onFinishChange && this.__onFinishChange.call(this, this.getValue());
				this.__prev = this.getValue();
				return a;
			}, updateDisplay: function updateDisplay() {
				this.getValue() === true ? (this.__checkbox.setAttribute("checked", "checked"), this.__checkbox.checked = true) : this.__checkbox.checked = false;
				return d.superclass.prototype.updateDisplay.call(this);
			}
		});
		return d;
	}(dat.controllers.Controller, dat.dom.dom, dat.utils.common);
	dat.color.toString = function (e) {
		return function (a) {
			if (a.a == 1 || e.isUndefined(a.a)) {
				for (a = a.hex.toString(16); a.length < 6;) {
					a = "0" + a;
				}return "#" + a;
			} else return "rgba(" + Math.round(a.r) + "," + Math.round(a.g) + "," + Math.round(a.b) + "," + a.a + ")";
		};
	}(dat.utils.common);
	dat.color.interpret = function (e, a) {
		var c,
		    d,
		    f = [{
			litmus: a.isString, conversions: {
				THREE_CHAR_HEX: {
					read: function read(a) {
						a = a.match(/^#([A-F0-9])([A-F0-9])([A-F0-9])$/i);
						return a === null ? false : {
							space: "HEX",
							hex: parseInt("0x" + a[1].toString() + a[1].toString() + a[2].toString() + a[2].toString() + a[3].toString() + a[3].toString())
						};
					}, write: e
				}, SIX_CHAR_HEX: {
					read: function read(a) {
						a = a.match(/^#([A-F0-9]{6})$/i);
						return a === null ? false : { space: "HEX", hex: parseInt("0x" + a[1].toString()) };
					}, write: e
				}, CSS_RGB: {
					read: function read(a) {
						a = a.match(/^rgb\(\s*(.+)\s*,\s*(.+)\s*,\s*(.+)\s*\)/);
						return a === null ? false : {
							space: "RGB",
							r: parseFloat(a[1]),
							g: parseFloat(a[2]),
							b: parseFloat(a[3])
						};
					}, write: e
				}, CSS_RGBA: {
					read: function read(a) {
						a = a.match(/^rgba\(\s*(.+)\s*,\s*(.+)\s*,\s*(.+)\s*\,\s*(.+)\s*\)/);
						return a === null ? false : {
							space: "RGB",
							r: parseFloat(a[1]),
							g: parseFloat(a[2]),
							b: parseFloat(a[3]),
							a: parseFloat(a[4])
						};
					}, write: e
				}
			}
		}, {
			litmus: a.isNumber, conversions: {
				HEX: {
					read: function read(a) {
						return { space: "HEX", hex: a, conversionName: "HEX" };
					}, write: function write(a) {
						return a.hex;
					}
				}
			}
		}, {
			litmus: a.isArray, conversions: {
				RGB_ARRAY: {
					read: function read(a) {
						return a.length != 3 ? false : { space: "RGB", r: a[0], g: a[1], b: a[2] };
					}, write: function write(a) {
						return [a.r, a.g, a.b];
					}
				}, RGBA_ARRAY: {
					read: function read(a) {
						return a.length != 4 ? false : { space: "RGB", r: a[0], g: a[1], b: a[2], a: a[3] };
					}, write: function write(a) {
						return [a.r, a.g, a.b, a.a];
					}
				}
			}
		}, {
			litmus: a.isObject, conversions: {
				RGBA_OBJ: {
					read: function read(b) {
						return a.isNumber(b.r) && a.isNumber(b.g) && a.isNumber(b.b) && a.isNumber(b.a) ? {
							space: "RGB",
							r: b.r,
							g: b.g,
							b: b.b,
							a: b.a
						} : false;
					}, write: function write(a) {
						return { r: a.r, g: a.g, b: a.b, a: a.a };
					}
				}, RGB_OBJ: {
					read: function read(b) {
						return a.isNumber(b.r) && a.isNumber(b.g) && a.isNumber(b.b) ? { space: "RGB", r: b.r, g: b.g, b: b.b } : false;
					}, write: function write(a) {
						return { r: a.r, g: a.g, b: a.b };
					}
				}, HSVA_OBJ: {
					read: function read(b) {
						return a.isNumber(b.h) && a.isNumber(b.s) && a.isNumber(b.v) && a.isNumber(b.a) ? {
							space: "HSV",
							h: b.h,
							s: b.s,
							v: b.v,
							a: b.a
						} : false;
					}, write: function write(a) {
						return { h: a.h, s: a.s, v: a.v, a: a.a };
					}
				}, HSV_OBJ: {
					read: function read(b) {
						return a.isNumber(b.h) && a.isNumber(b.s) && a.isNumber(b.v) ? {
							space: "HSV",
							h: b.h,
							s: b.s,
							v: b.v
						} : false;
					}, write: function write(a) {
						return { h: a.h, s: a.s, v: a.v };
					}
				}
			}
		}];
		return function () {
			d = false;
			var b = arguments.length > 1 ? a.toArray(arguments) : arguments[0];
			a.each(f, function (e) {
				if (e.litmus(b)) return a.each(e.conversions, function (e, f) {
					c = e.read(b);
					if (d === false && c !== false) return d = c, c.conversionName = f, c.conversion = e, a.BREAK;
				}), a.BREAK;
			});
			return d;
		};
	}(dat.color.toString, dat.utils.common);
	dat.GUI = dat.gui.GUI = function (e, a, c, d, f, b, n, h, j, m, l, o, y, g, i) {
		function q(a, b, r, c) {
			if (b[r] === void 0) throw Error("Object " + b + ' has no property "' + r + '"');
			c.color ? b = new l(b, r) : (b = [b, r].concat(c.factoryArgs), b = d.apply(a, b));
			if (c.before instanceof f) c.before = c.before.__li;
			t(a, b);
			g.addClass(b.domElement, "c");
			r = document.createElement("span");
			g.addClass(r, "property-name");
			r.innerHTML = b.property;
			var e = document.createElement("div");
			e.appendChild(r);
			e.appendChild(b.domElement);
			c = s(a, e, c.before);
			g.addClass(c, k.CLASS_CONTROLLER_ROW);
			g.addClass(c, _typeof(b.getValue()));
			p(a, c, b);
			a.__controllers.push(b);
			return b;
		}

		function s(a, b, d) {
			var c = document.createElement("li");
			b && c.appendChild(b);
			d ? a.__ul.insertBefore(c, params.before) : a.__ul.appendChild(c);
			a.onResize();
			return c;
		}

		function p(a, d, c) {
			c.__li = d;
			c.__gui = a;
			i.extend(c, {
				options: function options(b) {
					if (arguments.length > 1) return c.remove(), q(a, c.object, c.property, {
						before: c.__li.nextElementSibling,
						factoryArgs: [i.toArray(arguments)]
					});
					if (i.isArray(b) || i.isObject(b)) return c.remove(), q(a, c.object, c.property, { before: c.__li.nextElementSibling, factoryArgs: [b] });
				}, name: function name(a) {
					c.__li.firstElementChild.firstElementChild.innerHTML = a;
					return c;
				}, listen: function listen() {
					c.__gui.listen(c);
					return c;
				}, remove: function remove() {
					c.__gui.remove(c);
					return c;
				}
			});
			if (c instanceof j) {
				var e = new h(c.object, c.property, { min: c.__min, max: c.__max, step: c.__step });
				i.each(["updateDisplay", "onChange", "onFinishChange"], function (a) {
					var b = c[a],
					    H = e[a];
					c[a] = e[a] = function () {
						var a = Array.prototype.slice.call(arguments);
						b.apply(c, a);
						return H.apply(e, a);
					};
				});
				g.addClass(d, "has-slider");
				c.domElement.insertBefore(e.domElement, c.domElement.firstElementChild);
			} else if (c instanceof h) {
				var f = function f(b) {
					return i.isNumber(c.__min) && i.isNumber(c.__max) ? (c.remove(), q(a, c.object, c.property, {
						before: c.__li.nextElementSibling,
						factoryArgs: [c.__min, c.__max, c.__step]
					})) : b;
				};
				c.min = i.compose(f, c.min);
				c.max = i.compose(f, c.max);
			} else if (c instanceof b) g.bind(d, "click", function () {
				g.fakeEvent(c.__checkbox, "click");
			}), g.bind(c.__checkbox, "click", function (a) {
				a.stopPropagation();
			});else if (c instanceof n) g.bind(d, "click", function () {
				g.fakeEvent(c.__button, "click");
			}), g.bind(d, "mouseover", function () {
				g.addClass(c.__button, "hover");
			}), g.bind(d, "mouseout", function () {
				g.removeClass(c.__button, "hover");
			});else if (c instanceof l) g.addClass(d, "color"), c.updateDisplay = i.compose(function (a) {
				d.style.borderLeftColor = c.__color.toString();
				return a;
			}, c.updateDisplay), c.updateDisplay();
			c.setValue = i.compose(function (b) {
				a.getRoot().__preset_select && c.isModified() && B(a.getRoot(), true);
				return b;
			}, c.setValue);
		}

		function t(a, b) {
			var c = a.getRoot(),
			    d = c.__rememberedObjects.indexOf(b.object);
			if (d != -1) {
				var e = c.__rememberedObjectIndecesToControllers[d];
				e === void 0 && (e = {}, c.__rememberedObjectIndecesToControllers[d] = e);
				e[b.property] = b;
				if (c.load && c.load.remembered) {
					c = c.load.remembered;
					if (c[a.preset]) c = c[a.preset];else if (c[w]) c = c[w];else return;
					if (c[d] && c[d][b.property] !== void 0) d = c[d][b.property], b.initialValue = d, b.setValue(d);
				}
			}
		}

		function I(a) {
			var b = a.__save_row = document.createElement("li");
			g.addClass(a.domElement, "has-save");
			a.__ul.insertBefore(b, a.__ul.firstChild);
			g.addClass(b, "save-row");
			var c = document.createElement("span");
			c.innerHTML = "&nbsp;";
			g.addClass(c, "button gears");
			var d = document.createElement("span");
			d.innerHTML = "Save";
			g.addClass(d, "button");
			g.addClass(d, "save");
			var e = document.createElement("span");
			e.innerHTML = "New";
			g.addClass(e, "button");
			g.addClass(e, "save-as");
			var f = document.createElement("span");
			f.innerHTML = "Revert";
			g.addClass(f, "button");
			g.addClass(f, "revert");
			var m = a.__preset_select = document.createElement("select");
			a.load && a.load.remembered ? i.each(a.load.remembered, function (b, c) {
				C(a, c, c == a.preset);
			}) : C(a, w, false);
			g.bind(m, "change", function () {
				for (var b = 0; b < a.__preset_select.length; b++) {
					a.__preset_select[b].innerHTML = a.__preset_select[b].value;
				}a.preset = this.value;
			});
			b.appendChild(m);
			b.appendChild(c);
			b.appendChild(d);
			b.appendChild(e);
			b.appendChild(f);
			if (u) {
				var b = document.getElementById("dg-save-locally"),
				    l = document.getElementById("dg-local-explain");
				b.style.display = "block";
				b = document.getElementById("dg-local-storage");
				localStorage.getItem(document.location.href + ".isLocal") === "true" && b.setAttribute("checked", "checked");
				var o = function o() {
					l.style.display = a.useLocalStorage ? "block" : "none";
				};
				o();
				g.bind(b, "change", function () {
					a.useLocalStorage = !a.useLocalStorage;
					o();
				});
			}
			var h = document.getElementById("dg-new-constructor");
			g.bind(h, "keydown", function (a) {
				a.metaKey && (a.which === 67 || a.keyCode == 67) && x.hide();
			});
			g.bind(c, "click", function () {
				h.innerHTML = JSON.stringify(a.getSaveObject(), void 0, 2);
				x.show();
				h.focus();
				h.select();
			});
			g.bind(d, "click", function () {
				a.save();
			});
			g.bind(e, "click", function () {
				var b = prompt("Enter a new preset name.");
				b && a.saveAs(b);
			});
			g.bind(f, "click", function () {
				a.revert();
			});
		}

		function J(a) {
			function b(f) {
				f.preventDefault();
				e = f.clientX;
				g.addClass(a.__closeButton, k.CLASS_DRAG);
				g.bind(window, "mousemove", c);
				g.bind(window, "mouseup", d);
				return false;
			}

			function c(b) {
				b.preventDefault();
				a.width += e - b.clientX;
				a.onResize();
				e = b.clientX;
				return false;
			}

			function d() {
				g.removeClass(a.__closeButton, k.CLASS_DRAG);
				g.unbind(window, "mousemove", c);
				g.unbind(window, "mouseup", d);
			}

			a.__resize_handle = document.createElement("div");
			i.extend(a.__resize_handle.style, {
				width: "6px",
				marginLeft: "-3px",
				height: "200px",
				cursor: "ew-resize",
				position: "absolute"
			});
			var e;
			g.bind(a.__resize_handle, "mousedown", b);
			g.bind(a.__closeButton, "mousedown", b);
			a.domElement.insertBefore(a.__resize_handle, a.domElement.firstElementChild);
		}

		function D(a, b) {
			a.domElement.style.width = b + "px";
			if (a.__save_row && a.autoPlace) a.__save_row.style.width = b + "px";
			if (a.__closeButton) a.__closeButton.style.width = b + "px";
		}

		function z(a, b) {
			var c = {};
			i.each(a.__rememberedObjects, function (d, e) {
				var f = {};
				i.each(a.__rememberedObjectIndecesToControllers[e], function (a, c) {
					f[c] = b ? a.initialValue : a.getValue();
				});
				c[e] = f;
			});
			return c;
		}

		function C(a, b, c) {
			var d = document.createElement("option");
			d.innerHTML = b;
			d.value = b;
			a.__preset_select.appendChild(d);
			if (c) a.__preset_select.selectedIndex = a.__preset_select.length - 1;
		}

		function B(a, b) {
			var c = a.__preset_select[a.__preset_select.selectedIndex];
			c.innerHTML = b ? c.value + "*" : c.value;
		}

		function E(a) {
			a.length != 0 && o(function () {
				E(a);
			});
			i.each(a, function (a) {
				a.updateDisplay();
			});
		}

		e.inject(c);
		var w = "Default",
		    u;
		try {
			u = "localStorage" in window && window.localStorage !== null;
		} catch (K) {
			u = false;
		}
		var x,
		    F = true,
		    v,
		    A = false,
		    G = [],
		    k = function k(a) {
			function b() {
				localStorage.setItem(document.location.href + ".gui", JSON.stringify(d.getSaveObject()));
			}

			function c() {
				var a = d.getRoot();
				a.width += 1;
				i.defer(function () {
					a.width -= 1;
				});
			}

			var d = this;
			this.domElement = document.createElement("div");
			this.__ul = document.createElement("ul");
			this.domElement.appendChild(this.__ul);
			g.addClass(this.domElement, "dg");
			this.__folders = {};
			this.__controllers = [];
			this.__rememberedObjects = [];
			this.__rememberedObjectIndecesToControllers = [];
			this.__listening = [];
			a = a || {};
			a = i.defaults(a, { autoPlace: true, width: k.DEFAULT_WIDTH });
			a = i.defaults(a, { resizable: a.autoPlace, hideable: a.autoPlace });
			if (i.isUndefined(a.load)) a.load = { preset: w };else if (a.preset) a.load.preset = a.preset;
			i.isUndefined(a.parent) && a.hideable && G.push(this);
			a.resizable = i.isUndefined(a.parent) && a.resizable;
			if (a.autoPlace && i.isUndefined(a.scrollable)) a.scrollable = true;
			var e = u && localStorage.getItem(document.location.href + ".isLocal") === "true";
			Object.defineProperties(this, {
				parent: {
					get: function get() {
						return a.parent;
					}
				}, scrollable: {
					get: function get() {
						return a.scrollable;
					}
				}, autoPlace: {
					get: function get() {
						return a.autoPlace;
					}
				}, preset: {
					get: function get() {
						return d.parent ? d.getRoot().preset : a.load.preset;
					}, set: function set(b) {
						d.parent ? d.getRoot().preset = b : a.load.preset = b;
						for (b = 0; b < this.__preset_select.length; b++) {
							if (this.__preset_select[b].value == this.preset) this.__preset_select.selectedIndex = b;
						}d.revert();
					}
				}, width: {
					get: function get() {
						return a.width;
					}, set: function set(b) {
						a.width = b;
						D(d, b);
					}
				}, name: {
					get: function get() {
						return a.name;
					}, set: function set(b) {
						a.name = b;
						if (m) m.innerHTML = a.name;
					}
				}, closed: {
					get: function get() {
						return a.closed;
					}, set: function set(b) {
						a.closed = b;
						a.closed ? g.addClass(d.__ul, k.CLASS_CLOSED) : g.removeClass(d.__ul, k.CLASS_CLOSED);
						this.onResize();
						if (d.__closeButton) d.__closeButton.innerHTML = b ? k.TEXT_OPEN : k.TEXT_CLOSED;
					}
				}, load: {
					get: function get() {
						return a.load;
					}
				}, useLocalStorage: {
					get: function get() {
						return e;
					}, set: function set(a) {
						u && ((e = a) ? g.bind(window, "unload", b) : g.unbind(window, "unload", b), localStorage.setItem(document.location.href + ".isLocal", a));
					}
				}
			});
			if (i.isUndefined(a.parent)) {
				a.closed = false;
				g.addClass(this.domElement, k.CLASS_MAIN);
				g.makeSelectable(this.domElement, false);
				if (u && e) {
					d.useLocalStorage = true;
					var f = localStorage.getItem(document.location.href + ".gui");
					if (f) a.load = JSON.parse(f);
				}
				this.__closeButton = document.createElement("div");
				this.__closeButton.innerHTML = k.TEXT_CLOSED;
				g.addClass(this.__closeButton, k.CLASS_CLOSE_BUTTON);
				this.domElement.appendChild(this.__closeButton);
				g.bind(this.__closeButton, "click", function () {
					d.closed = !d.closed;
				});
			} else {
				if (a.closed === void 0) a.closed = true;
				var m = document.createTextNode(a.name);
				g.addClass(m, "controller-name");
				f = s(d, m);
				g.addClass(this.__ul, k.CLASS_CLOSED);
				g.addClass(f, "title");
				g.bind(f, "click", function (a) {
					a.preventDefault();
					d.closed = !d.closed;
					return false;
				});
				if (!a.closed) this.closed = false;
			}
			a.autoPlace && (i.isUndefined(a.parent) && (F && (v = document.createElement("div"), g.addClass(v, "dg"), g.addClass(v, k.CLASS_AUTO_PLACE_CONTAINER), document.body.appendChild(v), F = false), v.appendChild(this.domElement), g.addClass(this.domElement, k.CLASS_AUTO_PLACE)), this.parent || D(d, a.width));
			g.bind(window, "resize", function () {
				d.onResize();
			});
			g.bind(this.__ul, "webkitTransitionEnd", function () {
				d.onResize();
			});
			g.bind(this.__ul, "transitionend", function () {
				d.onResize();
			});
			g.bind(this.__ul, "oTransitionEnd", function () {
				d.onResize();
			});
			this.onResize();
			a.resizable && J(this);
			d.getRoot();
			a.parent || c();
		};
		k.toggleHide = function () {
			A = !A;
			i.each(G, function (a) {
				a.domElement.style.zIndex = A ? -999 : 999;
				a.domElement.style.opacity = A ? 0 : 1;
			});
		};
		k.CLASS_AUTO_PLACE = "a";
		k.CLASS_AUTO_PLACE_CONTAINER = "ac";
		k.CLASS_MAIN = "main";
		k.CLASS_CONTROLLER_ROW = "cr";
		k.CLASS_TOO_TALL = "taller-than-window";
		k.CLASS_CLOSED = "closed";
		k.CLASS_CLOSE_BUTTON = "close-button";
		k.CLASS_DRAG = "drag";
		k.DEFAULT_WIDTH = 245;
		k.TEXT_CLOSED = "Close Controls";
		k.TEXT_OPEN = "Open Controls";
		g.bind(window, "keydown", function (a) {
			document.activeElement.type !== "text" && (a.which === 72 || a.keyCode == 72) && k.toggleHide();
		}, false);
		i.extend(k.prototype, {
			add: function add(a, b) {
				return q(this, a, b, { factoryArgs: Array.prototype.slice.call(arguments, 2) });
			}, addColor: function addColor(a, b) {
				return q(this, a, b, { color: true });
			}, remove: function remove(a) {
				this.__ul.removeChild(a.__li);
				this.__controllers.slice(this.__controllers.indexOf(a), 1);
				var b = this;
				i.defer(function () {
					b.onResize();
				});
			}, destroy: function destroy() {
				this.autoPlace && v.removeChild(this.domElement);
			}, addFolder: function addFolder(a) {
				if (this.__folders[a] !== void 0) throw Error('You already have a folder in this GUI by the name "' + a + '"');
				var b = { name: a, parent: this };
				b.autoPlace = this.autoPlace;
				if (this.load && this.load.folders && this.load.folders[a]) b.closed = this.load.folders[a].closed, b.load = this.load.folders[a];
				b = new k(b);
				this.__folders[a] = b;
				a = s(this, b.domElement);
				g.addClass(a, "folder");
				return b;
			}, open: function open() {
				this.closed = false;
			}, close: function close() {
				this.closed = true;
			}, onResize: function onResize() {
				var a = this.getRoot();
				if (a.scrollable) {
					var b = g.getOffset(a.__ul).top,
					    c = 0;
					i.each(a.__ul.childNodes, function (b) {
						a.autoPlace && b === a.__save_row || (c += g.getHeight(b));
					});
					window.innerHeight - b - 20 < c ? (g.addClass(a.domElement, k.CLASS_TOO_TALL), a.__ul.style.height = window.innerHeight - b - 20 + "px") : (g.removeClass(a.domElement, k.CLASS_TOO_TALL), a.__ul.style.height = "auto");
				}
				a.__resize_handle && i.defer(function () {
					a.__resize_handle.style.height = a.__ul.offsetHeight + "px";
				});
				if (a.__closeButton) a.__closeButton.style.width = a.width + "px";
			}, remember: function remember() {
				if (i.isUndefined(x)) x = new y(), x.domElement.innerHTML = a;
				if (this.parent) throw Error("You can only call remember on a top level GUI.");
				var b = this;
				i.each(Array.prototype.slice.call(arguments), function (a) {
					b.__rememberedObjects.length == 0 && I(b);
					b.__rememberedObjects.indexOf(a) == -1 && b.__rememberedObjects.push(a);
				});
				this.autoPlace && D(this, this.width);
			}, getRoot: function getRoot() {
				for (var a = this; a.parent;) {
					a = a.parent;
				}return a;
			}, getSaveObject: function getSaveObject() {
				var a = this.load;
				a.closed = this.closed;
				if (this.__rememberedObjects.length > 0) {
					a.preset = this.preset;
					if (!a.remembered) a.remembered = {};
					a.remembered[this.preset] = z(this);
				}
				a.folders = {};
				i.each(this.__folders, function (b, c) {
					a.folders[c] = b.getSaveObject();
				});
				return a;
			}, save: function save() {
				if (!this.load.remembered) this.load.remembered = {};
				this.load.remembered[this.preset] = z(this);
				B(this, false);
			}, saveAs: function saveAs(a) {
				if (!this.load.remembered) this.load.remembered = {}, this.load.remembered[w] = z(this, true);
				this.load.remembered[a] = z(this);
				this.preset = a;
				C(this, a, true);
			}, revert: function revert(a) {
				i.each(this.__controllers, function (b) {
					this.getRoot().load.remembered ? t(a || this.getRoot(), b) : b.setValue(b.initialValue);
				}, this);
				i.each(this.__folders, function (a) {
					a.revert(a);
				});
				a || B(this.getRoot(), false);
			}, listen: function listen(a) {
				var b = this.__listening.length == 0;
				this.__listening.push(a);
				b && E(this.__listening);
			}
		});
		return k;
	}(dat.utils.css, '<div id="dg-save" class="dg dialogue">\n\n  Here\'s the new load parameter for your <code>GUI</code>\'s constructor:\n\n  <textarea id="dg-new-constructor"></textarea>\n\n  <div id="dg-save-locally">\n\n    <input id="dg-local-storage" type="checkbox"/> Automatically save\n    values to <code>localStorage</code> on exit.\n\n    <div id="dg-local-explain">The values saved to <code>localStorage</code> will\n      override those passed to <code>dat.GUI</code>\'s constructor. This makes it\n      easier to work incrementally, but <code>localStorage</code> is fragile,\n      and your friends may not see the same values you do.\n      \n    </div>\n    \n  </div>\n\n</div>', ".dg ul{list-style:none;margin:0;padding:0;width:100%;clear:both}.dg.ac{position:fixed;top:0;left:0;right:0;height:0;z-index:0}.dg:not(.ac) .main{overflow:hidden}.dg.main{-webkit-transition:opacity 0.1s linear;-o-transition:opacity 0.1s linear;-moz-transition:opacity 0.1s linear;transition:opacity 0.1s linear}.dg.main.taller-than-window{overflow-y:auto}.dg.main.taller-than-window .close-button{opacity:1;margin-top:-1px;border-top:1px solid #2c2c2c}.dg.main ul.closed .close-button{opacity:1 !important}.dg.main:hover .close-button,.dg.main .close-button.drag{opacity:1}.dg.main .close-button{-webkit-transition:opacity 0.1s linear;-o-transition:opacity 0.1s linear;-moz-transition:opacity 0.1s linear;transition:opacity 0.1s linear;border:0;position:absolute;line-height:19px;height:20px;cursor:pointer;text-align:center;background-color:#000}.dg.main .close-button:hover{background-color:#111}.dg.a{float:right;margin-right:15px;overflow-x:hidden}.dg.a.has-save ul{margin-top:27px}.dg.a.has-save ul.closed{margin-top:0}.dg.a .save-row{position:fixed;top:0;z-index:1002}.dg li{-webkit-transition:height 0.1s ease-out;-o-transition:height 0.1s ease-out;-moz-transition:height 0.1s ease-out;transition:height 0.1s ease-out}.dg li:not(.folder){cursor:auto;height:27px;line-height:27px;overflow:hidden;padding:0 4px 0 5px}.dg li.folder{padding:0;border-left:4px solid rgba(0,0,0,0)}.dg li.title{cursor:pointer;margin-left:-4px}.dg .closed li:not(.title),.dg .closed ul li,.dg .closed ul li > *{height:0;overflow:hidden;border:0}.dg .cr{clear:both;padding-left:3px;height:27px}.dg .property-name{cursor:default;float:left;clear:left;width:40%;overflow:hidden;text-overflow:ellipsis}.dg .c{float:left;width:60%}.dg .c input[type=text]{border:0;margin-top:4px;padding:3px;width:100%;float:right}.dg .has-slider input[type=text]{width:30%;margin-left:0}.dg .slider{float:left;width:66%;margin-left:-5px;margin-right:0;height:19px;margin-top:4px}.dg .slider-fg{height:100%}.dg .c input[type=checkbox]{margin-top:9px}.dg .c select{margin-top:5px}.dg .cr.function,.dg .cr.function .property-name,.dg .cr.function *,.dg .cr.boolean,.dg .cr.boolean *{cursor:pointer}.dg .selector{display:none;position:absolute;margin-left:-9px;margin-top:23px;z-index:10}.dg .c:hover .selector,.dg .selector.drag{display:block}.dg li.save-row{padding:0}.dg li.save-row .button{display:inline-block;padding:0px 6px}.dg.dialogue{background-color:#222;width:460px;padding:15px;font-size:13px;line-height:15px}#dg-new-constructor{padding:10px;color:#222;font-family:Monaco, monospace;font-size:10px;border:0;resize:none;box-shadow:inset 1px 1px 1px #888;word-wrap:break-word;margin:12px 0;display:block;width:440px;overflow-y:scroll;height:100px;position:relative}#dg-local-explain{display:none;font-size:11px;line-height:17px;border-radius:3px;background-color:#333;padding:8px;margin-top:10px}#dg-local-explain code{font-size:10px}#dat-gui-save-locally{display:none}.dg{color:#eee;text-shadow:0 -1px 0 #111}.dg.main::-webkit-scrollbar{width:5px;background:#1a1a1a}.dg.main::-webkit-scrollbar-corner{height:0;display:none}.dg.main::-webkit-scrollbar-thumb{border-radius:5px;background:#676767}.dg li:not(.folder){background:#1a1a1a;}.dg li.save-row{line-height:25px;background:#dad5cb;border:0}.dg li.save-row select{margin-left:5px;width:108px}.dg li.save-row .button{margin-left:5px;margin-top:1px;border-radius:2px;font-size:9px;line-height:7px;padding:4px 4px 5px 4px;background:#c5bdad;color:#fff;text-shadow:0 1px 0 #b0a58f;box-shadow:0 -1px 0 #b0a58f;cursor:pointer}.dg li.save-row .button.gears{background:#c5bdad url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAsAAAANCAYAAAB/9ZQ7AAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAAAQJJREFUeNpiYKAU/P//PwGIC/ApCABiBSAW+I8AClAcgKxQ4T9hoMAEUrxx2QSGN6+egDX+/vWT4e7N82AMYoPAx/evwWoYoSYbACX2s7KxCxzcsezDh3evFoDEBYTEEqycggWAzA9AuUSQQgeYPa9fPv6/YWm/Acx5IPb7ty/fw+QZblw67vDs8R0YHyQhgObx+yAJkBqmG5dPPDh1aPOGR/eugW0G4vlIoTIfyFcA+QekhhHJhPdQxbiAIguMBTQZrPD7108M6roWYDFQiIAAv6Aow/1bFwXgis+f2LUAynwoIaNcz8XNx3Dl7MEJUDGQpx9gtQ8YCueB+D26OECAAQDadt7e46D42QAAAABJRU5ErkJggg==) 2px 1px no-repeat;height:7px;width:8px}.dg li.save-row .button:hover{background-color:#bab19e;box-shadow:0 -1px 0 #b0a58f}.dg li.folder{border-bottom:0}.dg li.title{padding-left:16px;background:#000 url(data:image/gif;base64,R0lGODlhBQAFAJEAAP////Pz8////////yH5BAEAAAIALAAAAAAFAAUAAAIIlI+hKgFxoCgAOw==) 6px 10px no-repeat;cursor:pointer;}.dg .closed li.title{background-image:url(data:image/gif;base64,R0lGODlhBQAFAJEAAP////Pz8////////yH5BAEAAAIALAAAAAAFAAUAAAIIlGIWqMCbWAEAOw==)}.dg .cr.boolean{border-left:3px solid #806787}.dg .cr.function{border-left:3px solid #e61d5f}.dg .cr.number{border-left:3px solid #2fa1d6}.dg .cr.number input[type=text]{color:#2fa1d6}.dg .cr.string{border-left:3px solid #1ed36f}.dg .cr.string input[type=text]{color:#1ed36f}.dg .cr.function:hover,.dg .cr.boolean:hover{background:#111}.dg .c input[type=text]{background:#303030;outline:none}.dg .c input[type=text]:hover{background:#3c3c3c}.dg .c input[type=text]:focus{background:#494949;color:#fff}.dg .c .slider{background:#303030;cursor:ew-resize}.dg .c .slider-fg{background:#2fa1d6}.dg .c .slider:hover{background:#3c3c3c}.dg .c .slider:hover .slider-fg{background:#44abda}\n", dat.controllers.factory = function (e, a, c, d, f, b, n) {
		return function (h, j, m, l) {
			var o = h[j];
			if (n.isArray(m) || n.isObject(m)) return new e(h, j, m);
			if (n.isNumber(o)) return n.isNumber(m) && n.isNumber(l) ? new c(h, j, m, l) : new a(h, j, { min: m, max: l });
			if (n.isString(o)) return new d(h, j);
			if (n.isFunction(o)) return new f(h, j, "");
			if (n.isBoolean(o)) return new b(h, j);
		};
	}(dat.controllers.OptionController, dat.controllers.NumberControllerBox, dat.controllers.NumberControllerSlider, dat.controllers.StringController = function (e, a, c) {
		var d = function d(c, b) {
			function e() {
				h.setValue(h.__input.value);
			}

			d.superclass.call(this, c, b);
			var h = this;
			this.__input = document.createElement("input");
			this.__input.setAttribute("type", "text");
			a.bind(this.__input, "keyup", e);
			a.bind(this.__input, "change", e);
			a.bind(this.__input, "blur", function () {
				h.__onFinishChange && h.__onFinishChange.call(h, h.getValue());
			});
			a.bind(this.__input, "keydown", function (a) {
				a.keyCode === 13 && this.blur();
			});
			this.updateDisplay();
			this.domElement.appendChild(this.__input);
		};
		d.superclass = e;
		c.extend(d.prototype, e.prototype, {
			updateDisplay: function updateDisplay() {
				if (!a.isActive(this.__input)) this.__input.value = this.getValue();
				return d.superclass.prototype.updateDisplay.call(this);
			}
		});
		return d;
	}(dat.controllers.Controller, dat.dom.dom, dat.utils.common), dat.controllers.FunctionController, dat.controllers.BooleanController, dat.utils.common), dat.controllers.Controller, dat.controllers.BooleanController, dat.controllers.FunctionController, dat.controllers.NumberControllerBox, dat.controllers.NumberControllerSlider, dat.controllers.OptionController, dat.controllers.ColorController = function (e, a, c, d, f) {
		function b(a, b, c, d) {
			a.style.background = "";
			f.each(j, function (e) {
				a.style.cssText += "background: " + e + "linear-gradient(" + b + ", " + c + " 0%, " + d + " 100%); ";
			});
		}

		function n(a) {
			a.style.background = "";
			a.style.cssText += "background: -moz-linear-gradient(top,  #ff0000 0%, #ff00ff 17%, #0000ff 34%, #00ffff 50%, #00ff00 67%, #ffff00 84%, #ff0000 100%);";
			a.style.cssText += "background: -webkit-linear-gradient(top,  #ff0000 0%,#ff00ff 17%,#0000ff 34%,#00ffff 50%,#00ff00 67%,#ffff00 84%,#ff0000 100%);";
			a.style.cssText += "background: -o-linear-gradient(top,  #ff0000 0%,#ff00ff 17%,#0000ff 34%,#00ffff 50%,#00ff00 67%,#ffff00 84%,#ff0000 100%);";
			a.style.cssText += "background: -ms-linear-gradient(top,  #ff0000 0%,#ff00ff 17%,#0000ff 34%,#00ffff 50%,#00ff00 67%,#ffff00 84%,#ff0000 100%);";
			a.style.cssText += "background: linear-gradient(top,  #ff0000 0%,#ff00ff 17%,#0000ff 34%,#00ffff 50%,#00ff00 67%,#ffff00 84%,#ff0000 100%);";
		}

		var h = function h(e, l) {
			function o(b) {
				q(b);
				a.bind(window, "mousemove", q);
				a.bind(window, "mouseup", j);
			}

			function j() {
				a.unbind(window, "mousemove", q);
				a.unbind(window, "mouseup", j);
			}

			function g() {
				var a = d(this.value);
				a !== false ? (p.__color.__state = a, p.setValue(p.__color.toOriginal())) : this.value = p.__color.toString();
			}

			function i() {
				a.unbind(window, "mousemove", s);
				a.unbind(window, "mouseup", i);
			}

			function q(b) {
				b.preventDefault();
				var c = a.getWidth(p.__saturation_field),
				    d = a.getOffset(p.__saturation_field),
				    e = (b.clientX - d.left + document.body.scrollLeft) / c,
				    b = 1 - (b.clientY - d.top + document.body.scrollTop) / c;
				b > 1 ? b = 1 : b < 0 && (b = 0);
				e > 1 ? e = 1 : e < 0 && (e = 0);
				p.__color.v = b;
				p.__color.s = e;
				p.setValue(p.__color.toOriginal());
				return false;
			}

			function s(b) {
				b.preventDefault();
				var c = a.getHeight(p.__hue_field),
				    d = a.getOffset(p.__hue_field),
				    b = 1 - (b.clientY - d.top + document.body.scrollTop) / c;
				b > 1 ? b = 1 : b < 0 && (b = 0);
				p.__color.h = b * 360;
				p.setValue(p.__color.toOriginal());
				return false;
			}

			h.superclass.call(this, e, l);
			this.__color = new c(this.getValue());
			this.__temp = new c(0);
			var p = this;
			this.domElement = document.createElement("div");
			a.makeSelectable(this.domElement, false);
			this.__selector = document.createElement("div");
			this.__selector.className = "selector";
			this.__saturation_field = document.createElement("div");
			this.__saturation_field.className = "saturation-field";
			this.__field_knob = document.createElement("div");
			this.__field_knob.className = "field-knob";
			this.__field_knob_border = "2px solid ";
			this.__hue_knob = document.createElement("div");
			this.__hue_knob.className = "hue-knob";
			this.__hue_field = document.createElement("div");
			this.__hue_field.className = "hue-field";
			this.__input = document.createElement("input");
			this.__input.type = "text";
			this.__input_textShadow = "0 1px 1px ";
			a.bind(this.__input, "keydown", function (a) {
				a.keyCode === 13 && g.call(this);
			});
			a.bind(this.__input, "blur", g);
			a.bind(this.__selector, "mousedown", function () {
				a.addClass(this, "drag").bind(window, "mouseup", function () {
					a.removeClass(p.__selector, "drag");
				});
			});
			var t = document.createElement("div");
			f.extend(this.__selector.style, {
				width: "122px",
				height: "102px",
				padding: "3px",
				backgroundColor: "#222",
				boxShadow: "0px 1px 3px rgba(0,0,0,0.3)"
			});
			f.extend(this.__field_knob.style, {
				position: "absolute",
				width: "12px",
				height: "12px",
				border: this.__field_knob_border + (this.__color.v < 0.5 ? "#fff" : "#000"),
				boxShadow: "0px 1px 3px rgba(0,0,0,0.5)",
				borderRadius: "12px",
				zIndex: 1
			});
			f.extend(this.__hue_knob.style, {
				position: "absolute",
				width: "15px",
				height: "2px",
				borderRight: "4px solid #fff",
				zIndex: 1
			});
			f.extend(this.__saturation_field.style, {
				width: "100px",
				height: "100px",
				border: "1px solid #555",
				marginRight: "3px",
				display: "inline-block",
				cursor: "pointer"
			});
			f.extend(t.style, { width: "100%", height: "100%", background: "none" });
			b(t, "top", "rgba(0,0,0,0)", "#000");
			f.extend(this.__hue_field.style, {
				width: "15px",
				height: "100px",
				display: "inline-block",
				border: "1px solid #555",
				cursor: "ns-resize"
			});
			n(this.__hue_field);
			f.extend(this.__input.style, {
				outline: "none",
				textAlign: "center",
				color: "#fff",
				border: 0,
				fontWeight: "bold",
				textShadow: this.__input_textShadow + "rgba(0,0,0,0.7)"
			});
			a.bind(this.__saturation_field, "mousedown", o);
			a.bind(this.__field_knob, "mousedown", o);
			a.bind(this.__hue_field, "mousedown", function (b) {
				s(b);
				a.bind(window, "mousemove", s);
				a.bind(window, "mouseup", i);
			});
			this.__saturation_field.appendChild(t);
			this.__selector.appendChild(this.__field_knob);
			this.__selector.appendChild(this.__saturation_field);
			this.__selector.appendChild(this.__hue_field);
			this.__hue_field.appendChild(this.__hue_knob);
			this.domElement.appendChild(this.__input);
			this.domElement.appendChild(this.__selector);
			this.updateDisplay();
		};
		h.superclass = e;
		f.extend(h.prototype, e.prototype, {
			updateDisplay: function updateDisplay() {
				var a = d(this.getValue());
				if (a !== false) {
					var e = false;
					f.each(c.COMPONENTS, function (b) {
						if (!f.isUndefined(a[b]) && !f.isUndefined(this.__color.__state[b]) && a[b] !== this.__color.__state[b]) return e = true, {};
					}, this);
					e && f.extend(this.__color.__state, a);
				}
				f.extend(this.__temp.__state, this.__color.__state);
				this.__temp.a = 1;
				var h = this.__color.v < 0.5 || this.__color.s > 0.5 ? 255 : 0,
				    j = 255 - h;
				f.extend(this.__field_knob.style, {
					marginLeft: 100 * this.__color.s - 7 + "px",
					marginTop: 100 * (1 - this.__color.v) - 7 + "px",
					backgroundColor: this.__temp.toString(),
					border: this.__field_knob_border + "rgb(" + h + "," + h + "," + h + ")"
				});
				this.__hue_knob.style.marginTop = (1 - this.__color.h / 360) * 100 + "px";
				this.__temp.s = 1;
				this.__temp.v = 1;
				b(this.__saturation_field, "left", "#fff", this.__temp.toString());
				f.extend(this.__input.style, {
					backgroundColor: this.__input.value = this.__color.toString(),
					color: "rgb(" + h + "," + h + "," + h + ")",
					textShadow: this.__input_textShadow + "rgba(" + j + "," + j + "," + j + ",.7)"
				});
			}
		});
		var j = ["-moz-", "-o-", "-webkit-", "-ms-", ""];
		return h;
	}(dat.controllers.Controller, dat.dom.dom, dat.color.Color = function (e, a, c, d) {
		function f(a, b, c) {
			Object.defineProperty(a, b, {
				get: function get() {
					if (this.__state.space === "RGB") return this.__state[b];
					n(this, b, c);
					return this.__state[b];
				}, set: function set(a) {
					if (this.__state.space !== "RGB") n(this, b, c), this.__state.space = "RGB";
					this.__state[b] = a;
				}
			});
		}

		function b(a, b) {
			Object.defineProperty(a, b, {
				get: function get() {
					if (this.__state.space === "HSV") return this.__state[b];
					h(this);
					return this.__state[b];
				}, set: function set(a) {
					if (this.__state.space !== "HSV") h(this), this.__state.space = "HSV";
					this.__state[b] = a;
				}
			});
		}

		function n(b, c, e) {
			if (b.__state.space === "HEX") b.__state[c] = a.component_from_hex(b.__state.hex, e);else if (b.__state.space === "HSV") d.extend(b.__state, a.hsv_to_rgb(b.__state.h, b.__state.s, b.__state.v));else throw "Corrupted color state";
		}

		function h(b) {
			var c = a.rgb_to_hsv(b.r, b.g, b.b);
			d.extend(b.__state, { s: c.s, v: c.v });
			if (d.isNaN(c.h)) {
				if (d.isUndefined(b.__state.h)) b.__state.h = 0;
			} else b.__state.h = c.h;
		}

		var j = function j() {
			this.__state = e.apply(this, arguments);
			if (this.__state === false) throw "Failed to interpret color arguments";
			this.__state.a = this.__state.a || 1;
		};
		j.COMPONENTS = "r,g,b,h,s,v,hex,a".split(",");
		d.extend(j.prototype, {
			toString: function toString() {
				return c(this);
			}, toOriginal: function toOriginal() {
				return this.__state.conversion.write(this);
			}
		});
		f(j.prototype, "r", 2);
		f(j.prototype, "g", 1);
		f(j.prototype, "b", 0);
		b(j.prototype, "h");
		b(j.prototype, "s");
		b(j.prototype, "v");
		Object.defineProperty(j.prototype, "a", {
			get: function get() {
				return this.__state.a;
			}, set: function set(a) {
				this.__state.a = a;
			}
		});
		Object.defineProperty(j.prototype, "hex", {
			get: function get() {
				if (!this.__state.space !== "HEX") this.__state.hex = a.rgb_to_hex(this.r, this.g, this.b);
				return this.__state.hex;
			}, set: function set(a) {
				this.__state.space = "HEX";
				this.__state.hex = a;
			}
		});
		return j;
	}(dat.color.interpret, dat.color.math = function () {
		var e;
		return {
			hsv_to_rgb: function hsv_to_rgb(a, c, d) {
				var e = a / 60 - Math.floor(a / 60),
				    b = d * (1 - c),
				    n = d * (1 - e * c),
				    c = d * (1 - (1 - e) * c),
				    a = [[d, c, b], [n, d, b], [b, d, c], [b, n, d], [c, b, d], [d, b, n]][Math.floor(a / 60) % 6];
				return { r: a[0] * 255, g: a[1] * 255, b: a[2] * 255 };
			}, rgb_to_hsv: function rgb_to_hsv(a, c, d) {
				var e = Math.min(a, c, d),
				    b = Math.max(a, c, d),
				    e = b - e;
				if (b == 0) return { h: NaN, s: 0, v: 0 };
				a = a == b ? (c - d) / e : c == b ? 2 + (d - a) / e : 4 + (a - c) / e;
				a /= 6;
				a < 0 && (a += 1);
				return { h: a * 360, s: e / b, v: b / 255 };
			}, rgb_to_hex: function rgb_to_hex(a, c, d) {
				a = this.hex_with_component(0, 2, a);
				a = this.hex_with_component(a, 1, c);
				return a = this.hex_with_component(a, 0, d);
			}, component_from_hex: function component_from_hex(a, c) {
				return a >> c * 8 & 255;
			}, hex_with_component: function hex_with_component(a, c, d) {
				return d << (e = c * 8) | a & ~(255 << e);
			}
		};
	}(), dat.color.toString, dat.utils.common), dat.color.interpret, dat.utils.common), dat.utils.requestAnimationFrame = function () {
		return window.webkitRequestAnimationFrame || window.mozRequestAnimationFrame || window.oRequestAnimationFrame || window.msRequestAnimationFrame || function (e) {
			window.setTimeout(e, 1E3 / 60);
		};
	}(), dat.dom.CenteredDiv = function (e, a) {
		var c = function c() {
			this.backgroundElement = document.createElement("div");
			a.extend(this.backgroundElement.style, {
				backgroundColor: "rgba(0,0,0,0.8)",
				top: 0,
				left: 0,
				display: "none",
				zIndex: "1000",
				opacity: 0,
				WebkitTransition: "opacity 0.2s linear"
			});
			e.makeFullscreen(this.backgroundElement);
			this.backgroundElement.style.position = "fixed";
			this.domElement = document.createElement("div");
			a.extend(this.domElement.style, {
				position: "fixed",
				display: "none",
				zIndex: "1001",
				opacity: 0,
				WebkitTransition: "-webkit-transform 0.2s ease-out, opacity 0.2s linear"
			});
			document.body.appendChild(this.backgroundElement);
			document.body.appendChild(this.domElement);
			var c = this;
			e.bind(this.backgroundElement, "click", function () {
				c.hide();
			});
		};
		c.prototype.show = function () {
			var c = this;
			this.backgroundElement.style.display = "block";
			this.domElement.style.display = "block";
			this.domElement.style.opacity = 0;
			this.domElement.style.webkitTransform = "scale(1.1)";
			this.layout();
			a.defer(function () {
				c.backgroundElement.style.opacity = 1;
				c.domElement.style.opacity = 1;
				c.domElement.style.webkitTransform = "scale(1)";
			});
		};
		c.prototype.hide = function () {
			var a = this,
			    c = function c() {
				a.domElement.style.display = "none";
				a.backgroundElement.style.display = "none";
				e.unbind(a.domElement, "webkitTransitionEnd", c);
				e.unbind(a.domElement, "transitionend", c);
				e.unbind(a.domElement, "oTransitionEnd", c);
			};
			e.bind(this.domElement, "webkitTransitionEnd", c);
			e.bind(this.domElement, "transitionend", c);
			e.bind(this.domElement, "oTransitionEnd", c);
			this.backgroundElement.style.opacity = 0;
			this.domElement.style.opacity = 0;
			this.domElement.style.webkitTransform = "scale(1.1)";
		};
		c.prototype.layout = function () {
			this.domElement.style.left = window.innerWidth / 2 - e.getWidth(this.domElement) / 2 + "px";
			this.domElement.style.top = window.innerHeight / 2 - e.getHeight(this.domElement) / 2 + "px";
		};
		return c;
	}(dat.dom.dom, dat.utils.common), dat.dom.dom, dat.utils.common);

	return dat;
}.call(exports, __webpack_require__, exports, module),
				__WEBPACK_AMD_DEFINE_RESULT__ !== undefined && (module.exports = __WEBPACK_AMD_DEFINE_RESULT__));

/***/ })

});
//# sourceMappingURL=23.bundle.js.map