(function(){
    Ext.onReady(function(){
        var accountRouter = Zenoss.remote.AccountRouter;
        var servicesRouter = Zenoss.remote.ServicesRouter;

        Ext.define('com.pagerduty.ImportServicePanel', {
            extend: 'Ext.form.Panel',
            alias: 'widget.com-pagerduty-import-service-panel',
            title: 'PagerDuty Settings',
            id: 'pdSettingsPanel',
            defaults: {
                listeners: {
                    specialkey: function(field, event) {
                        if (event.getKey() == event.ENTER) {
                           field.up('form').submit();
                        }
                    }
                }
            },
            items: [
                {
                    fieldLabel: 'PagerDuty Subdomain',
                    labelWidth: 150,
                    name: 'subdomain',
                    width: 400,
                    xtype: 'textfield'
                },
                {
                    fieldLabel: 'API Access Key',
                    labelWidth: 150,
                    name: 'apiAccessKey',
                    width: 400,
                    xtype: 'textfield'
                },
                {
                    xtype: 'button',
                    text: 'Apply',
                    style: {
                        marginBottom: '15px'
                    },
                    handler: function() {
                        var panel = Ext.getCmp('pdSettingsPanel');
                        panel.submit();
                    }
                },
                {
                    xtype: 'grid',
                    name: 'pd_service_grid',
                    title: 'PagerDuty Services',
                    columns: [{header: 'Service Name', dataIndex: 'name', flex: 1}],
                    sortableColumns: false,
                    enableColumnHide: false,
                    enableColumnMove: false,
                    enableColumnResize: true,
                    hideHeaders: true,
                    store: Ext.create('Ext.data.Store', {
                        storeId: 'pdServiceStore',
                        model: 'pagerduty.model.Service'
                    }),
                    flex: 1
                },
            ],
            onRender: function() {
                this.callParent(arguments);
                this.load();
            },
            load: function() {
                accountRouter.getAccountSettings({}, function(result) {
                    if (!result.success)
                        return;

                    this.getForm().setValues(result.data);

                    if (result.data.apiAccessKey && result.data.subdomain) {
                        servicesRouter.getServices({wantsMessages: true}, function(result) {
                            var pdServiceStore = Ext.data.StoreManager.lookup('pdServiceStore');
                            pdServiceStore.loadData((result.success && result.data) ? result.data : []);
                        }, this);
                    }
                }, this);
            },
            submit: function() {
                var values = this.getForm().getValues();
                accountRouter.updateAccountSettings(values, function(result) {
                    var pdServiceStore = Ext.data.StoreManager.lookup('pdServiceStore');
                    pdServiceStore.loadData((result.success && result.data) ? result.data : []);
                });
            },
        });

        var settings = Ext.create(com.pagerduty.ImportServicePanel, {
            renderTo: 'import-pagerduty-services'
        });

    }); // End Ext.onReady.
})(); // End closure.
