var widget_sort={};

var pmDashboard = {
    pageSize:20,
    model:{
        name:"module"
    }
}

pmDashboard.model.className = "pmDashboard"

pmDashboard.model.count = {
    projects:'-',
    inventories:'-',
    hosts:'-',
    groups:'-',
    users:'-',
    history:'-',
}

pmDashboard.statsData={
    projects:'-',
    inventories:'-',
    hosts:'-',
    groups:'-',
    users:'-',
    templates:'-'
}

pmDashboard.statsDataLast=14;
pmDashboard.statsDataLastQuery=14;
pmDashboard.statsDataMomentType='day';


/**
 * Двумерный массив с описанием списка отображаемых виджетов в каждой строке
 *
 * @example
 * [
 *  [{
        name:'pmwTemplatesCounter',  // Имя класса виджета
        opt:{},                      // Опции для виджета
    }]
 ]
 *
 * @type Array
 */
pmDashboard.model.widgets = [
    [

    ],
]

/*
*Двумерный массив, хранящий в себе настройки виджетов по умолчанию.
 */
pmDashboard.model.defaultWidgets = [
    [
        {
            name:'pmwTemplatesCounter',
            title:'Templates Counter',
            sortNum:0,
            active:true,
            opt:{},
            type:1,
            collapse:false,
        },
        {
            name:'pmwProjectsCounter',
            title:'Projects Counter',
            sortNum:1,
            active:true,
            opt:{},
            type:1,
            collapse:false,
        },
        {
            name:'pmwInventoriesCounter',
            title:'Inventories Counter',
            sortNum:2,
            active:true,
            opt:{},
            type:1,
            collapse:false,
        },
        {
            name:'pmwHostsCounter',
            title:'Hosts Counter',
            sortNum:3,
            active:true,
            opt:{},
            type:1,
            collapse:false,
        },
        {
            name:'pmwGroupsCounter',
            title:'Groups Counter',
            sortNum:4,
            active:true,
            opt:{},
            type:1,
            collapse:false,
        },
        {
            name:'pmwUsersCounter',
            title:'Users Counter',
            sortNum:5,
            active:true,
            opt:{},
            type:1,
            collapse:false,
        },
        {
            name:'pmwAnsibleModuleWidget',
            title:'Run shell command',
            sortNum:6,
            active:true,
            opt:{},
            type:0,
            collapse:false,
        },
        {
            name:'pmwChartWidget',
            title:'Tasks history',
            sortNum:7,
            active:true,
            opt:{},
            type:0,
            collapse:false,
        },
        {
            name:'pmwTasksTemplatesWidget',
            title:'Templates Task',
            sortNum:8,
            active:true,
            opt:{},
            type:0,
            collapse:false,
        },
        {
            name:'pmwModulesTemplatesWidget',
            title:'Templates Module',
            sortNum:9,
            active:true,
            opt:{},
            type:0,
            collapse:false,
        },/**/
    ],
]

/*
 * Массив, хранящий в себе настройки линий графика на странице Dashboard'а.
 */
pmDashboard.model.ChartLineSettings = [

]

/*
 * Массив, хранящий в себе настройки по умолчанию линий графика на странице Dashboard'а.
 */
pmDashboard.model.defaultChartLineSettings = [
    {
        name: "all_tasks",
        title: "All tasks",
        color: "#1f77b4",
        active: true
    },
    {
        name: "ok",
        title: "OK",
        color: "#276900",
        active: true
    },
    {
        name: "error",
        title: "ERROR",
        color: "#333333",
        active: true
    },
    {
        name: "interrupted",
        title: "INTERRUPTED",
        color: "#9b97e4",
        active: true
    },
    {
        name: "delay",
        title: "DELAY",
        color: "#808419",
        active: true
    },
    {
        name: "offline",
        title: "OFFLINE",
        color: "#9e9e9e",
        active: true
    }
]

/**
 * Функция полностью копирует настройки для линий графика.
 * Подразумевается, что данная функция вызывается, когда пришел из API пустой JSON.
 */
pmDashboard.cloneChartLineSettingsTotally = function(){
    pmDashboard.model.ChartLineSettings = JSON.parse(JSON.stringify(pmDashboard.model.defaultChartLineSettings));
    return pmDashboard.model.ChartLineSettings;
}

/**
 * Функция обновляет часть настроек линий графика, данные по которым пришли из API.
 * Подразумевается, что данная функция вызывается, когда пришел из API непустой JSON.
 */
