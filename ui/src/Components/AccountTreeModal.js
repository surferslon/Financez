function AccountItem({ accs, targetFunc, setAccTreeIsOpen, padding }) {
  const handleClick = (acc, targetFunc) => {
    targetFunc({'name': acc.name, 'id': acc.pk})
    setAccTreeIsOpen(false);
  }
  const newPadding = padding + 20

  return (
    <div>
        { accs.map((acc) =>
          <>
            <div
              key={acc.pk}
              className="acc-item"
              onClick={e => handleClick(acc, targetFunc)}
              style={{paddingLeft: `${newPadding}px`}}
              >
                {acc.name}
            </div>
            {
              acc.subaccs && <AccountItem
                accs={acc.subaccs}
                targetFunc={targetFunc}
                padding={newPadding}
                setAccTreeIsOpen={setAccTreeIsOpen}
              />
            }
          </>
        )}
    </div>
  )
}


export default function AccountTreeModal({setAccTreeIsOpen, accList, targetAcc, targetFuncs}) {
  const targetFunc = targetFuncs[targetAcc];
  const closeModal = () => {
    setAccTreeIsOpen(false)
  }
  const padding = 0;
  return (
    <>

      <div id="modal-account-list">
        <div className="account-container">

          <input id="acc_type" hidden />
          <div className="acc-list-block" style={{gridArea: 'a'}}>
            <label className="results-header"> Assets </label>
            <AccountItem accs={accList.assets} targetFunc={targetFunc} padding={padding} setAccTreeIsOpen={setAccTreeIsOpen}/>
          </div>
          <div className="acc-list-block" style={{gridArea: "b", borderLeft: "1px solid #dbdbdb"}}>
            <label className="results-header"> Expenses </label>
            <AccountItem accs={accList.expenses} targetFunc={targetFunc} padding={padding} setAccTreeIsOpen={setAccTreeIsOpen} />
          </div>
          <div className="acc-list-block" style={{gridArea: "c"}}>
            <label className="results-header"> Plans </label>
            <AccountItem accs={accList.plans} targetFunc={targetFunc} padding={padding} setAccTreeIsOpen={setAccTreeIsOpen} />
          </div>
          <div className="acc-list-block" style={{gridArea: "d"}}>
            <label className="results-header"> Debts </label>
            <AccountItem accs={accList.debts} targetFunc={targetFunc} padding={padding} setAccTreeIsOpen={setAccTreeIsOpen}/>
          </div>
          <div className="acc-list-block" style={{gridArea: "e"}}>
            <label className="results-header"> Incomes </label>
            <AccountItem accs={accList.incomes} targetFunc={targetFunc} padding={padding} setAccTreeIsOpen={setAccTreeIsOpen}/>
          </div>

        </div>
      </div>

      <div id="modal-background" onClick={closeModal} />

    </>
  )
}
