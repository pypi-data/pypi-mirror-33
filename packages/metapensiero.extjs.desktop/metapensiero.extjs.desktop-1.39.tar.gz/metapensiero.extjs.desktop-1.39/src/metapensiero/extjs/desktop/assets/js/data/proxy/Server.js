// -*- coding: utf-8 -*-
// :Project:   metapensiero.extjs.desktop -- Customize Ext.data.proxy.Server
// :Created:   gio 16 mar 2017 09:04:11 CET
// :Author:    Lele Gaifax <lele@metapensiero.it>
// :License:   GNU General Public License version 3 or later
// :Copyright: © 2017 Lele Gaifax
//

/*jsl:declare Ext*/
/*jsl:declare _*/

// Reimplement ExtJS 4.2.1 Ext.data.proxy.Server.encodeFilters to send the filter operator

Ext.define('MP.data.proxy.Server', {
    override: 'Ext.data.proxy.Server',

    encodeFilters: function(filters) {
        var min = [],
            length = filters.length,
            i = 0;

        for (; i < length; i++) {
            min[i] = {
                property: filters[i].property,
                value: filters[i].value
            };
            if (filters[i].operator) {
                min[i].operator = filters[i].operator;
            }
        }
        return this.applyEncoding(min);
    }
});