pmDashboard.cloneChartLineSettingsFromApi = function(data){
    pmDashboard.model.ChartLineSettings = JSON.parse(JSON.stringify(pmDashboard.model.defaultChartLineSettings));
    for(var i in pmDashboard.model.ChartLineSettings)
    {
        for(var j in data)
        {
            if(pmDashboard.model.ChartLineSettings[i].name == j)
            {
                for(var k in data[j])
                {
                    if(pmDashboard.model.ChartLineSettings[i].hasOwnProperty(k))
                    {
                        pmDashboard.model.ChartLineSettings[i][k] = data[j][k];
                    }
                }
            }
        }
    }
    return pmDashboard.model.ChartLineSettings;
}

/**
 * Функция полностью копирует настройки по умолчанию для виджетов.
 * Подразумевается, что данная функция вызывается, когда пришел из API пустой JSON.
 */
pmDashboard.cloneDefaultWidgetsTotally = function(){
    for(var i in pmDashboard.model.defaultWidgets[0])
    {
        pmDashboard.model.widgets[0][i]={};
        for (var j in pmDashboard.model.defaultWidgets[0][i])
        {
            pmDashboard.model.widgets[0][i][j]=pmDashboard.model.defaultWidgets[0][i][j];
        }
    }
    console.log(pmDashboard.model.widgets[0]);
    return pmDashboard.model.widgets[0];
}

/**
 * Функция копирует "статичные" настройки по умолчанию для виджетов.
 * Под "статичными" понимается name, title, opt, type.
 * Данные настройки не меняются в ходе работы пользователя с интерфейсом.
 * Подразумевается, что данная функция вызывается, когда пришел из API непустой JSON.
 */
pmDashboard.cloneDefaultWidgetsStaticSettingsOnly = function(){
    for(var i in pmDashboard.model.defaultWidgets[0])
    {
        pmDashboard.model.widgets[0][i]={};
        pmDashboard.model.widgets[0][i].name=pmDashboard.model.defaultWidgets[0][i].name;
        pmDashboard.model.widgets[0][i].title=pmDashboard.model.defaultWidgets[0][i].title;
        pmDashboard.model.widgets[0][i].opt=pmDashboard.model.defaultWidgets[0][i].opt;
        pmDashboard.model.widgets[0][i].type=pmDashboard.model.defaultWidgets[0][i].type;
    }
    return pmDashboard.model.widgets[0];
}

/**
 * Функция добавляет виджету оставшиеся(не "статичные") настройки.
 * Функция проверяет есть ли соответсвуют ли пришедшие настройки для виджетов из API тем,
 * что хранятся в массиве с настройками по умолчанию.
 * Если данное свойство соответсвует, то его значение присваивается настройкам виджета.
 * В противном случае ему присваивается настройка по умолчанию.
 */
pmDashboard.clonetWidgetsSettingsFromApiAndVerify = function(data){
    pmDashboard.cloneDefaultWidgetsStaticSettingsOnly();
    for(var i in pmDashboard.model.defaultWidgets[0])
    {
        for(var j in data)
        {
            if(pmDashboard.model.defaultWidgets[0][i].name==j)
            {
                for (var k in pmDashboard.model.defaultWidgets[0][i])
                {
                    if(k in data[j]){
                        pmDashboard.model.widgets[0][i][k]=data[j][k];
                    }
                    else
                    {
                        pmDashboard.model.widgets[0][i][k]=pmDashboard.model.defaultWidgets[0][i][k];
                    }
                }
            }
        }
    }
    return pmDashboard.model.widgets[0];
}

/**
 * Функция проверяет необходимо ли посылать запрос к API для загрузки
 * пользовательских настроек Dashboard'a (настройки виджетов, настройки линий графика).
 * Например, если в модели отсутствует какой-либо виджет,
 * либо у виджета отсутсвует какое-нибудь свойство,
 * то запрос к API будет отправлен.
 * @param {Object} defaultObj - объект с настройками по умолчанию
 * @param {Object} currentObj - объект с текущими настройками
 *
 */
pmDashboard.checkNecessityToLoadDashboardSettingsFromApi = function(defaultObj, currentObj)
{
    var bool1 = false, bool2 = false;
    for (var i in defaultObj){
        for (var j in currentObj)
        {
            if(defaultObj[i].name == currentObj[j].name)
            {
                for(var k in defaultObj[i])
                {
                    if(!(k in currentObj[j])){
                        bool1 = true;
                    }

                }
            }
        }
    }

    if(defaultObj.length != currentObj.length)
    {
        bool2 = true;
    }

    if(bool1 || bool2)
    {
        //нужно послать запрос к api
        return true;
    }
    else
    {
        //не нужно посылать запрос к api
        return false;
    }
}

