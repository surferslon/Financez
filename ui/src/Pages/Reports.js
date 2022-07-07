import '../Styles/Reports.css';
import { FetchReportData } from "../Api/Main"
import { useState, useEffect } from "react"
import { useTranslation, Trans } from 'react-i18next';
import 'devextreme/dist/css/dx.light.css';
import { Chart, Series, CommonSeriesSettings, Legend, ValueAxis, Title, Export, Tooltip } from 'devextreme-react/chart';

import service from './data.js';

const dataSource = service.getMaleAgeData();

function customizeTooltip(arg) {
    return {
      text: `${arg.seriesName} years: ${arg.valueText}`,
    };
  }

function ChartBlock (props) {
    //   const [CVList, setCVList] = useState([])

    //   useEffect(() => {
    //     FetchReportData().then((result) =>  {
    //         setCVList(result.data);
    //         }
    //     )
    //   }, []);

    return (
      // height 750px
      <div className="dx-viewport">
        <Chart id="chart" title="Male Age Structure" dataSource={dataSource} >
            <CommonSeriesSettings argumentField="state" type="stackedBar" />
            <Series valueField="young" name="0-14" />
            <Series valueField="middle" name="15-64" />
            <Series valueField="older" name="65 and older" />
            <ValueAxis position="right">
                <Title text="millions" />
            </ValueAxis>
            <Legend verticalAlignment="bottom" horizontalAlignment="center" itemTextPosition="top" />
            <Export enabled={true} />
            <Tooltip enabled={true} location="edge"
                //   customizeTooltip={this.customizeTooltip}
            />
        </Chart>
      </div>
    );
}

export default function Reports() {
  const { t } = useTranslation();

  return (
      <div>
        <div className="dashboard">

            <div className="settings_block">
                <div>
                    <input id="period-from" name="period-from" type="date"  />
                    <label> - </label>
                    <input id="period-to" name="period-to" type="date"  />
                    <button id="update-report"> {t('update')} </button>
                </div>
                <div className="settings-row">
                    <input className="checkbx" type="checkbox" name="group_all" id="group_all" />
                    <label className="settings-item">{t('Group all')}</label>
                    <input className="checkbx" type="checkbox" name="group_details" id="group_details" />
                    <label className="settings-item">{t('Group details')}</label>
                </div>
            </div>

            <div className="results">

                <div className="results-block">
                    <div className="results-header">{t('Results')}</div>
                    <span>{t('Incomes')}</span>
                    <span style={{textAlign: 'right'}} id="period_inc"></span>
                    <span>{t('Expenses')}</span>
                    <span style={{textAlign: 'right'}} id="period_exp"></span>
                    <span >{t('Result')}</span>
                    <span style={{textAlign: 'right'}} id="period_sum"></span>
                </div>

                <div className="results-block">
                    <div className="results-header">{t('Assets')}</div>
                    {/* {% include 'financez/results.html' with qs=results_queryset type=result_types.assets %} */}
                </div>

                <div className="results-block">
                    <div className="results-header">{t('Debts')}</div>
                    {/* {% include 'financez/results.html' with qs=results_queryset type=result_types.debts %} */}
                </div>

                <div className="results-block">
                    <div className="results-header">{t('Plans')}</div>
                    {/* {% include 'financez/results.html' with qs=results_queryset type=result_types.plans %} */}
                </div>

            </div>

        </div>

        <ChartBlock />

        <div className="dx-viewport dx_hidden">
            <div className="demo-container">
                <div id="chart_details"></div>
            </div>
        </div>

        <div className="report_block" id="report_entries" data-entries-url="{% url 'report_entries' %}">
        </div>

      </div>
  );
}