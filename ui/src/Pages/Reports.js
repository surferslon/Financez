import '../Styles/Reports.css';
import 'devextreme/dist/css/dx.light.css';
import { FetchReportData, fetchAccDetails, fetchAccEntries } from "../Api/Main"
import { useState, useEffect } from "react"
import { useTranslation, Trans } from 'react-i18next';
import { Chart, Series, CommonSeriesSettings, Legend, ValueAxis, Tooltip, LoadingIndicator} from 'devextreme-react/chart';


function AccEntriesBlock({ accEntries }){
  return (
      <div className="report_block" id="report_entries">
        <div className="reposrt-details-wrapper">
            <label>Total:</label>
            <div>{accEntries.total_sum}</div>
            <br />
            <div className="report-details-header">
                <div>Date</div>
                <div>Sum</div>
                <div>Comment</div>
            </div>
            {accEntries.entries.map((entry, index) => (
              <>
                <br />
                <div className="report-details-entries" key={index}>
                  <div>{entry.date}</div>
                  <div>{entry.total}</div>
                  <div>{entry.comment}</div>
                </div>
              </>
              )
            )}
        </div>
      </div>
  )
}

function ChartDeatailsBlock({ detailsData, setAccEntries, fetchAccEntries}) {
  function handleClick ({target}) {
    const acc_id = target.series.getValueFields()[0]
    const month = target.originalArgument
    fetchAccEntries(acc_id, month)
      .then((resp) => setAccEntries(resp.data))
  }

  return (
    <div className="dx-viewport">
      <div id="chart_details">

        <Chart id="chartDetails" palette="Soft" dataSource={detailsData.results} onPointClick={handleClick} >

          <CommonSeriesSettings argumentField="group_date" type="bar" />
          {detailsData.accounts.map((value, index) => {
              return <Series valueField={value.valueField} name={value.name} key={index} />
          })}

        </Chart>

      </div>
    </div>
  )
}

function ChartBlock ({ setAccDetails }) {
  const [reportData, setReportData] = useState([])
  const [seriesSource, setSeriesSource] = useState([])

  useEffect(() => {
    FetchReportData().then((result) =>  {
        setReportData(result.data);
        var response = result.data;
        var seriesCompiled = [];
        for (var i=0; i<response.accounts_incomes.length; i++) {
            seriesCompiled.push({
                id: response.accounts_incomes[i].id,
                name: response.accounts_incomes[i].name,
                stack: 'incomes',
            })
        }
        for (var i=0; i<response.accounts_expenses.length; i++) {
            seriesCompiled.push({
                id: response.accounts_expenses[i].id,
                name: response.accounts_expenses[i].name,
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

  function SeriesClick({ target }) {
    const accId = target.series.getValueFields()[0]
    fetchAccDetails(accId, target.argument, target.argument)
      .then(({ data }) => {setAccDetails(data)})
  }

  return (
    <div className="dx-viewport">
      <Chart id="chart" palette="Soft Pastel" dataSource={reportData.results} onPointClick={SeriesClick}>

        <CommonSeriesSettings argumentField="group_date" type="stackedBar" />

        {seriesSource.map((value, index) => {
            return <Series valueField={value.id} name={value.name} stack={value.stack} key={index} />
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
  const [accDetails, setAccDetails] = useState({})
  const [accEntries, setAccEntries] = useState({})

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

      <ChartBlock setAccDetails={setAccDetails} />

      {accDetails.results && <ChartDeatailsBlock
        detailsData={accDetails}
        setAccEntries={setAccEntries}
        fetchAccEntries={fetchAccEntries}
      />}

      {accEntries.entries && <AccEntriesBlock accEntries={accEntries} /> }

    </div>
  );
}
