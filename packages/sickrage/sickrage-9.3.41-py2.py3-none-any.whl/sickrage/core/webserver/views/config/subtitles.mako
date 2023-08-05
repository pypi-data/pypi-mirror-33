<%inherit file="../layouts/config.mako"/>
<%def name='formaction()'><% return 'saveSubtitles' %></%def>
<%!
    import sickrage
    import sickrage.subtitles
    from sickrage.core.helpers import anon_url
%>
<%block name="tabs">
    <li class="active"><a data-toggle="tab" href="#core-tab-pane1">${_('Subtitles Search')}</a></li>
    <li><a data-toggle="tab" href="#core-tab-pane2">${_('Subtitles Plugin')}</a></li>
    <li><a data-toggle="tab" href="#core-tab-pane3">${_('Plugin Settings')}</a></li>
</%block>
<%block name="pages">
    <%
        providerLoginDict = {'legendastv': {'user': sickrage.app.config.legendastv_user, 'pass': sickrage.app.config.legendastv_pass},
                            'itasa': {'user': sickrage.app.config.itasa_user, 'pass': sickrage.app.config.itasa_pass},
                            'addic7ed': {'user': sickrage.app.config.addic7ed_user, 'pass': sickrage.app.config.addic7ed_pass},
                            'opensubtitles': {'user': sickrage.app.config.opensubtitles_user, 'pass': sickrage.app.config.opensubtitles_pass}}
    %>
    <div id="core-tab-pane1" class="tab-pane fade in active">
        <div class="row tab-pane">
            <div class="col-lg-3 col-md-4 col-sm-4 col-xs-12 tab-pane-desc">
                <h3>${_('Subtitles Search')}</h3>
                <p>${_('Settings that dictate how SickRage handles subtitles search results.')}</p>
            </div>

            <fieldset class="col-lg-9 col-md-8 col-sm-8 col-xs-12 tab-pane-list">
                <div class="row field-pair">
                    <div class="col-lg-3 col-md-4 col-sm-5 col-xs-12">
                        <label class="component-title">${_('Enabled')}</label>
                    </div>
                    <div class="col-lg-9 col-md-8 col-sm-7 col-xs-12 component-desc">
                        <input type="checkbox"
                               class="enabler" ${('', ' checked="checked"')[bool(sickrage.app.config.use_subtitles)]}
                               id="use_subtitles" name="use_subtitles">
                        <label for="use_subtitles">${_('Search Subtitles')}</label>
                    </div>
                </div>

                <div id="content_use_subtitles">
                    <div class="row field-pair">
                        <div class="col-lg-3 col-md-4 col-sm-5 col-xs-12">
                            <label class="component-title">${_('Subtitle Languages')}</label>
                        </div>
                        <div class="col-lg-9 col-md-8 col-sm-7 col-xs-12 component-desc">
                            <div class="input-group input350">
                                <div class="input-group-addon">
                                    <span class="glyphicon glyphicon-flag"></span>
                                </div>
                                <input class="form-control "
                                       id="subtitles_languages"
                                       name="subtitles_languages"
                                       title="Select subtitle languages"
                                       value="${','.join(code for code in sickrage.subtitles.wanted_languages())}"/>
                            </div>
                        </div>
                    </div>
                    <div class="row field-pair">
                        <div class="col-lg-3 col-md-4 col-sm-5 col-xs-12">
                            <label class="component-title">${_('Subtitles History')}</label>
                        </div>
                        <div class="col-lg-9 col-md-8 col-sm-7 col-xs-12 component-desc">
                            <input type="checkbox" name="subtitles_history"
                                   id="subtitles_history" ${('', 'checked')[bool(sickrage.app.config.subtitles_history)]}/>
                            <label for="subtitles_history">
                                <p>${_('Log downloaded Subtitle on History page?')}</p>
                            </label>
                        </div>
                    </div>
                    <div class="row field-pair">
                        <div class="col-lg-3 col-md-4 col-sm-5 col-xs-12">
                            <label class="component-title">${_('Subtitles Multi-Language')}</label>
                        </div>
                        <div class="col-lg-9 col-md-8 col-sm-7 col-xs-12 component-desc">
                            <input type="checkbox" name="subtitles_multi"
                                   id="subtitles_multi" ${('', 'checked')[bool(sickrage.app.config.subtitles_multi)]}/>
                            <label for="subtitles_multi">
                                <p>${_('Append language codes to subtitle filenames?')}</p>
                            </label>
                        </div>
                    </div>
                    <div class="row field-pair">
                        <div class="col-lg-3 col-md-4 col-sm-5 col-xs-12">
                            <label class="component-title">${_('Embedded Subtitles')}</label>
                        </div>
                        <div class="col-lg-9 col-md-8 col-sm-7 col-xs-12 component-desc">
                            <input type="checkbox" name="embedded_subtitles_all"
                                   id="embedded_subtitles_all" ${('', 'checked')[bool(sickrage.app.config.embedded_subtitles_all)]}/>
                            <label for="embedded_subtitles_all">
                                ${_('Ignore subtitles embedded inside video file?')}<br/>
                                <b>${_('Warning:')}</b> ${_('this will ignore <u>all</u> embedded subtitles for every video file!')}
                            </label>
                        </div>
                    </div>
                    <div class="row field-pair">
                        <div class="col-lg-3 col-md-4 col-sm-5 col-xs-12">
                            <label class="component-title">${_('Hearing Impaired Subtitles')}</label>
                        </div>
                        <div class="col-lg-9 col-md-8 col-sm-7 col-xs-12 component-desc">
                            <input type="checkbox" name="subtitles_hearing_impaired"
                                   id="subtitles_hearing_impaired" ${('', 'checked')[bool(sickrage.app.config.subtitles_hearing_impaired)]}/>
                            <label for="subtitles_hearing_impaired">
                                <p>${_('Download hearing impaired style subtitles?')}</p>
                            </label>
                        </div>
                    </div>
                    <div class="row field-pair">
                        <div class="col-lg-3 col-md-4 col-sm-5 col-xs-12">
                            <label class="component-title">${_('Subtitle Directory')}</label>
                        </div>
                        <div class="col-lg-9 col-md-8 col-sm-7 col-xs-12 component-desc">
                            <div class="input-group input350">
                                <div class="input-group-addon">
                                    <span class="glyphicon glyphicon-folder-open"></span>
                                </div>
                                <input value="${sickrage.app.config.subtitles_dir}"
                                       id="subtitles_dir"
                                       name="subtitles_dir" class="form-control"
                                       autocapitalize="off"/>
                            </div>
                            <label for="subtitles_dir">
                                ${_('The directory where SickRage should store your')}
                                <i>${_('Subtitles')}</i> ${_('files.')}<br/>
                                <b>${_('NOTE:')}</b> ${_('Leave empty if you want store subtitle in episode path.')}
                            </label>
                        </div>
                    </div>
                    <div class="row field-pair">
                        <div class="col-lg-3 col-md-4 col-sm-5 col-xs-12">
                            <label class="component-title">${_('Subtitle Find Frequency')}</label>
                        </div>
                        <div class="col-lg-9 col-md-8 col-sm-7 col-xs-12 component-desc">
                            <div class="input-group input350">
                                <div class="input-group-addon">
                                    <span class="glyphicon glyphicon-time"></span>
                                </div>
                                <input type="number" name="subtitles_finder_frequency"
                                       value="${sickrage.app.config.subtitle_searcher_freq}" hours="1"
                                       placeholder="${_('1')}"
                                       title="time in hours between scans"
                                       class="form-control"/>
                                <div class="input-group-addon">
                                    hours
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="row field-pair">
                        <div class="col-lg-3 col-md-4 col-sm-5 col-xs-12">
                            <label class="component-title">${_('Extra Scripts')}</label>
                        </div>
                        <div class="col-lg-9 col-md-8 col-sm-7 col-xs-12 component-desc">
                            <div class="input-group input350">
                                <div class="input-group-addon">
                                    <span class="glyphicon glyphicon-file"></span>
                                </div>
                                <input name="subtitles_extra_scripts" id="subtitles_extra_scripts"
                                       value="<% '|'.join(sickrage.app.config.subtitles_extra_scripts) %>"
                                       class="form-control" autocapitalize="off"/>
                            </div>
                            <label for="subtitles_extra_scripts">
                                <b>${_('NOTE:')}</b>
                                <ul>
                                    <li>
                                        ${_('See')}
                                        <a href="https://git.sickrage.ca/SiCKRAGE/sickrage/wikis/Subtitle%20Scripts">
                                            <span style="color: red; "><b>${_('Wiki')}</b></span>
                                        </a>
                                        ${_('for a script arguments description.')}
                                    </li>
                                    <li>
                                        ${_('Additional scripts separated by')} <b>|</b>.
                                    </li>
                                    <li>
                                        ${_('Scripts are called after each episode has searched and downloaded subtitles.')}
                                    </li>
                                    <li>
                                        ${_('For any scripted languages, include the interpreter executable before the script. See the following example:')}
                                    </li>
                                    <ul>
                                        <li>
                                            ${_('For Windows:')}
                                            <pre>C:\Python27\pythonw.exe C:\Script\test.py</pre>
                                        </li>
                                        <li>
                                            ${_('For Linux:')}
                                            <pre>python /Script/test.py</pre>
                                        </li>
                                    </ul>
                                </ul>
                            </label>
                        </div>
                    </div>

                    <div class="row">
                        <div class="col-md-12">
                            <input type="submit" class="btn config_submitter" value="${_('Save Changes')}"/>
                        </div>
                    </div>
                </div>
            </fieldset>
        </div>
    </div><!-- /tab-pane1 //-->

    <div id="core-tab-pane2" class="tab-pane fade">
        <div class="row tab-pane">
            <div class="col-lg-3 col-md-4 col-sm-4 col-xs-12 tab-pane-desc">
                <h3>${_('Subtitle Plugins')}</h3>
                <p>${_('Check off and drag the plugins into the order you want them to be used.')}</p>
                <p class="note">${_('At least one plugin is required.')}</p>
                <p class="note"><span style="font-size: 16px;">*</span> ${_('Web-scraping plugin')}</p>
            </div>

            <fieldset class="col-lg-9 col-md-8 col-sm-8 col-xs-12 tab-pane-list">
                <div class="row">
                    <div class="col-md-12">
                        <ul id="service_order_list">
                            % for curService in sickrage.subtitles.sortedServiceList():
                                <li class="ui-state-default" id="${curService['name']}">
                                    <input type="checkbox" id="enable_${curService['name']}"
                                           class="service_enabler" ${('', 'checked')[curService['enabled'] == True]}/>
                                    <label for="enable_${curService['name']}">
                                        <a href="${anon_url(curService['url'])}" class="imgLink" target="_new">
                                            <img src="${srWebRoot}/images/subtitles/${curService['image']}"
                                                 alt="${curService['url']}" title="${curService['url']}" width="16"
                                                 height="16" style="vertical-align:middle;"/>
                                        </a>
                                        <span style="vertical-align:middle;">${curService['name'].capitalize()}</span>
                                        <i class="fa fa-arrows-v blue-text pull-right"
                                           style="vertical-align:middle;"></i>
                                        <i class="fa ${('fa-unlock green-text','fa-lock red-text')[curService['name'] in providerLoginDict]} pull-right"
                                           style="vertical-align:middle;"></i>
                                    </label>
                                </li>
                            % endfor
                        </ul>
                    </div>
                </div>

                <input type="hidden" name="service_order" id="service_order"
                       value="<% ''.join(['%s:%d' % (x['name'], x['enabled']) for x in sickrage.subtitles.sortedServiceList()])%>"/>

                <div class="row">
                    <div class="col-md-12">
                        <input type="submit" class="btn config_submitter" value="${_('Save Changes')}"/>
                    </div>
                </div>
            </fieldset>
        </div>
    </div><!-- /tab-pane2 //-->

    <div id="core-tab-pane3" class="tab-pane fade">
        <div class="row tab-pane">
            <div class="col-lg-3 col-md-4 col-sm-4 col-xs-12 tab-pane-desc">
                <h3>${_('Subtitle Settings')}</h3>
                <p>${_('Set user and password for each provider')}</p>
            </div>

            <fieldset class="col-lg-9 col-md-8 col-sm-8 col-xs-12 tab-pane-list">
                % for curService in sickrage.subtitles.sortedServiceList():
                    % if curService['name'] in providerLoginDict.keys():
                        <div class="row field-pair">
                            <div class="col-lg-3 col-md-4 col-sm-5 col-xs-12">
                                <label class="component-title">${curService['name'].capitalize()} ${_('User Name')}</label>
                            </div>
                            <div class="col-lg-9 col-md-8 col-sm-7 col-xs-12 component-desc">
                                <div class="input-group input350">
                                    <div class="input-group-addon">
                                        <span class="glyphicon glyphicon-user"></span>
                                    </div>
                                    <input name="${curService['name']}_user"
                                           id="${curService['name']}_user"
                                           value="${providerLoginDict[curService['name']]['user']}"
                                           title="${curService['name'].capitalize()} User Name"
                                           class="form-control" autocapitalize="off"/>
                                </div>
                            </div>
                        </div>
                        <div class="row field-pair">
                            <div class="col-lg-3 col-md-4 col-sm-5 col-xs-12">
                                <label class="component-title">${curService['name'].capitalize()} ${_('Password')}</label>
                            </div>
                            <div class="col-lg-9 col-md-8 col-sm-7 col-xs-12 component-desc">
                                <div class="input-group input350">
                                    <div class="input-group-addon">
                                        <span class="glyphicon glyphicon-lock"></span>
                                    </div>
                                    <input type="password" name="${curService['name']}_pass"
                                           id="${curService['name']}_pass"
                                           value="${providerLoginDict[curService['name']]['pass']}"
                                           title="${curService['name'].capitalize()} Password"
                                           class="form-control" autocapitalize="off"/>
                                </div>
                            </div>
                        </div>
                    % endif
                % endfor
                <div class="row">
                    <div class="col-md-12">
                        <input type="submit" class="btn config_submitter" value="${_('Save Changes')}"/>
                    </div>
                </div>
            </fieldset>
        </div>
    </div><!-- /tab-pane3 //-->
</%block>