/**
 *Функция создает объект, в который вносит актуальные настройки виджета,
 *на основе изменений, внесенных в pmDashboard.model.widgets[0][i].
 *localObj- pmDashboard.model.widgets[0][i]
 * @type Object
 */
pmDashboard.getNewWidgetSettings = function(localObj)
{
    var obj={};
    obj.sortNum=localObj.sortNum;
    obj.active=localObj.active;
    obj.collapse=localObj.collapse;
    return obj;
}

/**
 *Функция заправшивает у API пользовательские настройки Dashboard'a
 *(настройки виджетов, настройки линий графика).
 *Если они есть(пришел не пустой объект), то данные настройки добавляются в pmDashboard.model.
 */
pmDashboard.getUserDashboardSettingsFromAPI = function()
{
    var userId=window.my_user_id;
    if(pmDashboard.checkNecessityToLoadDashboardSettingsFromApi(pmDashboard.model.defaultWidgets[0], pmDashboard.model.widgets[0]) ||
        pmDashboard.checkNecessityToLoadDashboardSettingsFromApi(pmDashboard.model.defaultChartLineSettings, pmDashboard.model.ChartLineSettings))
    {
        return spajs.ajax.Call({
            url: hostname + "/api/v1/users/" + userId + "/settings/",
            type: "GET",
            contentType: 'application/json',
            success: function (data)
            {
                if ($.isEmptyObject(data.widgetSettings))
                {
                    pmDashboard.cloneDefaultWidgetsTotally();
                }
                else
                {
                    pmDashboard.clonetWidgetsSettingsFromApiAndVerify(data.widgetSettings);
                    pmDashboard.model.widgets[0].sort(pmDashboard.sortCountWidget);
                }

                if ($.isEmptyObject(data.chartLineSettings))
                {
                    pmDashboard.cloneChartLineSettingsTotally();
                }
                else
                {
                    pmDashboard.cloneChartLineSettingsFromApi(data.chartLineSettings);
                }
            },
            error: function (e)
            {
                console.warn(e)
                polemarch.showErrors(e)
            }
        });
    }
    else
    {
        return false;
    }
}

/**
 *Функция сохраняет в API пользовательские настройки Dashboard'a
 *(настройки виджетов, настройки линий графика).
 */
pmDashboard.putUserDashboardSettingsToAPI = function()
{
    var userId=window.my_user_id;
    var widgetSettings= {};
    for(var i in  pmDashboard.model.widgets[0]){
        var objName=pmDashboard.model.widgets[0][i].name;
        widgetSettings[objName]=pmDashboard.getNewWidgetSettings(pmDashboard.model.widgets[0][i]);
    }
    var chartLineSettings = {};
    for(var i in pmDashboard.model.ChartLineSettings){
        var objName=pmDashboard.model.ChartLineSettings[i].name;
        chartLineSettings[objName]={active: pmDashboard.model.ChartLineSettings[i].active};
    }
    return spajs.ajax.Call({
        url: hostname + "/api/v1/users/" + userId + "/settings/",
        type: "POST",
        contentType: 'application/json',
        data: JSON.stringify({widgetSettings:widgetSettings, chartLineSettings:chartLineSettings}),
        success: function (data)
        {
            //console.log("Data was posted");

        },
        error: function (e)
        {
            console.warn(e)
            polemarch.showErrors(e)
        }
    });

}

/**
 *Функция, сортирующая массив объектов.
 */
pmDashboard.sortCountWidget=function(Obj1, Obj2)
{
    return Obj1.sortNum-Obj2.sortNum;
}

/**
 *Функция, меняющая свойство виджета active на false.
 */
pmDashboard.setNewWidgetActiveValue = function(thisButton)
{
    var widgetName=thisButton.parentElement.parentElement.parentElement.parentElement.parentElement.getAttribute("id");
    for(var i in pmDashboard.model.widgets[0])
    {
        if(pmDashboard.model.widgets[0][i].name==widgetName)
        {
            pmDashboard.model.widgets[0][i].active=false;
        }
    }
    pmDashboard.putUserDashboardSettingsToAPI();
}

/**
 *Функция, меняющая свойство виджета collapse на противоположное (true-false).
 */
