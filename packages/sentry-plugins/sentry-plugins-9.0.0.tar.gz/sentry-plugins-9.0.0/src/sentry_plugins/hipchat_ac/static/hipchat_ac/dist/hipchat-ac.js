/******/ (function(modules) { // webpackBootstrap
/******/ 	// The module cache
/******/ 	var installedModules = {};
/******/
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/
/******/ 		// Check if module is in cache
/******/ 		if(installedModules[moduleId])
/******/ 			return installedModules[moduleId].exports;
/******/
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = installedModules[moduleId] = {
/******/ 			i: moduleId,
/******/ 			l: false,
/******/ 			exports: {}
/******/ 		};
/******/
/******/ 		// Execute the module function
/******/ 		modules[moduleId].call(module.exports, module, module.exports, __webpack_require__);
/******/
/******/ 		// Flag the module as loaded
/******/ 		module.l = true;
/******/
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/
/******/
/******/ 	// expose the modules object (__webpack_modules__)
/******/ 	__webpack_require__.m = modules;
/******/
/******/ 	// expose the module cache
/******/ 	__webpack_require__.c = installedModules;
/******/
/******/ 	// identity function for calling harmony imports with the correct context
/******/ 	__webpack_require__.i = function(value) { return value; };
/******/
/******/ 	// define getter function for harmony exports
/******/ 	__webpack_require__.d = function(exports, name, getter) {
/******/ 		if(!__webpack_require__.o(exports, name)) {
/******/ 			Object.defineProperty(exports, name, {
/******/ 				configurable: false,
/******/ 				enumerable: true,
/******/ 				get: getter
/******/ 			});
/******/ 		}
/******/ 	};
/******/
/******/ 	// getDefaultExport function for compatibility with non-harmony modules
/******/ 	__webpack_require__.n = function(module) {
/******/ 		var getter = module && module.__esModule ?
/******/ 			function getDefault() { return module['default']; } :
/******/ 			function getModuleExports() { return module; };
/******/ 		__webpack_require__.d(getter, 'a', getter);
/******/ 		return getter;
/******/ 	};
/******/
/******/ 	// Object.prototype.hasOwnProperty.call
/******/ 	__webpack_require__.o = function(object, property) { return Object.prototype.hasOwnProperty.call(object, property); };
/******/
/******/ 	// __webpack_public_path__
/******/ 	__webpack_require__.p = "";
/******/
/******/ 	// Load entry module and return exports
/******/ 	return __webpack_require__(__webpack_require__.s = 3);
/******/ })
/************************************************************************/
/******/ ([
/* 0 */
/***/ (function(module, exports) {

module.exports = React;

/***/ }),
/* 1 */
/***/ (function(module, exports) {

module.exports = Sentry;

/***/ }),
/* 2 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
  value: true
});

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _get = function get(object, property, receiver) { if (object === null) object = Function.prototype; var desc = Object.getOwnPropertyDescriptor(object, property); if (desc === undefined) { var parent = Object.getPrototypeOf(object); if (parent === null) { return undefined; } else { return get(parent, property, receiver); } } else if ("value" in desc) { return desc.value; } else { var getter = desc.get; if (getter === undefined) { return undefined; } return getter.call(receiver); } };

var _react = __webpack_require__(0);

var _react2 = _interopRequireDefault(_react);

var _sentry = __webpack_require__(1);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var Settings = function (_plugins$BasePlugin$D) {
  _inherits(Settings, _plugins$BasePlugin$D);

  function Settings(props) {
    _classCallCheck(this, Settings);

    var _this = _possibleConstructorReturn(this, (Settings.__proto__ || Object.getPrototypeOf(Settings)).call(this, props));

    _this.onTest = _this.onTest.bind(_this);
    _this.fetchData = _this.fetchData.bind(_this);

    Object.assign(_this.state, {
      tenants: null,
      tenantsLoading: true,
      tenantsError: false
    });
    return _this;
  }

  _createClass(Settings, [{
    key: 'fetchData',
    value: function fetchData() {
      var _this2 = this;

      _get(Settings.prototype.__proto__ || Object.getPrototypeOf(Settings.prototype), 'fetchData', this).call(this);

      this.api.request(this.getPluginEndpoint() + 'tenants/', {
        success: function success(data) {
          _this2.setState({
            tenants: data,
            tenantsLoading: false,
            tenantsError: false
          });
        },
        error: function error(_error) {
          _this2.setState({
            tenantsLoading: false,
            tenantsError: true
          });
        }
      });
    }

    // TODO(dcramer): move this to Sentry core

  }, {
    key: 'onTest',
    value: function onTest() {
      var _this3 = this;

      var loadingIndicator = _sentry.IndicatorStore.add(_sentry.i18n.t('Saving changes..'));
      this.api.request(this.getPluginEndpoint() + 'test-config/', {
        method: 'POST',
        success: function success(data) {
          _this3.setState({
            testResults: data
          });
        },
        error: function error(_error2) {
          _this3.setState({
            testResults: {
              error: true,
              message: 'An unknown error occurred while testing this integration.'
            }
          });
        },
        complete: function complete() {
          _sentry.IndicatorStore.remove(loadingIndicator);
        }
      });
    }
  }, {
    key: 'renderLink',
    value: function renderLink(url, metadata) {
      var tenants = this.state.tenants;
      if (!tenants || !tenants.length) {
        if (metadata.onPremise) {
          return _react2.default.createElement(
            'div',
            null,
            _react2.default.createElement(
              'p',
              null,
              'Installing this integration will allow you to receive notifications for and assign team members to new Sentry errors within HipChat rooms. To install the integration, click the button below.'
            ),
            _react2.default.createElement(
              'p',
              null,
              _react2.default.createElement(
                'a',
                { href: url,
                  className: 'btn btn-primary',
                  target: '_blank' },
                'Enable Integration'
              )
            )
          );
        } else {
          return _react2.default.createElement(
            'div',
            null,
            _react2.default.createElement(
              'p',
              null,
              'To add the Sentry integration to HipChat click on "Install an integration from a descriptor URL" on your room in HipChat and add the following descriptor URL:'
            ),
            _react2.default.createElement(
              'pre',
              null,
              metadata.descriptor
            )
          );
        }
      }
    }
  }, {
    key: 'renderTenants',
    value: function renderTenants(url) {
      var _this4 = this;

      var tenants = this.state.tenants;
      if (this.state.tenantsLoading) return _react2.default.createElement(_sentry.LoadingIndicator, null);else if (this.state.tenantsError) return _react2.default.createElement(_sentry.LoadingError, { onRetry: this.fetchData });
      if (!tenants.length) return null;

      var isTestable = this.props.plugin.isTestable;
      return _react2.default.createElement(
        'div',
        null,
        _react2.default.createElement(
          'h4',
          null,
          'Active Rooms'
        ),
        _react2.default.createElement(
          'table',
          { className: 'table', style: { fontSize: 14 } },
          _react2.default.createElement(
            'thead',
            null,
            _react2.default.createElement(
              'tr',
              null,
              _react2.default.createElement(
                'th',
                null,
                'Room'
              ),
              _react2.default.createElement(
                'th',
                null,
                'By'
              ),
              isTestable && _react2.default.createElement(
                'th',
                null,
                'Test'
              )
            )
          ),
          _react2.default.createElement(
            'tbody',
            null,
            tenants.map(function (tenant) {
              return _react2.default.createElement(
                'tr',
                { key: tenant.id },
                _react2.default.createElement(
                  'td',
                  null,
                  _react2.default.createElement(
                    'strong',
                    null,
                    tenant.room.name
                  ),
                  _react2.default.createElement('br', null),
                  _react2.default.createElement(
                    'small',
                    null,
                    '(id: ',
                    tenant.room.id,
                    '; owner: ',
                    tenant.room.owner.name,
                    ')'
                  )
                ),
                _react2.default.createElement(
                  'td',
                  null,
                  tenant.authUser && tenant.authUser.username || '(unknown)'
                ),
                isTestable && _react2.default.createElement(
                  'td',
                  null,
                  _react2.default.createElement(
                    'a',
                    { className: 'btn btn-default btn-sm',
                      onClick: _this4.onTest },
                    'Test'
                  )
                )
              );
            })
          )
        ),
        _react2.default.createElement(
          'p',
          null,
          'To manage HipChat notifications or the rooms in which Sentry errors appear, visit the',
          _react2.default.createElement(
            'a',
            { href: url, target: '_blank' },
            ' integration configuration page'
          ),
          '.'
        ),
        _react2.default.createElement(
          'p',
          null,
          _react2.default.createElement(
            'b',
            null,
            'Disabling the plugin here will delete all associations and will disable notifications to all HipChat Rooms'
          )
        )
      );
    }
  }, {
    key: 'render',
    value: function render() {
      var metadata = this.props.plugin.metadata;

      var url = '/plugins/hipchat-ac/start/' + this.props.organization.slug + '/' + this.props.project.slug;
      return _react2.default.createElement(
        'div',
        { className: 'ref-hipchat-settings' },
        this.state.testResults && _react2.default.createElement(
          'div',
          { className: 'ref-hipchat-test-results' },
          _react2.default.createElement(
            'h4',
            null,
            'Test Results'
          ),
          this.state.testResults.error ? _react2.default.createElement(
            'div',
            { className: 'alert alert-block alert-error' },
            this.state.testResults.message
          ) : _react2.default.createElement(
            'div',
            { className: 'alert alert-block alert-success' },
            this.state.testResults.message
          )
        ),
        this.renderLink(url, metadata),
        this.renderTenants(url)
      );
    }
  }]);

  return Settings;
}(_sentry.plugins.BasePlugin.DefaultSettings);

exports.default = Settings;
module.exports = exports['default'];

/***/ }),
/* 3 */
/***/ (function(module, exports, __webpack_require__) {

"use strict";


Object.defineProperty(exports, "__esModule", {
    value: true
});

var _extends = Object.assign || function (target) { for (var i = 1; i < arguments.length; i++) { var source = arguments[i]; for (var key in source) { if (Object.prototype.hasOwnProperty.call(source, key)) { target[key] = source[key]; } } } return target; };

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _react = __webpack_require__(0);

var _react2 = _interopRequireDefault(_react);

var _sentry = __webpack_require__(1);

var _settings = __webpack_require__(2);

var _settings2 = _interopRequireDefault(_settings);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var Hipchat = function (_plugins$BasePlugin) {
    _inherits(Hipchat, _plugins$BasePlugin);

    function Hipchat() {
        _classCallCheck(this, Hipchat);

        return _possibleConstructorReturn(this, (Hipchat.__proto__ || Object.getPrototypeOf(Hipchat)).apply(this, arguments));
    }

    _createClass(Hipchat, [{
        key: 'renderSettings',
        value: function renderSettings(props) {
            return _react2.default.createElement(_settings2.default, _extends({ plugin: this }, props));
        }
    }]);

    return Hipchat;
}(_sentry.plugins.BasePlugin);

Hipchat.displayName = 'Hipchat';

_sentry.plugins.add('hipchat-ac', Hipchat);

exports.default = Hipchat;
module.exports = exports['default'];

/***/ })
/******/ ]);
//# sourceMappingURL=hipchat-ac.js.map