
export default function AccountTreeModal() {
  return (
      <div id="modal-account-list">
        <div className="account-container">
            <input id="acc_type" hidden />
            <div className="acc-list-block" style={{gridArea: 'a'}}>
                <label className="results-header"> Assets </label>
                <div>  </div>
            </div>
            <div className="acc-list-block" style={{gridArea: "b", borderLeft: "1px solid #dbdbdb"}}>
                <label className="results-header"> Expenses </label>
                <div>  </div>
            </div>
            <div className="acc-list-block" style={{gridArea: "c"}}>
                <label className="results-header"> Plans </label>
                <div>  </div>
            </div>
            <div className="acc-list-block" style={{gridArea: "d"}}>
                <label className="results-header"> Debts </label>
                <div>  </div>
            </div>
            <div className="acc-list-block" style={{gridArea: "e"}}>
                <label className="results-header"> Incomes </label>
                <div>  </div>
            </div>

        </div>
      </div>
  )
}
