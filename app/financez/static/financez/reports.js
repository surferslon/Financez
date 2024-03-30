function show_entries(response) {
    let reportEntries = document.getElementById("report_entries");
    reportEntries.style.display = "flex";
    reportEntries.innerHTML = response;
}

function setPeriodResults(data){
    document.getElementById("period_inc").innerText = data.period_inc;
    document.getElementById("period_exp").innerText = data.period_exp;
    document.getElementById("period_sum").innerText = data.period_sum;
}

function createLegend(response) {
    const legend = document.getElementById("chartLegend");
    legend.innerHTML = "";
    legend.innerHTML += '<span>Incomes</span>'
    for (let i = 0; i < response.accounts_incomes.length; i++) {
        legend.innerHTML += `<span class="legendItem">${response.accounts_incomes[i]}</span>`;
    }
    legend.innerHTML += '<span>Expenses</span>'
    for (let i = 0; i < response.accounts_expenses.length; i++) {
        legend.innerHTML += `<span class="legendItem">${response.accounts_expenses[i]}</span>`;
    }
}

function create_background(max_value){
    const chartBackground = document.getElementById("chartBackground");
    chartBackground.innerHTML = "";
    chartBackground.style.height = `${document.getElementById("chartArea").offsetHeight}px`;
    chartBackground.style.width = `${document.getElementById("chartArea").offsetWidth}px`;
    const step = (1000 / max_value) * 100;
    for (let i = 0; i < 100; i += step) {
        const line = document.createElement("div");
        line.style.height = `${step}%`;
        line.style.borderTop = "1px solid #ccc";
        chartBackground.appendChild(line);
    }
}

function create_report(response) {
    setPeriodResults(response);
    createLegend(response);
    const chartArea = document.getElementById("chartArea")
    const periodTitles = document.getElementById("periodTitles")
    chartArea.innerHTML = "";
    periodTitles.innerHTML = "";
    const periodsLen = Object.keys(response.results).length;
    const maxValue = response.max_value;
    chartArea.style.gridTemplateColumns = `repeat(${periodsLen}, 1fr)`;
    periodTitles.style.gridTemplateColumns = `repeat(${periodsLen}, 1fr)`;
    for (const [period, periodVals] of Object.entries(response.results)) {
        const periodDiv = document.createElement("div");
        periodDiv.className = "chartPeriodBlock";
        const periodExps = document.createElement("div");
        const periodIncs = document.createElement("div");
        periodExps.className = "periodBar"
        periodIncs.className = "periodBar"
        for (const [acc, val] of Object.entries(periodVals)) {
            for (const [accName, accValue] of Object.entries(val)) {
                const bar = document.createElement("div");
                const barHeight = (accValue / maxValue) * 100;
                bar.style.height = `${barHeight}%`;
                if (barHeight > 3) {
                    bar.innerHTML = `<span>${accName} ${accValue}</span>`;
                }
                if (acc == "incs") {
                    bar.className = "periodIncs";
                    periodIncs.appendChild(bar);
                } else {
                    bar.className = "periodExps";
                    periodExps.appendChild(bar);
                }
                bar.classList.add("barItem");
            }
        }
        periodDiv.appendChild(periodIncs);
        periodDiv.appendChild(periodExps);
        chartArea.appendChild(periodDiv);
        const periodTitle = document.createElement("div");
        periodTitle.className = "periodTitle";
        periodTitle.innerText = period;
        periodTitles.appendChild(periodTitle);
    }
    create_background(maxValue);
}

function create_report_details(response) {
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


document.addEventListener("DOMContentLoaded", function() {
    const data_url = document.getElementById("chartContainer").dataset.url;
    fetch(data_url)
        .then(response => response.json())
        .then(resp_json => create_report(resp_json));
    document.querySelector('#update-report').addEventListener("click", function(event){
        fetch([
            data_url,
            '?period-from=', document.querySelector('#period-from').value,
            '&period-to=', document.querySelector('#period-to').value,
            '&group_all=', document.querySelector('#group_all').checked
        ].join(''))
        .then(response => response.json())
        .then(resp_json => create_report(resp_json));
    });
    document.querySelector('#modal-background').addEventListener('click', function(event) {
        document.querySelector('#modal-background').style.display = 'none';
        document.querySelector('#report_details').style.display = 'none';
        document.body.style.overflow = 'auto';
    });
});
