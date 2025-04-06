let checkedAccs = [];

function detailsOnClick(event) {
    const { url, accid, period } = event.target.dataset;
    const params = new URLSearchParams({ accid, period });
    fetch(`${url}?${params}`)
        .then(response => response.text())
        .then(resp => {
            const entriesElement = document.getElementById("report_entries");
            entriesElement.style.display = "flex";
            entriesElement.innerHTML = resp
        })
}

function checkboxChange(event) {
    const accName = event.target.id;
    if (event.target.checked && !checkedAccs.includes(accName)) {
        checkedAccs.push(accName);
    } else {
        checkedAccs = checkedAccs.filter((item) => item !== accName);
    }
}

function showBarDetails(event, accId, period) {
    if (event.target.classList.contains('barTooltip') || event.target.closest('.barTooltip')) {
        return;
    }
    const {detailsUrl} = document.getElementById("chartContainer").dataset;
    const params = new URLSearchParams({ accId, period });
    const url  = `${detailsUrl}?${params}`
    fetch(url)
        .then(response => response.text())
        .then(resp => {
            document.getElementById(`tooltip-${period}-${accId}`).innerHTML = resp
        })
}

class Chart {
    constructor(dataSet, init) {
        if (Object.keys(dataSet.results).length === 0) {
            return;
        }
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
        checkBox.id = `accFilter-${accounts[i][0]}`;
        legendItem.appendChild(checkBox);
        legendItem.innerHTML += `<span>${accounts[i][1]}</span>`;
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
    _drawChartLabel(bar, barHeight, accName) {
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
    _appendToolTip(bar, barHeight, accId, accName, accValue, period) {
        const barTooltip = document.createElement("div");
        barTooltip.className = "barTooltip";
        barTooltip.id = `tooltip-${period}-${accId}`;
        barTooltip.style.top = `${barHeight}*0.2%`;
        barTooltip.innerHTML = `${accName} <br> ${accValue.toFixed(2)}`
        bar.appendChild(barTooltip);
    }
    _drawPeriod(period, periodVals, periodIncs, periodExps, maxValue) {
        for (const [acc, val] of Object.entries(periodVals)) {
            for (const [accIdName, accValue] of Object.entries(val)) {
                const trimmed = accIdName.slice(1, -1)
                const accId = trimmed.split(",")[0].trim();
                const accName = trimmed.split(",")[1].trim().slice(1, -1);
                const accFilter = document.getElementById(`accFilter-${accId}`);
                if (!accFilter.checked) {
                    continue;
                }
                const bar = document.createElement("div");
                const barHeight = (accValue / maxValue) * 100;
                bar.style.height = `${barHeight}%`;
                bar.classList.add("barItem");
                bar.addEventListener('click', (event) => showBarDetails(event, accId, period))
                this._drawChartLabel(bar, barHeight, accName);
                this._appendChartLabel(periodIncs, periodExps, bar, acc);
                this._appendToolTip(bar, barHeight, accId, accName, accValue, period);
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
                const trimmed = accName.slice(1, -1)
                const accId = trimmed.split(",")[0].trim();
                const accFilter = document.getElementById(`accFilter-${accId}`);
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
                    const trimmed = accName.slice(1, -1)
                    const accId = trimmed.split(",")[0].trim();
                    const accFilter = document.getElementById(`accFilter-${accId}`);
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
            this._drawPeriod(period, periodVals, periodIncs, periodExps, maxValue)
            periodDiv.appendChild(periodIncs);
            periodDiv.appendChild(periodExps);
            chartArea.appendChild(periodDiv);
        }
    }
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
