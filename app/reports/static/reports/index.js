function showEntries(response) {
    let reportEntries = document.getElementById("report_entries");
    reportEntries.style.display = "flex";
    reportEntries.innerHTML = response;
}
class Chart {
    constructor(dataSet) {
        this.periods = dataSet.periods;
        this.chartArea = document.getElementById("chartArea");
        this.periodTitles = document.getElementById("periodTitles");
        this.chartArea.innerHTML = "";
        this.periodTitles.innerHTML = "";
        const periodsLen = Object.keys(dataSet.results).length;
        const maxValue = dataSet.max_value;
        this.chartArea.style.gridTemplateColumns = `repeat(${periodsLen}, 1fr)`;
        this.periodTitles.style.gridTemplateColumns = `repeat(${periodsLen}, 1fr)`;
        this._setPeriodResults(dataSet);
        this._drawLegend(dataSet);
        this._drawChart(dataSet.results, maxValue);
        this._drawBackground(maxValue)

    }
    _setPeriodResults(data){
        document.getElementById("period_inc").innerText = data.period_inc;
        document.getElementById("period_exp").innerText = data.period_exp;
        document.getElementById("period_sum").innerText = data.period_sum;
    }

    _drawLegend(response) {
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

    _drawBackground(maxValue){
        const chartBackground = document.getElementById("chartBackground");
        chartBackground.innerHTML = "";
        chartBackground.style.height = `${document.getElementById("chartArea").offsetHeight}px`;
        chartBackground.style.width = `${document.getElementById("chartArea").offsetWidth}px`;
        let stepValue = 1;
        let tmpValue = maxValue;
        while (tmpValue >= 10) {
            tmpValue /= 10;
            stepValue *= 10;
        }
        const stepPrc = (stepValue / maxValue) * 100;
        let currentScale = 0;
        let prcFilled = 0;
        while (prcFilled + stepPrc <= 100) {
            const line = document.createElement("div");
            const subLine = document.createElement("div")
            line.className = "bgLine";
            subLine.className = "bgSubLine "
            line.style.height = `${stepPrc}%`;
            line.innerHTML = currentScale;
            chartBackground.appendChild(line);
            line.appendChild(subLine);
            currentScale += stepValue;
            prcFilled += stepPrc;
        }
    }

    _drawChartLabel(bar, barHeight, accValue, accName) {
        if (barHeight > 3) {
            bar.innerHTML = `<div class="barLabel"><span>${accValue.toFixed(2)}</span><span>${accName}</span></div>`;
        }
    }
    _appendChartLabel(periodIncs, periodExps, bar, acc) {
        if (acc == "incs") {
            bar.classList.add("periodIncs");
            periodIncs.appendChild(bar);
        } else {
            bar.classList.add("periodExps");
            periodExps.appendChild(bar);
        }
    }
    _drawPeriod(periodVals, periodIncs, periodExps, maxValue) {
        for (const [acc, val] of Object.entries(periodVals)) {
            for (const [accName, accValue] of Object.entries(val)) {
                const bar = document.createElement("div");
                const barHeight = (accValue / maxValue) * 100;
                bar.style.height = `${barHeight}%`;
                bar.classList.add("barItem");
                this._drawChartLabel(bar, barHeight, accValue, accName);
                this._appendChartLabel(periodIncs, periodExps, bar, acc);
            }
        }
    }
    _drawChart(periodsData, maxValue) {
        for (const [period, periodVals] of Object.entries(periodsData)) {
            const periodDiv = document.createElement("div");
            periodDiv.className = "chartPeriodBlock";
            const periodIncs = document.createElement("div");
            const periodExps = document.createElement("div");
            periodExps.className = "periodBar"
            periodIncs.className = "periodBar"
            this._drawPeriod(periodVals, periodIncs, periodExps, maxValue)
            periodDiv.appendChild(periodIncs);
            periodDiv.appendChild(periodExps);
            chartArea.appendChild(periodDiv);
            const periodTitle = document.createElement("div");
            periodTitle.className = "periodTitle";
            periodTitle.innerText = period;
            periodTitles.appendChild(periodTitle);
        }
    }
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
            $.get(url, showEntries)
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
            $.get(url, showEntries)
        },
        title: { text: response.title, },
    });
}

function buildChart() {
    const data_url = document.getElementById("chartContainer").dataset.url;
    fetch([
        data_url,
        '?period-from=', document.querySelector('#period-from').value,
        '&period-to=', document.querySelector('#period-to').value,
        '&group_all=', document.querySelector('#group_all').checked
    ].join(""))
    .then(response => response.json())
    .then(resp_json => new Chart(resp_json));
}

document.addEventListener("DOMContentLoaded", function() {
    buildChart();
    document.querySelector('#update-report').addEventListener("click", buildChart());
    document.querySelector('#modal-background').addEventListener("click", function(event) {
        document.querySelector('#modal-background').style.display = 'none';
        document.querySelector('#report_details').style.display = 'none';
        document.body.style.overflow = 'auto';
    });
});