pmDashboard.setNewWidgetCollapseValue = function(thisButton)
{
    var widgetName=thisButton.parentElement.parentElement.parentElement.parentElement.parentElement.getAttribute("id");
    for(var i in pmDashboard.model.widgets[0])
    {
        if(pmDashboard.model.widgets[0][i].name==widgetName)
        {
            pmDashboard.model.widgets[0][i].collapse=!pmDashboard.model.widgets[0][i].collapse;

            //скрываем селект с выбором периода на виджете-графике при его сворачивании
            if(widgetName=="pmwChartWidget")
            {
                if(pmDashboard.model.widgets[0][i].collapse==false)
                {
                    $("#period-list").slideDown(400);
                }
                else
                {
                    $("#period-list").slideUp(400);
                }
            }
        }
    }
    pmDashboard.putUserDashboardSettingsToAPI();
}

/**
 *Функция, сохраняющая настройки виджетов/линий графика,
 *внесенные в таблицу редактирования настроек Dashboard'a.
 */
pmDashboard.getOptionsFromTable = function(table_id, pmDashboard_obj)
{
    var modalTable=document.getElementById(table_id);
    var modalTableTr=modalTable.getElementsByTagName("tr");
    for(var i=1; i<modalTableTr.length; i++)
    {
        var pmDashboard_obj_name=modalTableTr[i].getAttribute("rowname");
        var modalTableTrTds=modalTableTr[i].children;
        for(var j=0; j<modalTableTrTds.length; j++)
        {
            var valueName=modalTableTrTds[j].getAttribute("valuename");

            if(valueName)
            {
                var classList1=modalTableTrTds[j].children[0].classList;
                var selected=false;
                for(var k in classList1)
                {
                    if(classList1[k]=="selected")
                    {
                        selected=true;
                    }
                }
                for(var z in  pmDashboard_obj)
                {
                    if(pmDashboard_obj[z].name==pmDashboard_obj_name)
                    {
                        pmDashboard_obj[z][valueName]=selected;
                    }
                }
            }
        }
    }
}

/**
 *Функция, сохраняющая настройки виджетов, внесенные в форму настроек виджетов Dashboard'a.
 */
pmDashboard.saveWigdetsOptions = function()
{
    pmDashboard.getOptionsFromTable("modal-table",pmDashboard.model.widgets[0]);
    pmDashboard.putUserDashboardSettingsToAPI();
}

/**
 *Функция, сохраняющая настройки виджетов, внесенные в форму настроек виджетов Dashboard'a,
 *из модального окна на странице Dashboard'a.
 */
pmDashboard.saveWigdetsOptionsFromModal = function()
{
    return $.when(pmDashboard.saveWigdetsOptions()).done(function(){
        return $.when(hidemodal(), pmDashboard.HideAfterSaveModalWindow()).done(function(){
            return spajs.openURL("/");
        }).promise();
    }).promise();

}

/**
 *Функция, сохраняющая настройки виджетов, внесенные в форму настроек виджетов Dashboard'a,
 *из секции на странице профиля пользователя.
 */
pmDashboard.saveWigdetsOptionsFromProfile = function()
{
    return $.when(pmDashboard.saveWigdetsOptions()).done(function(){
        return $.notify("Dashboard widget options were successfully saved", "success");
    }).fail(function(){
        return $.notify("Dashboard widget options were not saved", "error");
    }).promise();
}

/**
 *Функция, сохраняющая настройки линий графика Dashboard'a.
 */
pmDashboard.saveChartLineSettings = function()
{
    pmDashboard.getOptionsFromTable("chart_line_settings_table", pmDashboard.model.ChartLineSettings);
    pmDashboard.putUserDashboardSettingsToAPI();
}

/**
 *Функция, сохраняющая настройки линий графика, внесенных в форму настроек виджетов Dashboard'a,
 *из секции на странице профиля пользователя.
 */
pmDashboard.saveChartLineSettingsFromProfile = function()
{
    return $.when(pmDashboard.saveChartLineSettings()).done(function(){
        return $.notify("Dashboard chart lines settings were successfully saved", "success");
    }).fail(function(){
        return $.notify("Dashboard chart lines settings were not saved", "error");
    }).promise();
}

/**
 *Функция, сохраняющая все настройки, касающиеся Dashboard'a, со страницы профиля пользователя.
 */
pmDashboard.saveAllDashboardSettingsFromProfile = function(){
    pmDashboard.getOptionsFromTable("modal-table",pmDashboard.model.widgets[0]);
    pmDashboard.getOptionsFromTable("chart_line_settings_table", pmDashboard.model.ChartLineSettings);
    return $.when(pmDashboard.putUserDashboardSettingsToAPI()).done(function(){
        return $.notify("Dashboard settings were successfully saved", "success");
    }).fail(function(){
        return $.notify("Dashboard settings were not saved", "error");
    }).promise();
}

