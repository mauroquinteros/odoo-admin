odoo.define('technical_customizer.wizard_menu', function (require) {
    "use strict";

    var page = require('web.UserMenu');
    var ajax = require('web.ajax');
    var rpc = require('web.rpc');
    var usepage = page.include({
        _onMenuAgency: function () {
            var self = this;
            var session = this.getSession();
            this.trigger_up('clear_uncommitted_changes', {
                callback: function () {
                    self._rpc({
                        model: "res.users",
                        method: "change_agency_get"
                    })
                        .then(function (result) {
                            result.res_id = session.uid;
                            self.do_action(result);
                        });
                },
            });
        },
    })
    return AgencySubMenu;
});