odoo.define('l10n_pe_currency.TopButton', function (require) {
    "use strict";
 
    var core = require('web.core');
    var SystrayMenu = require('web.SystrayMenu');
    var Widget = require('web.Widget');
    var QWeb = core.qweb;
    var ajax = require('web.ajax');
 
 var MySystrayWidget = Widget.extend({
    template: 'TopButton_systray',
    events: {
        "click .systray_click": 'button_click'
    },
 
    button_click: function (e) {
        var self = this;
        e.preventDefault();
        self.do_action({
            name: 'Asistente de Consulta de Tipo de Cambio',
            type: 'ir.actions.act_window',
            res_model: 'money.exchange.query',
            view_type: 'form',
            view_mode: 'form',
            view_id: 'l10n_pe_currency.money_exchange_query',
            views: [[false, 'form']],
            target: 'new'
        }, {
            on_reverse_breadcrumb: function () {
                self.update_control_panel({clear: true, hidden: true});
            }
        });
    }
 });
 SystrayMenu.Items.push(MySystrayWidget);
 });