/**
 * Функция, которая формирует массив данных для кривых графика по отдельному статусу
 */
pmDashboard.getDataForStatusChart = function(tasks_data, tasks_data_t, status)
{
    for(var i in tasks_data) {
        tasks_data[i]=0;
    }

    for(var i in pmDashboard.statsData.jobs[pmDashboard.statsDataMomentType])
    {
        var val = pmDashboard.statsData.jobs[pmDashboard.statsDataMomentType][i];
        var time =+ moment(val[pmDashboard.statsDataMomentType]).tz(window.timeZone).format("x");

        if(val.status==status){
            tasks_data[time] = val.sum;
            tasks_data_t.push(time)
        }
    }

    var chart_tasks_data1 = [status];

    for(var j in tasks_data_t)
    {
        var time = tasks_data_t[j]
        chart_tasks_data1.push(tasks_data[time]/1);
    }
    return chart_tasks_data1;

}

/**
 * Функция, отправляющая запрос /api/v1/stats/,
 * который дает нам информацию для виджетов класса pmwItemsCounter,
 * а также для графика на странице Dashboard.
 */
pmDashboard.loadStats=function()
{
    var limit=1;
    var thisObj = this;
    return spajs.ajax.Call({
        url: hostname + "/api/v1/stats/?last="+pmDashboard.statsDataLastQuery,
        type: "GET",
        contentType: 'application/json',
        data: "limit=" + encodeURIComponent(limit)+"&rand="+Math.random(),
        success: function (data)
        {
            pmDashboard.statsData=data;
        },
        error: function (e)
        {
            console.warn(e)
            polemarch.showErrors(e)
        }
    });
}

/**
 *Функция вызывается, когда происходит изменение периода на графике(пользователь выбрал другой option в select).
 *Функция обновляет значения переменных, которые в дальнейшем используются для запроса к api/v1/stats и отрисовки графика.
 */
pmDashboard.updateStatsDataLast=function(thisEl)
{
    var newLast=thisEl.value;
    switch(newLast) {
        case '1095':
            pmDashboard.statsDataLast=3;
            pmDashboard.statsDataMomentType="year";
            break;
        case '365':
            pmDashboard.statsDataLast=13;
            pmDashboard.statsDataMomentType="month";
            break;
        case '90':
            pmDashboard.statsDataLast=3;
            pmDashboard.statsDataMomentType="month";
            break;
        default:
            pmDashboard.statsDataLast=+newLast;
            pmDashboard.statsDataMomentType="day";
            break;
    }
    pmDashboard.statsDataLastQuery=+newLast;
    pmDashboard.updateData();
}

/**
 * Ниже представлены 3 функции для работы с модальным окном - Set widget options
 * pmDashboard.showModalWindow - открывает модальное окно, предварительно обновляя данные
 * pmDashboard.HideAfterSaveModalWindow - скрывает модальное окно
 * pmDashboard.renderModalWindow - отрисовывает модальное окно
 */
pmDashboard.showModalWindow = function()
{
    if($('div').is('#modal-widgets-settings'))
    {
        pmDashboard.model.widgets[0].sort(pmDashboard.sortCountWidget);
        $('#modal-widgets-settings').empty();
        $('#modal-widgets-settings').html(pmDashboard.renderModalWindow());
        $("#modal-widgets-settings").modal('show');
    }
}

pmDashboard.HideAfterSaveModalWindow = function()
{
    if($('div').is('#modal-widgets-settings'))
    {
        return $("#modal-widgets-settings").modal('hide');
    }

}

pmDashboard.renderModalWindow = function()
{
    var html=spajs.just.render('modalWidgetsSettings');
    return html;
}



pmDashboard.stopUpdates = function()
{
    clearTimeout(this.model.updateTimeoutId)
    this.model.updateTimeoutId = undefined;
}

pmDashboard.toggleSortable = function(thisButton)
{
    var state = widget_sort.option("disabled");
    widget_sort.option("disabled", !state);
    if(thisButton.children[0].getAttribute("class")=="fa fa-lock")
    {
        thisButton.children[0].setAttribute("class", "fa fa-unlock");
        var sortableArr=$('.cursor-move1');
        for (var i=0; i<sortableArr.length; i++)
        {
            $(sortableArr[i]).addClass('cursor-move');
            $(sortableArr[i]).removeClass('cursor-move1');
        }
    }
    else
    {
        thisButton.children[0].setAttribute("class", "fa fa-lock");
        var sortableArr=$('.cursor-move');
        for (var i=0; i<sortableArr.length; i++)
        {
            $(sortableArr[i]).addClass('cursor-move1');
            $(sortableArr[i]).removeClass('cursor-move');
        }
    }
}

