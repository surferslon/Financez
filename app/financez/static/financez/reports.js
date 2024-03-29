function show_entries (response) {
    $('#report_entries').css('display', 'flex');
    $('#report_entries').html(response);
}

function mergeSeries(data){
        const seriesSource = [];
        for (let i=0; i<data.accounts_incomes.length; i++) {
            seriesSource.push({
                valueField: data.accounts_incomes[i],
                name: data.accounts_incomes[i],
                stack: "incomes",
            })
        }
        for (let i=0; i<data.accounts_expenses.length; i++) {
            seriesSource.push({
                valueField: data.accounts_expenses[i],
                name: data.accounts_expenses[i],
                stack: "expenses",
            })
        }
        return seriesSource;
    }

function castStrToFloat(data){
    for (let i=0; i<data.length; i++) {
        let resObj = data[i];
        for (let key in resObj) {
            if (key === "group_date") {
                continue;
            }
            resObj[key] = parseFloat(resObj[key]);
        }
    }
    return data;
}

function setPeriodResults(data){
    document.getElementById("period_inc").innerText = data.period_inc;
    document.getElementById("period_exp").innerText = data.period_exp;
    document.getElementById("period_sum").innerText = data.period_sum;
}

function create_report(response) {
    setPeriodResults(response);
    const seriesSource = mergeSeries(response);
    castStrToFloat(response.results);

    $("#chart").dxChart({
        palette: "Soft Pastel",
        dataSource: response.results,
        commonSeriesSettings: {
            argumentField: "group_date",
            type: "stackedBar",
            hoverMode: "allSeriesPoints",
            selectionMode: "allSeriesPoints",
        },
        series: seriesSource,
        legend: {
            horizontalAlignment: "left",
            verticalAlignment: "top",
            position: "outside",
            border: { visible: false },
            columnCount: 1,
        },
        valueAxis: { },
        loadingIndicator: { enabled: true },
        "export": { enabled: false },
        onPointClick: function(e) {
            let data_details_url = $('.demo-container').data('details-url')
            $.get([
                data_details_url,
                '?category=', e.target.series.name,
                '&period-from=', e.target.argument,
                '&period-to=', e.target.argument,
                '&group_details=', false
            ].join(''), create_report_details)
        },
        onLegendClick: function(e) {
            let data_details_url = $('.demo-container').data('details-url')
            $.get([
                data_details_url,
                '?category=', e.target.name,
                '&period-from=', $('#period-from').val(),
                '&period-to=', $('#period-to').val(),
                '&group_details=', $('#group_details').is(':checked')
            ].join(''), create_report_details)
        },
        tooltip: {
            enabled: true,
            customizeTooltip: function (arg) {
                return { text: arg.seriesName + "\n" + parseFloat(arg.valueText).toFixed(3) }
            },
        }
    });
}

var create_report_details = function(response) {
    $("#chart_details").parents('.dx-viewport').removeClass('dx_hidden');
    $("#chart_details").dxChart({
        palette: "soft",
        dataSource: response.results,
        pointSelectionMode: 'single', // or 'single'
        commonSeriesSettings: {
            barPadding: 0.5,
            argumentField: "group_date",
            type: "bar",
            selectionMode: "allSeriesPoints",
            label: {
                visible: true,
                format: {
                    type: "fixedPoint",
                    precision: 3,
                }
            }
        },
        series: response.accounts,
        legend: {
            horizontalAlignment: "left",
            verticalAlignment: "top",
        },
        onPointClick: function(e) {
            acc_id = e.target.series.getValueFields()[0]
            let report_entries_url = $('#report_entries').data('entries-url')
            if ($('#group_details').is(':checked') || e.target.originalArgument == 'Total') {
                url = [
                report_entries_url,
                    '?acc_id=', acc_id,
                    '&period-from=', $('#period-from').val(),
                    '&period-to=', $('#period-to').val(),
                ].join('')
            }
            else {
                url = [
                    report_entries_url,
                    '?acc_id=', acc_id,
                    '&month=', e.target.originalArgument
                ].join('')
            }
            $.get(url, show_entries)
        },
        onLegendClick: function(e) {
            e.target.select();
            acc_id = e.target.getValueFields()[0]
            let report_entries_url = $('#report_entries').data('entries-url')
            url = [
                report_entries_url,
                '?acc_id=', acc_id,
                '&period-from=', $('#period-from').val(),
                '&period-to=', $('#period-to').val(),
            ].join('')
            $.get(url, show_entries)
        },
        title: { text: response.title, },
    });
}

$(function() {
    let data_url = $('.demo-container').data('url')
    $.get(data_url, create_report);
    $('#update-report').click(function(event){
        $.get([
            data_url,
            '?period-from=', $('#period-from').val(),
            '&period-to=', $('#period-to').val(),
            '&group_all=', $('#group_all').is(":checked")
        ].join(''), create_report );
    })
    $('#modal-background').click(function(event) {
        $('#modal-background').css('display', 'none');
        $('#report_details').css('display', 'none');
        $('body').css('overflow', 'auto');
    });
});
