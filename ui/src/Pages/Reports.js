import '../Styles/Reports.css';
import { FetchReportData } from "../Api/Main"
import { useState, useEffect } from "react"
import { useTranslation, Trans } from 'react-i18next';
import 'devextreme/dist/css/dx.light.css';
import { Chart, Series, CommonSeriesSettings, Legend, ValueAxis, Tooltip, LoadingIndicator} from 'devextreme-react/chart';


function ChartBlock (props) {
  const [reportData, setReportData] = useState([])
  const [seriesSource, setSeriesSource] = useState([])

  useEffect(() => {
    FetchReportData().then((result) =>  {
        setReportData(result.data);
        var response = result.data;
        var seriesCompiled = [];
        for (var i=0; i<response.accounts_incomes.length; i++) {
            seriesCompiled.push({
                valueField: response.accounts_incomes[i],
                name: response.accounts_incomes[i],
                stack: 'incomes',
            })
        }
        for (var i=0; i<response.accounts_expenses.length; i++) {
            seriesCompiled.push({
                valueField: response.accounts_expenses[i],
                name: response.accounts_expenses[i],
                stack: 'expenses',
            })
        }
        setSeriesSource(seriesCompiled)
    })
  }, []);

  function customizeTooltip(arg) {
    return {
      text: `${arg.seriesName} \n ${parseFloat(arg.valueText).toFixed(3)}`
    };
  }

  return (
    <div className="dx-viewport">
      <Chart id="chart" palette="Soft Pastel" dataSource={reportData.results} >

        <CommonSeriesSettings argumentField="group_date" type="stackedBar" />

        {seriesSource.map((value, index) => {
            return <Series valueField={value.valueField} name={value.name} stack={value.stack} key={index}/>
        })}

        <ValueAxis position="left" />
        <Legend verticalAlignment="top" horizontalAlignment="left" itemTextPosition="right" />
        <Tooltip enabled={true} location="edge" customizeTooltip={customizeTooltip} />
        <LoadingIndicator enabled={true} />

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