/**
 * Функция подгружает данные необходимые для отрисовки страницы Dashboard'a
 * одним bulk запросом.
 */
pmDashboard.getDataForDashboardFromBulk = function ()
{
    var def = new $.Deferred();
    var bulkArr = [
        {
            type:"get",
            item: "projects",
            filters: "limit=1"
        },
        {
            type:"get",
            item: "inventories",
            filters: "limit=1"
        },
        {
            type:"get",
            item: "templates",
            filters: "limit=1"
        },
    ];

    spajs.ajax.Call({
        url: hostname + "/api/v1/_bulk/",
        type: "POST",
        contentType: 'application/json',
        data: JSON.stringify(bulkArr),
        success: function (data)
        {
            for(var i in data)
            {
                var pmObj = pmItems.definePmObject(bulkArr[i].item);
                pmObj.model.itemslist = data[i].data;
                for(var j in data[i].data.results)
                {
                    var val = pmObj.afterItemLoad(data[i].data.results[j])
                    pmObj.model.items.justWatch(val.id);
                    pmObj.model.items[val.id] = mergeDeep(pmObj.model.items[val.id], val)
                }
            }
            def.resolve();
        },
        error: function (e) {
            $.notify("Error " + e, "error");
            def.reject();
        }
    })

    return def.promise();
}



tabSignal.connect('guiLocalSettings.hideMenu', function(){

    setTimeout(function(){

        if(spajs.currentOpenMenu && spajs.currentOpenMenu.id == 'home')
        {
            pmDashboard.updateData()
        }
    }, 200)
})

tabSignal.connect('hideLoadingProgress', function(){ 
    if(spajs.currentOpenMenu && spajs.currentOpenMenu.id == 'home')
    {
        pmDashboard.updateData()
    } 
})

pmDashboard.updateData = function()
{
    var thisObj = this
    if(this.model.updateTimeoutId)
    {
        clearTimeout(this.model.updateTimeoutId)
        this.model.updateTimeoutId = undefined
    }

    $.when(pmDashboard.loadStats()).done(function()
    {
        //обновляем счетчики для виджетов
        pmwHostsCounter.updateCount();
        pmwTemplatesCounter.updateCount();
        pmwGroupsCounter.updateCount();
        pmwProjectsCounter.updateCount();
        pmwInventoriesCounter.updateCount();
        pmwUsersCounter.updateCount();

        //строим график
        //определяем текущий месяц и год
        var monthNum=moment().format("MM");
        var yearNum=moment().format("YYYY");
        var dayNum=moment().format("DD");
        var hourNum=",T00:00:00";
        var startTimeOrg="";

        switch (pmDashboard.statsDataMomentType) {
            case "year":
                startTimeOrg=yearNum+"-01-01"+hourNum;
                break;
            case "month":
                startTimeOrg=yearNum+"-"+monthNum+"-01"+hourNum;
                break;
            case "day":
                startTimeOrg=yearNum+"-"+monthNum+"-"+dayNum+hourNum;
                break;
        }

        //задаем стартовую дату для графика.
        //pmDashboard.statsDataLast - количество периодов назад
        //pmDashboard.statsDataMomentType - тип периода - месяц/год
        var startTime =+ moment(startTimeOrg).subtract(pmDashboard.statsDataLast-1, pmDashboard.statsDataMomentType).tz(window.timeZone).format("x");

        tasks_data = {};
        tasks_data_t = [];

        //формируем в цикле временные отрезки для графика относительно стартовой даты
        for(var i = 0; i< pmDashboard.statsDataLast; i++)
        {
            //идем на период вперед
            var time=+moment(startTime).add(i, pmDashboard.statsDataMomentType).tz(window.timeZone).format("x");
            tasks_data[time] = 0;
            tasks_data_t.push(time);
        }

        //массив для линий графика, которые необходимо отобразить на странице
        var linesForChartArr = [];
        //объект, хранящий в себе цвета этих линий
        var colorPaternForLines = {};
        for(var i in pmDashboard.model.ChartLineSettings)
        {
            var lineChart = pmDashboard.model.ChartLineSettings[i];

            //формируем массив значений для кривой all tasks
            if(lineChart.name == 'all_tasks')
            {
                for (var i in pmDashboard.statsData.jobs[pmDashboard.statsDataMomentType]) {
                    var val = pmDashboard.statsData.jobs[pmDashboard.statsDataMomentType][i];
                    var time = +moment(val[pmDashboard.statsDataMomentType]).tz(window.timeZone).format("x");
                    if (!tasks_data[time]) {
                        tasks_data[time] = val.all;
                        tasks_data_t.push(time)
                    }
                }
                chart_tasks_start_x = ['time'];
                chart_tasks_data = [lineChart.title];
                for (var j in tasks_data_t) {
                    var time = tasks_data_t[j]
                    chart_tasks_start_x.push(time / 1);
                    chart_tasks_data.push(tasks_data[time] / 1);
                }

                linesForChartArr.push(chart_tasks_start_x);
                if(lineChart.active == true)
                {
                    linesForChartArr.push(chart_tasks_data);
                    colorPaternForLines[lineChart.title]=lineChart.color;
                }
            }

            //формируем массив значений для кривой каждого статуса
            if(lineChart.name != 'all_tasks' && lineChart.active == true)
            {
                var chart_tasks_data_var = pmDashboard.getDataForStatusChart(tasks_data, tasks_data_t, lineChart.title);
                linesForChartArr.push(chart_tasks_data_var);
                colorPaternForLines[lineChart.title]=lineChart.color;
            }
        }

        //загружаем график, перечисляем массивы данных для графика и необходимые цвета для графиков
        pmDashboard.model.historyChart.load({
            columns: linesForChartArr,
            colors: colorPaternForLines
        });
    });

    this.model.updateTimeoutId = setTimeout(function(){
        pmDashboard.updateData()
    }, 1000*30)
}




