function showEntries(response) {
    let reportEntries = document.getElementById("report_entries");
    reportEntries.style.display = "flex";
    reportEntries.innerHTML = response;
}

let checkedAccs = [];

function checkboxChange(event) {
        const accName = event.target.id;
        if (event.target.checked && !checkedAccs.includes(accName)) {
            checkedAccs.push(accName);
        } else {
            checkedAccs = checkedAccs.filter((item) => item !== accName);
        }
    }

class Chart {
    constructor(dataSet, init) {
        const periodsLen = Object.keys(dataSet.results).length;
        this.init = init;
        this._initChartAreas(periodsLen);
        this._setPeriodResults(dataSet);
        this._drawLegend(dataSet);
        const maxValue = this._getMaxValue(dataSet.results);
        this._drawChart(dataSet.results, maxValue);
        this._drawBackground(maxValue)
        this.init = false;
    }
    _initChartAreas(periodsLen) {
        const columnsStyle = `repeat(${periodsLen}, 1fr)`;
        this.chartArea = document.getElementById("chartArea");
        this.chartArea.innerHTML = "";
        this.chartArea.style.gridTemplateColumns = columnsStyle;
        this.periodTitles = document.getElementById("chartPeriodTitles");
        this.periodTitles.innerHTML = "";
        this.periodTitles.style.gridTemplateColumns = columnsStyle;
        this.periodSums = document.getElementById("chartPeriodSums");
        this.periodSums .style.gridTemplateColumns = columnsStyle;
        this.periodSums.innerHTML = "";
    }
    _setPeriodResults(data){
        document.getElementById("period_inc").innerText = data.period_inc;
        document.getElementById("period_exp").innerText = data.period_exp;
        document.getElementById("period_sum").innerText = data.period_sum;
    }
    _createLegendItem(accounts, i) {
        const legendItem = document.createElement("div");
        const checkBox = document.createElement("input");
        legendItem.className = "legendItem";
        checkBox.type = "checkbox";
        checkBox.id = `accFilter-${accounts[i]}`;
        legendItem.appendChild(checkBox);
        legendItem.innerHTML += `<span>${accounts[i]}</span>`;
        if (this.init) {
            checkedAccs.push(checkBox.id);
        }
        return legendItem;
    }
    _drawLegend(response) {
        const legend = document.getElementById("chartLegend");
        legend.innerHTML = "";
        legend.innerHTML += '<span>Incomes</span>'
        for (let i = 0; i < response.accounts_incomes.length; i++) {
            const legendItem = this._createLegendItem(response.accounts_incomes, i);
            legend.appendChild(legendItem);
            const checkBox = legendItem.querySelector("input");
            checkBox.addEventListener("change", checkboxChange);
            checkBox.checked = checkedAccs.includes(checkBox.id);
        }
        const legendHeader = document.createElement("span");
        legendHeader.innerText = "Expenses";
        legend.appendChild(legendHeader);
        for (let i = 0; i < response.accounts_expenses.length; i++) {
            const legendItem = this._createLegendItem(response.accounts_expenses, i);
            legend.appendChild(legendItem);
            const checkBox = legendItem.querySelector("input");
            checkBox.addEventListener("change", checkboxChange);
            checkBox.checked = checkedAccs.includes(checkBox.id);
        }
    }
    _drawBackground(maxValue){
        const chartBackground = document.getElementById("chartBackground");
        chartBackground.innerHTML = "";
        chartBackground.style.height = `${this.chartArea.offsetHeight}px`;
        chartBackground.style.width = `${this.chartArea.offsetWidth}px`;
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
            bar.innerHTML = `<span>${accName}</span>`;
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
    _appendToolTip(bar, barHeight, accName, accValue) {
        const barTooltip = document.createElement("div");
        barTooltip.className = "barTooltip";
        barTooltip.style.top = `${barHeight}*0.2%`;
        barTooltip.innerText = `${accName} ${accValue.toFixed(2)}`
        bar.appendChild(barTooltip);
    }
    _drawPeriod(periodVals, periodIncs, periodExps, maxValue) {
        for (const [acc, val] of Object.entries(periodVals)) {
            for (const [accName, accValue] of Object.entries(val)) {
                const accFilter = document.getElementById(`accFilter-${accName}`);
                if (!accFilter.checked) {
                    continue;
                }
                const bar = document.createElement("div");
                const barHeight = (accValue / maxValue) * 100;
                bar.style.height = `${barHeight}%`;
                bar.classList.add("barItem");
                this._drawChartLabel(bar, barHeight, accValue, accName);
                this._appendChartLabel(periodIncs, periodExps, bar, acc);
                this._appendToolTip(bar, barHeight, accName, accValue);
            }
        }
    }
    _addPeriodTitle(title) {
        const periodTitle = document.createElement("div");
        periodTitle.className = "periodTitle";
        periodTitle.innerText = title;
        this.periodTitles.appendChild(periodTitle);
    }
    _addPeriodSums(periodVals) {
        let periodIncSum = 0;
        let periodExpSum = 0;
        for (const [acc, val] of Object.entries(periodVals)) {
            for (const [accName, accValue] of Object.entries(val)) {
                const accFilter = document.getElementById(`accFilter-${accName}`);
                if (!accFilter.checked) {
                    continue;
                }
                if (acc == "incs") {
                    periodIncSum += accValue;
                } else {
                    periodExpSum += accValue;
                }
            }
        }
        const sumsElement = document.createElement("div");
        sumsElement.className = "sumsElement"
        sumsElement.innerHTML = `
            <span>${periodIncSum.toFixed(2)}</span>
            <span>${periodExpSum.toFixed(2)}</span>
        `
        this.periodSums.appendChild(sumsElement);
    }
    _getMaxValue(periodsData) {
        let maxValues = [];
        for (const [period, periodVals] of Object.entries(periodsData)) {
            for (const [acc, val] of Object.entries(periodVals)) {
                let entryTypeMax = 0;
                for (const [accName, accValue] of Object.entries(val)) {
                    const accFilter = document.getElementById(`accFilter-${accName}`);
                    if (!accFilter.checked) {
                        continue;
                    }
                    entryTypeMax += accValue;
                }
                maxValues.push(entryTypeMax);
            }
        }
        return Math.max(...maxValues);
    }
    _drawChart(periodsData, maxValue) {
        for (const [period, periodVals] of Object.entries(periodsData)) {
            this._addPeriodTitle(period);
            this._addPeriodSums(periodVals);
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

function buildChart(init=true) {
    const data_url = document.getElementById("chartContainer").dataset.url;
    fetch([
        data_url,
        '?period-from=', document.querySelector('#period-from').value,
        '&period-to=', document.querySelector('#period-to').value,
        '&group_all=', document.querySelector('#group_all').checked
    ].join(""))
    .then(response => response.json())
    .then(resp_json => new Chart(resp_json, init));
}

document.addEventListener("DOMContentLoaded", function() {
    document.querySelector('#update-report').addEventListener("click", () => {buildChart(false)});
    document.querySelector('#modal-background').addEventListener("click", function(event) {
        document.querySelector('#modal-background').style.display = 'none';
        document.querySelector('#report_details').style.display = 'none';
        document.body.style.overflow = 'auto';
    });
    buildChart();
});
