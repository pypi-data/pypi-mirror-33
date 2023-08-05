<%inherit file="../layouts/config.mako"/>
<%def name='formaction()'><% return 'saveQualities' %></%def>
<%!
    import sickrage
%>

<%block name="tabs">
    <li class="active"><a data-toggle="tab" href="#core-tab-pane1">${_('Quality Sizes')}</a></li>
</%block>

<%block name="pages">
    <%namespace file="../includes/quality_defaults.mako" import="renderQualityPill"/>
    <div id="core-tab-pane1" class="tab-pane fade in active">
        <div class="row tab-pane">
            <div class="col-lg-3 col-md-4 col-sm-4 col-xs-12 tab-pane-desc">
                <h3>${_('Quality Sizes')}</h3>
                <p>${_('Use default qualitiy sizes or specify custom ones per quality definition.')}</p>
                <div>
                    <p class="note">
                        ${_('Settings represent maximum size allowed per episode video file.')}
                    </p>
                </div>
            </div>
            <fieldset class="col-lg-9 col-md-8 col-sm-8 col-xs-12 tab-pane-list">
                % for qtype, qsize in sickrage.app.config.quality_sizes.items():
                    % if qsize:
                        <div class="row field-pair">
                            <div class="col-lg-3 col-md-4 col-sm-5 col-xs-12">
                                <label class="component-title">${renderQualityPill(qtype)}</label>
                            </div>
                            <div class="col-lg-9 col-md-8 col-sm-7 col-xs-12 component-desc">
                                <div class="input-group input350">
                                    <div class="input-group-addon">
                                        <span class="glyphicon glyphicon-file"></span>
                                    </div>
                                    <input class="form-control"
                                           type="number"
                                           value="${qsize}"
                                           name="${qtype}"
                                           id="${qtype}"
                                           min="1"
                                           title="Specify max quality size allowed in MB">
                                    <div class="input-group-addon">
                                        MB
                                    </div>
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
    </div><!-- /tab-pane1 //-->
</%block>