pmDashboard.open  = function(holder, menuInfo, data)
{
    setActiveMenuLi();
    var thisObj = this;

    return $.when(pmDashboard.getUserDashboardSettingsFromAPI(),
        pmDashboard.getDataForDashboardFromBulk()).always(function()
    {
        // Инициализация всех виджетов на странице
        for(var i in pmDashboard.model.widgets)
        {
            for(var j in pmDashboard.model.widgets[i])
            {
                if(pmDashboard.model.widgets[i][j].widget === undefined  )
                {
                    pmDashboard.model.widgets[i][j].widget = new window[pmDashboard.model.widgets[i][j]['name']](pmDashboard.model.widgets[i][j].opt);
                }
            }
        }

        thisObj.updateData()
        $(holder).insertTpl(spajs.just.render('dashboard_page', {}))

        pmwTasksTemplatesWidget.render();
        pmwModulesTemplatesWidget.render();
        pmwAnsibleModuleWidget.render();
        pmwChartWidget.render();

        pmDashboard.model.historyChart = c3.generate({
            bindto: '#c3-history-chart',
            data: {
                x: 'time',
                columns: [
                    ['time'],
                    ['All tasks'],
                    ['OK'],
                    ['ERROR'],
                    ['INTERRUPTED'],
                    ['DELAY'],
                    ['OFFLINE']
                ],
                type: 'area',
                types: {
                    OK: 'line',
                    ERROR: 'line',
                    INTERRUPTED: 'line',
                    DELAY: 'line',
                    OFFLINE: 'line'
                },
            },
            axis: {
                x: {
                    type: 'timeseries',
                    tick: {
                        format: '%Y-%m-%d'
                    }
                }
            },
            color: {
                pattern: ['#1f77b4',  '#276900', '#333333', '#9b97e4', '#808419', '#9e9e9e', '#d62728',  '#9467bd', '#c5b0d5', '#8c564b', '#c49c94', '#e377c2', '#f7b6d2', '#7f7f7f', '#c7c7c7', '#bcbd22', '#dbdb8d', '#17becf', '#9edae5']
            }
        });
        if($('select').is('#chart-period'))
        {
            $('#chart-period').val(pmDashboard.statsDataLastQuery).change();
        }

        //drag and drop для виджетов
        if($('div').is('#dnd-container'))
        {
            widget_sort = Sortable.create(document.getElementById("dnd-container"), {
                animation: 150, // ms, animation speed moving items when sorting, `0` — without animation
                handle: ".dnd-block", // Restricts sort start click/touch to the specified element
                draggable: ".dnd-block", // Specifies which items inside the element should be sortable
                disabled: true,
                onUpdate: function (evt)
                {
                    // console.log("onUpdate[1]", evt);
                    var item = evt.item; // the current dragged HTMLElement
                    //запоминаем новый порядок сортировки
                    var divArr=$('.dnd-block');
                    var idArr=[];
                    for (var i=0; i<divArr.length; i++)
                    {
                        idArr.push(divArr[i].id);
                    }
                    for(var i=0; i<idArr.length; i++)
                    {
                        for(var j=0; j<pmDashboard.model.widgets[0].length; j++)
                        {
                            if(idArr[i].toLowerCase()==pmDashboard.model.widgets[0][j].name.toLowerCase())
                            {
                                pmDashboard.model.widgets[0][j].sortNum=i;
                                pmDashboard.model.widgets[0].sort(pmDashboard.sortCountWidget);
                            }
                        }
                    }
                    pmDashboard.putUserDashboardSettingsToAPI();
                }
            });
        }
    }).promise();

}

