<%inherit file="../layouts/main.mako"/>
<%!
    import re
    import calendar

    import sickrage
    from sickrage.core.helpers import srdatetime, pretty_filesize, get_size
    from sickrage.core.updaters import tz_updater
    from sickrage.core.media.util import showImage
%>
<%block name="metas">
    <meta data-var="max_download_count" data-content="${max_download_count}">
</%block>
<%block name="content">
    <%namespace file="../includes/quality_defaults.mako" import="renderQualityPill"/>
    <div class="row">
        <div class="col-xs-12 text-center">
            % if sickrage.app.config.home_layout != 'poster':
                <label for="popover" class="badge">${_('Select Columns:')}
                    <button id="popover" type="button" class="form-control form-control-inline input-sm"><b
                            class="caret"></b></button>
                </label>
            % endif

            % if sickrage.app.config.home_layout == 'poster':
                <label for="filterShowName" class="badge">${_('Filter By:')}
                    <input id="filterShowName" class="form-control form-control-inline input-sm" type="search"
                           placeholder="${_('Filter Show Name')}">
                </label>

                <label for="postersort" class="badge">${_('Sort By:')}
                    <select id="postersort" class="form-control form-control-inline input-sm">
                        <option value="name"
                                data-sort="${srWebRoot}/setPosterSortBy/?sort=name" ${('', 'selected')[sickrage.app.config.poster_sortby == 'name']}>
                            ${_('Name')}
                        </option>
                        <option value="date"
                                data-sort="${srWebRoot}/setPosterSortBy/?sort=date" ${('', 'selected')[sickrage.app.config.poster_sortby == 'date']}>
                            ${_('Next Episode')}
                        </option>
                        <option value="network"
                                data-sort="${srWebRoot}/setPosterSortBy/?sort=network" ${('', 'selected')[sickrage.app.config.poster_sortby == 'network']}>
                            ${_('Network')}
                        </option>
                        <option value="progress"
                                data-sort="${srWebRoot}/setPosterSortBy/?sort=progress" ${('', 'selected')[sickrage.app.config.poster_sortby == 'progress']}>
                            ${_('Progress')}
                        </option>
                    </select>
                </label>

                <label for="postersortdirection" class="badge">${_('Sort Order:')}
                    <select id="postersortdirection" class="form-control form-control-inline input-sm">
                        <option value="true"
                                data-sort="${srWebRoot}/setPosterSortDir/?direction=1" ${('', 'selected')[sickrage.app.config.poster_sortdir == 1]}>
                            ${_('Asc')}
                        </option>
                        <option value="false"
                                data-sort="${srWebRoot}/setPosterSortDir/?direction=0" ${('', 'selected')[sickrage.app.config.poster_sortdir == 0]}>
                            ${_('Desc')}
                        </option>
                    </select>
                </label>
            % endif

            <label for="layout" class="badge">${_('Layout:')}
                <select id="layout" name="layout" class="form-control form-control-inline input-sm"
                        onchange="location = this.options[this.selectedIndex].value;">
                    <option value="${srWebRoot}/setHomeLayout/?layout=poster" ${('', 'selected')[sickrage.app.config.home_layout == 'poster']}>
                        ${_('Poster')}
                    </option>
                    <option value="${srWebRoot}/setHomeLayout/?layout=small" ${('', 'selected')[sickrage.app.config.home_layout == 'small']}>
                        ${_('Small Poster')}
                    </option>
                    <option value="${srWebRoot}/setHomeLayout/?layout=banner" ${('', 'selected')[sickrage.app.config.home_layout == 'banner']}>
                        ${_('Banner')}
                    </option>
                    <option value="${srWebRoot}/setHomeLayout/?layout=simple" ${('', 'selected')[sickrage.app.config.home_layout == 'simple']}>
                        ${_('Simple')}
                    </option>
                </select>
            </label>

            % if sickrage.app.config.home_layout == 'poster':
                <label for="posterSizeSlider" class="badge">${_('Poster Size:')}
                    <div style="width: 100px; display: inline-block; margin-left: 7px;" id="posterSizeSlider"></div>
                </label>
            % endif
        </div>
    </div>

    % for curListType, curShowlist in showlists.items():
        % if curListType == "Anime":
            <div class="row">
                <div class="col-lg-10 col-lg-offset-1 col-md-10 col-md-offset-1 col-sm-12 col-xs-12">
                    <div class="h4 well well-sm" style="text-align: center;">${_('Anime List')}</div>
                </div>
            </div>
        % endif
        % if sickrage.app.config.home_layout == 'poster':
            <div id="${('container', 'container-anime')[curListType == 'Anime' and sickrage.app.config.home_layout == 'poster']}"
                 class="show-grid clearfix">
                <div class="posterview">
                    % for curLoadingShow in sickrage.app.show_queue.loadingShowList:
                        % if not curLoadingShow.show:
                            <div class="show-container" data-name="0" data-date="010101" data-network="0"
                                 data-progress="101">
                                <img alt="" title="${curLoadingShow.show_name}" class="show-image"
                                     style="border-bottom: 1px solid #111;" src="${srWebRoot}/images/poster.png"/>
                                <div class="show-details">
                                    <div class="show-add">${_('Loading...')} ${curLoadingShow.show_name}</div>
                                </div>
                            </div>
                        % endif
                    % endfor

                    % for curShow in sorted(curShowlist, lambda x, y: cmp(x.name, y.name)):
                    <%
                        cur_airs_next = ''
                        cur_snatched = 0
                        cur_downloaded = 0
                        cur_total = 0
                        download_stat_tip = ''
                        display_status = curShow.status

                        if display_status:
                            if re.search(r'(?i)(?:new|returning)\s*series', curShow.status):
                                display_status = _('Continuing')
                            elif re.search(r'(?i)(?:nded)', curShow.status):
                                display_status = _('Ended')

                        if curShow.indexerid in show_stat:
                            cur_airs_next = show_stat[curShow.indexerid]['ep_airs_next']

                            cur_snatched = show_stat[curShow.indexerid]['ep_snatched']
                            if not cur_snatched:
                                cur_snatched = 0

                            cur_downloaded = show_stat[curShow.indexerid]['ep_downloaded']
                            if not cur_downloaded:
                                cur_downloaded = 0

                            cur_total = show_stat[curShow.indexerid]['ep_total']
                            if not cur_total:
                                cur_total = 0

                        if cur_total != 0:
                            download_stat = str(cur_downloaded)
                            download_stat_tip = _("Downloaded: ") + str(cur_downloaded)
                            if cur_snatched > 0:
                                download_stat = download_stat
                                download_stat_tip = download_stat_tip + "&#013;" + _("Snatched: ") + str(cur_snatched)

                            download_stat = download_stat + " / " + str(cur_total)
                            download_stat_tip = download_stat_tip + "&#013;" + _("Total: ") + str(cur_total)
                        else:
                            download_stat = '?'
                            download_stat_tip = _("no data")

                        nom = cur_downloaded
                        den = cur_total
                        if den == 0:
                            den = 1

                        progressbar_percent = nom * 100 / den

                        data_date = '6000000000.0'
                        if cur_airs_next:
                            data_date = calendar.timegm(srdatetime.srDateTime(tz_updater.parse_date_time(cur_airs_next, curShow.airs, curShow.network), convert=True).dt.timetuple())
                        elif display_status:
                            if 'nded' not in display_status and 1 == int(curShow.paused):
                                data_date = '5000000500.0'
                            elif 'ontinu' in display_status:
                                data_date = '5000000000.0'
                            elif 'nded' in display_status:
                                data_date = '5000000100.0'
                    %>
                        <div class="show-container" id="show${curShow.indexerid}" data-name="${curShow.name}"
                             data-date="${data_date}" data-network="${curShow.network}"
                             data-progress="${progressbar_percent}">
                            <div class="show-image">
                                <a href="${srWebRoot}/home/displayShow?show=${curShow.indexerid}">
                                    <img alt="" class="show-image"
                                         src="${srWebRoot}${showImage(curShow.indexerid, 'poster_thumb').url}"/>
                                </a>
                            </div>

                            <div class="progressbar hidden-print" style="position:relative;"
                                 data-show-id="${curShow.indexerid}"
                                 data-progress-percentage="${progressbar_percent}"></div>

                            <div class="show-title">
                                ${curShow.name}
                            </div>

                            <div class="show-date">
                                % if cur_airs_next:
                                    <% ldatetime = srdatetime.srDateTime(tz_updater.parse_date_time(cur_airs_next, curShow.airs, curShow.network), convert=True).dt %>
                                    <%
                                        try:
                                            out = srdatetime.srDateTime(ldatetime).srfdate()
                                        except ValueError:
                                            out = _('Invalid date')
                                    %>
                                % else:
                                    <% display_status = curShow.status %>
                                    <%
                                        out = ''
                                        if display_status:
                                            out = display_status
                                            if 'nded' not in display_status and 1 == int(curShow.paused):
                                                out = _('Paused')
                                    %>
                                % endif
                                ${out}
                            </div>

                            <div class="show-details">
                                <table class="show-details" width="100%" cellspacing="1" border="0" cellpadding="0">
                                    <tr>
                                        <td class="show-table">
                                            <span class="show-dlstats"
                                                  title="${download_stat_tip}">${download_stat}</span>
                                        </td>

                                        <td class="show-table">
                                            % if sickrage.app.config.home_layout != 'simple':
                                                % if curShow.network:
                                                    <span>
                                                        <img class="show-network-image"
                                                             src="${srWebRoot}${showImage(curShow.indexerid, 'network').url}"
                                                             alt="${curShow.network}"
                                                             title="${curShow.network}"/>
                                                    </span>
                                                % else:
                                                    <span>
                                                        <img class="show-network-image"
                                                             src="${srWebRoot}/images/network/nonetwork.png"
                                                             alt="${_('No Network')}"
                                                             title="${_('No Network')}"/>
                                                    </span>
                                                % endif
                                            % else:
                                                <span title="${curShow.network}">${curShow.network}</span>
                                            % endif
                                        </td>

                                        <td class="show-table">
                                            ${renderQualityPill(curShow.quality, showTitle=True, overrideClass="show-quality")}
                                        </td>
                                    </tr>
                                </table>
                            </div>
                        </div>
                    % endfor
                </div>
            </div>
        % else:
            <div class="horizontal-scroll">
                <table id="showListTable${curListType}" class="sickrageTable tablesorter" cellspacing="1" border="0"
                       cellpadding="0">
                    <thead>
                    <tr>
                        <th class="nowrap">${_('Next Ep')}</th>
                        <th class="nowrap">${_('Prev Ep')}</th>
                        <th>${_('Show')}</th>
                        <th>${_('Network')}</th>
                        <th>${_('Quality')}</th>
                        <th>${_('Downloads')}</th>
                        <th>${_('Size')}</th>
                        <th>${_('Active')}</th>
                        <th>${_('Status')}</th>
                    </tr>
                    </thead>

                    <tfoot>
                    <tr>
                        <th rowspan="1" colspan="1" align="center"><a
                                href="${srWebRoot}/home/addShows/">${_('Add')} ${(_('Show'), _('Anime'))[curListType == 'Anime']}</a>
                        </th>
                        <th>&nbsp;</th>
                        <th>&nbsp;</th>
                        <th>&nbsp;</th>
                        <th>&nbsp;</th>
                        <th>&nbsp;</th>
                        <th>&nbsp;</th>
                        <th>&nbsp;</th>
                        <th>&nbsp;</th>
                    </tr>
                    </tfoot>

                    % if sickrage.app.show_queue.loadingShowList:
                        <tbody class="tablesorter-infoOnly">
                            % for curLoadingShow in sickrage.app.show_queue.loadingShowList:
                                % if not curLoadingShow.show or curLoadingShow.show not in sickrage.app.showlist:
                                    <tr>
                                        <td align="center">(${_('loading')})</td>
                                        <td></td>
                                        <td>
                                            % if curLoadingShow.show is None:
                                                <span title="">${_('Loading...')} ${curLoadingShow.show_name}</span>
                                            % else:
                                                <a data-fancybox
                                                   href="displayShow?show=${curLoadingShow.show.indexerid}">${curLoadingShow.show.name}</a>
                                            % endif
                                        </td>
                                        <td></td>
                                        <td></td>
                                        <td></td>
                                        <td></td>
                                        <td></td>
                                    </tr>
                                % endif
                            % endfor
                        </tbody>
                    % endif

                    <tbody>
                        % for curShow in sorted(curShowlist, lambda x, y: cmp(x.name, y.name)):
                            <%
                                cur_airs_next = ''
                                cur_airs_prev = ''
                                cur_snatched = 0
                                cur_downloaded = 0
                                cur_total = 0
                                show_size = 0
                                download_stat_tip = ''

                                if curShow.indexerid in show_stat:
                                    cur_airs_next = show_stat[curShow.indexerid]['ep_airs_next']
                                    cur_airs_prev = show_stat[curShow.indexerid]['ep_airs_prev']

                                    cur_snatched = show_stat[curShow.indexerid]['ep_snatched']
                                    if not cur_snatched:
                                        cur_snatched = 0

                                    cur_downloaded = show_stat[curShow.indexerid]['ep_downloaded']
                                    if not cur_downloaded:
                                        cur_downloaded = 0

                                    cur_total = show_stat[curShow.indexerid]['ep_total']
                                    if not cur_total:
                                        cur_total = 0

                                    show_size = get_size(curShow.location.encode('utf-8'))

                                if cur_total != 0:
                                    download_stat = str(cur_downloaded)
                                    download_stat_tip = _("Downloaded: ") + str(cur_downloaded)
                                    if cur_snatched > 0:
                                        download_stat = download_stat + "+" + str(cur_snatched)
                                        download_stat_tip = download_stat_tip + "&#013;" + _("Snatched: ") + str(cur_snatched)

                                    download_stat = download_stat + " / " + str(cur_total)
                                    download_stat_tip = download_stat_tip + "&#013;" + _("Total: ") + str(cur_total)
                                else:
                                    download_stat = '?'
                                    download_stat_tip = _("no data")

                                nom = cur_downloaded
                                den = cur_total
                                if den == 0:
                                    den = 1

                                progressbar_percent = nom * 100 / den
                            %>
                            <tr>
                                % if cur_airs_next:
                                <% airDate = srdatetime.srDateTime(tz_updater.parse_date_time(cur_airs_next, curShow.airs, curShow.network), convert=True).dt %>
                                % try:
                                    <td align="center" class="nowrap">
                                        <time datetime="${airDate.isoformat()}"
                                              class="date">${srdatetime.srDateTime(airDate).srfdate()}</time>
                                    </td>
                                % except ValueError:
                                    <td align="center" class="nowrap"></td>
                                % endtry
                                % else:
                                    <td align="center" class="nowrap"></td>
                                % endif

                                % if cur_airs_prev:
                                <% airDate = srdatetime.srDateTime(tz_updater.parse_date_time(cur_airs_prev, curShow.airs, curShow.network), convert=True).dt %>
                                % try:
                                    <td align="center" class="nowrap">
                                        <time datetime="${airDate.isoformat()}" class="date">
                                            ${srdatetime.srDateTime(airDate).srfdate()}
                                        </time>
                                    </td>
                                % except ValueError:
                                    <td align="center" class="nowrap"></td>
                                % endtry
                                % else:
                                    <td align="center" class="nowrap"></td>
                                % endif

                                % if sickrage.app.config.home_layout == 'small':
                                    <td class="tvShow" align="left">
                                        <div class="imgsmallposter ${sickrage.app.config.home_layout}">
                                            <a href="${srWebRoot}/home/displayShow?show=${curShow.indexerid}"
                                               title="${curShow.name}">
                                                <img src="${srWebRoot}${showImage(curShow.indexerid, 'poster_thumb').url}"
                                                     class="${sickrage.app.config.home_layout}"
                                                     alt="${curShow.indexerid}"/>
                                            </a>
                                            <a href="${srWebRoot}/home/displayShow?show=${curShow.indexerid}"
                                               style="vertical-align: middle;">${curShow.name}</a>
                                        </div>
                                    </td>
                                % elif sickrage.app.config.home_layout == 'banner':
                                    <td>
                                        <span style="display: none;">${curShow.name}</span>
                                        <div class="imgbanner ${sickrage.app.config.home_layout}">
                                            <a href="${srWebRoot}/home/displayShow?show=${curShow.indexerid}">
                                                <img src="${srWebRoot}${showImage(curShow.indexerid, 'banner').url}"
                                                     class="${sickrage.app.config.home_layout}"
                                                     alt="${curShow.indexerid}" title="${curShow.name}"/>
                                            </a>
                                        </div>
                                    </td>
                                % elif sickrage.app.config.home_layout == 'simple':
                                    <td class="tvShow"><a
                                            href="${srWebRoot}/home/displayShow?show=${curShow.indexerid}">${curShow.name}</a>
                                    </td>
                                % endif

                                % if sickrage.app.config.home_layout != 'simple':
                                    <td align="center">
                                        % if curShow.network:
                                            <span>
                                                <img id="network" width="54" height="27"
                                                     src="${srWebRoot}${showImage(curShow.indexerid, 'network').url}"
                                                     alt="${curShow.network}"
                                                     title="${curShow.network}"/>
                                            </span>
                                            <span class="visible-print-inline">${curShow.network}</span>
                                        % else:
                                            <span>
                                                <img id="network" width="54" height="27"
                                                     src="${srWebRoot}/images/network/nonetwork.png"
                                                     alt="${_('No Network')}"
                                                     title="${_('No Network')}"/>
                                            </span>
                                            <span class="visible-print-inline">No Network</span>
                                        % endif
                                    </td>
                                % else:
                                    <td>
                                        <span title="${curShow.network}">${curShow.network}</span>
                                    </td>
                                % endif

                                <td align="center">${renderQualityPill(curShow.quality, showTitle=True)}</td>

                                <td align="center">
                                    <span style="display: none;">${download_stat}</span>
                                    <div class="progressbar" style="position:relative"
                                         data-show-id="${curShow.indexerid}"
                                         data-progress-percentage="${progressbar_percent}"
                                         data-progress-text="${download_stat}"
                                         data-progress-tip="${download_stat_tip}"></div>
                                </td>

                                <td align="center" data-show-size="${show_size}">${pretty_filesize(show_size)}</td>

                                <td align="center">
                                    <% paused = int(curShow.paused) == 0 and curShow.status == 'Continuing' %>
                                    <i class="fa ${("fa-times red-text", "fa-check green-text")[bool(paused)]}"></i>
                                </td>

                                <td align="center">
                                    % if curShow.status and re.search(r'(?i)(?:new|returning)\s*series', curShow.status):
                                        ${_('Continuing')}
                                    % elif curShow.status and re.search('(?i)(?:nded)', curShow.status):
                                        ${_('Ended')}
                                    % else:
                                        ${curShow.status}
                                    % endif
                                </td>
                            </tr>
                        % endfor
                    </tbody>
                </table>
            </div>
        % endif
    % endfor
</%block>
