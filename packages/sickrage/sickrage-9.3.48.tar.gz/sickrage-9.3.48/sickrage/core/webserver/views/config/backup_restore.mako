<%inherit file="../layouts/config.mako"/>
<%def name='formaction()'><% return 'backuprestore' %></%def>
<%block name="tabs">
    <li class="active"><a data-toggle="tab" href="#core-tab-pane1">${_('Backup')}</a></li>
    <li><a data-toggle="tab" href="#core-tab-pane2">${_('Restore')}</a></li>
</%block>
<%block name="pages">
    <div id="core-tab-pane1" class="tab-pane fade in active clearfix">
        <div class="col-lg-3 col-md-4 col-sm-4 col-xs-12 tab-pane-desc">
            <h3>${_('Backup')}</h3>
            <p><b>${_('Backup your main database file and config')}</b></p>
        </div>

        <fieldset class="col-lg-9 col-md-8 col-sm-8 col-xs-12 tab-pane-list">
            <div class="row field-pair">
                <div class="col-md-12 component-desc">
                    <div class="input-group input350">
                        <input name="backupDir" id="backupDir" class="form-control"
                               placeholder="${_('Select the folder you wish to save your backup file to')}"
                               autocapitalize="off"/>
                        <div class="input-group-addon">
                            <a href="#" class="fa fa-download" title="${_('Backup')}" id="Backup"></a>
                        </div>
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="col-md-12">
                    <div class="Backup" id="Backup-result"></div>
                </div>
            </div>
        </fieldset>
    </div><!-- /tab-pane1 //-->

    <div id="core-tab-pane2" class="tab-pane fade clearfix">
        <div class="col-lg-3 col-md-4 col-sm-4 col-xs-12 tab-pane-desc">
            <h3>${_('Restore')}</h3>
            <p><b>${_('Restore your main database file and config')}</b></p>
        </div>
        <fieldset class="col-lg-9 col-md-8 col-sm-8 col-xs-12 tab-pane-list">
            <div class="row field-pair">
                <div class="col-md-12 component-desc">
                    <div class="row">
                        <div class="col-md-12">
                            <div class="input-group input350">
                                <input name="backupFile" id="backupFile"
                                       placeholder="${_('Select the backup file you wish to restore')}"
                                       class="form-control" autocapitalize="off"/>
                                <div class="input-group-addon">
                                    <a href="#" class="fa fa-upload" title="${_('Restore')}" id="Restore"></a>
                                </div>
                            </div>
                        </div>
                    </div>

                    <br/>

                    <div class="row">
                        <div class="col-md-12">
                            <input type="checkbox" name="restore_database" id="restore_database" checked/>
                            <label for="restore_database">
                                ${_('Restore database files')}
                            </label>
                        </div>
                    </div>

                    <div class="row">
                        <div class="col-md-12">
                            <input type="checkbox" name="restore_config" id="restore_config" checked/>
                            <label for="restore_config">
                                ${_('Restore configuration file')}
                            </label>
                        </div>
                    </div>

                    <div class="row">
                        <div class="col-md-12">
                            <input type="checkbox" name="restore_cache" id="restore_cache" checked/>
                            <label for="restore_cache">
                                ${_('Restore cache files')}
                            </label>
                        </div>
                    </div>
                </div>
            </div>
            <div class="row">
                <div class="col-md-12">
                    <div class="Restore" id="Restore-result"></div>
                </div>
            </div>
        </fieldset>
    </div><!-- /tab-pane2 //-->
</%block>