tabSignal.connect("polemarch.start", function()
{
    spajs.addMenu({
        id:"home",
        urlregexp:[/^(home|)$/],
        onOpen:function(holder, menuInfo, data){return pmDashboard.open(holder, menuInfo, data);},
        onClose:function(){return pmDashboard.stopUpdates();},
    })

})


/**
 * Базовый класс виджета
 * @type Object
 */
pmDashboardWidget = {
    id:'',
    model:{
        test:1
    },
    render:function(){

    },
    init:function(opt){
        mergeDeep(this.model, opt)
    }
}

/**
 * Создание классов для виджетов: tasks history, run shell command, template tasks, template module
 * @type Object
 */

var pmwTasksTemplatesWidget = inheritance(pmDashboardWidget);
pmwTasksTemplatesWidget.render = function()
{
    var div_id="#pmwTasksTemplatesWidget";
    pmTasksTemplates.showTaskWidget($(div_id));
    return "";
}

var pmwModulesTemplatesWidget = inheritance(pmDashboardWidget);
pmwModulesTemplatesWidget.render = function()
{
    var div_id="#pmwModulesTemplatesWidget";
    pmTasksTemplates.showModuleWidget($(div_id));
    return "";
}

var pmwAnsibleModuleWidget = inheritance(pmDashboardWidget);
pmwAnsibleModuleWidget.render = function()
{
    var div_id="#pmwAnsibleModuleWidget";
    pmAnsibleModule.fastCommandWidget($(div_id));
    return "";
}

var pmwChartWidget=inheritance(pmDashboardWidget);
pmwChartWidget.render = function()
{
    var div_id="#pmwChartWidget";
    var html=spajs.just.render('pmwChartWidget');
    $(div_id).html(html);
    return "";
}


/**
 * Базовый класс виджета показывающего количество элементов
 * @type Object
 */
var pmwItemsCounter = inheritance(pmDashboardWidget);

pmwItemsCounter.model.count = '-';
pmwItemsCounter.model.countObject = pmItems;
pmwItemsCounter.model.nameInStats = "";

pmwItemsCounter.render = function()
{

    var thisObj = this;
    var html = spajs.just.render('pmwItemsCounter', {model:this.model});
    return window.JUST.onInsert(html, function(){});
}
pmwItemsCounter.updateCount = function()
{
    var thisObj = this;
    var statsData=pmDashboard.statsData;
    thisObj.model.count=statsData[thisObj.model.nameInStats];
}

/**
 * Класс виджета показывающий количество хостов
 * @type Object
 */
var pmwHostsCounter = inheritance(pmwItemsCounter);
pmwHostsCounter.model.countObject = pmHosts;
pmwHostsCounter.model.nameInStats = "hosts";

/**
 * Класс виджета показывающий количество шаблонов
 * @type Object
 */
var pmwTemplatesCounter = inheritance(pmwItemsCounter);
pmwTemplatesCounter.model.countObject = pmTemplates;
pmwTemplatesCounter.model.nameInStats = "templates";

/**
 * Класс виджета показывающий количество групп
 * @type Object
 */
var pmwGroupsCounter = inheritance(pmwItemsCounter);
pmwGroupsCounter.model.countObject = pmGroups;
pmwGroupsCounter.model.nameInStats = "groups";

/**
 * Класс виджета показывающий количество проектов
 * @type Object
 */
var pmwProjectsCounter = inheritance(pmwItemsCounter);
pmwProjectsCounter.model.countObject = pmProjects;
pmwProjectsCounter.model.nameInStats = "projects";

/**
 * Класс виджета показывающий количество инвенториев
 * @type Object
 */
var pmwInventoriesCounter = inheritance(pmwItemsCounter);
pmwInventoriesCounter.model.countObject = pmInventories;
pmwInventoriesCounter.model.nameInStats = "inventories";

/**
 * Класс виджета показывающий количество пользователей
 * @type Object
 */
var pmwUsersCounter = inheritance(pmwItemsCounter);
pmwUsersCounter.model.countObject = pmUsers;
pmwUsersCounter.model.nameInStats = "users";
