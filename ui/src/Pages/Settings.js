import { useEffect, useState } from 'react';
import { fetchCurrencies, postCurrency } from '../Api/Main';
import '../Styles/settings.css';


function CurrencyBlock() {
  const [currencies, setCurrencies] = useState([])
  const [currency, setCurrency] = useState(localStorage.getItem("currency"))

  useEffect(() => {
    fetchCurrencies().then((resp) => setCurrencies(resp.data))
  }, [currency]);

  const handleClick = (id, name) => {
    postCurrency(id).then(() => {
        setCurrency(name)
        localStorage.setItem('currency', name);
    })
  }

  return (
    <div className='settings-row'>
      <div> Currency </div>
      <div className='currencies-list' data-url="">
        { currencies && currencies.map((cur) => (
          <div key={cur.pk}
            className="currency-row"
            style={{ fontWeight: cur.selected == true? 'bold': 'normal' }}
          >
            <div data-curid="" className="cur-button" onClick={e => handleClick(cur.pk, cur.name)}>
              {cur.name}
            </div>
          </div>
        ))}
        <a href='#' id="add-currency-button"> + </a>
      </div>
    </div>
  )
}

function ModalNewAcc() {
    return (
        <div className="settings-modal" id="modal-new-acc">
            <form id="form-new-acc" method='post' action="{% url 'new_acc' %}">
                <button className="modal-create-button">Create</button>
            </form>
        </div>
    )
}

function ModalDelAcc() {

  return (
      <div className='settings-modal' id="modal-del-acc">
          <form id="form-del-acc" method='post'>
              <input name="section" value="" hidden />
              <label>Are you sure?</label>
              <button>Yes</button>
          </form>
      </div>
  )
}

function ModalNewCur() {
  return (
    <div className='settings-modal' id="modal-new-cur">
      <form id="form-new-cur" method='post' action="">
        <br />
        <button>Create</button>
      </form>
    </div>
  )
}

function AccTree() {
    return (
      <div className="acc-tree">
          <div className="acc-tree-row-header">
              <div className="acc-tree-header">Name</div>
              <div className="acc-tree-header">Parent</div>
              <div className="acc-tree-header">Order</div>
              <div className="acc-tree-header">Type</div>
              <div className="acc-tree-header">Results</div>
              <button id="new-acc-button"> + </button>
          </div>
      </div>
    )
}

function LanguageBlock() {
  return (
    <div className='settings-row'>
        <div>
            UI Language
        </div>
        <div>
            <form id="language-form" action="" method="post">
                <input name="next" type="hidden" value="" />
                <select name="language" id="language-selector" value="">
                    <option>English</option>
                </select>
            </form>
        </div>
    </div>
  )
}

function LogoutBlock() {
  return (
    <div className="settings-row">
      <a href="">Log out</a>
    </div>
  )
}

function Menu() {
  return (
    <div className="settings-menu" id="">
      <a className="set-menu-item" href="" id="menu-general">General</a>
      <a className="set-menu-item" href="" id="menu-assets">Assets</a>
      <a className="set-menu-item" href="" id="menu-plans">Plans</a>
      <a className="set-menu-item" href="" id="menu-debts">Debts</a>
      <a className="set-menu-item" href="" id="menu-incomes">Incomes</a>
      <a className="set-menu-item" href="" id="menu-expenses">Expenses</a>
    </div>
  )
}

function GeneralSettings() {
  return (
    <div className='settings-block'>
      <CurrencyBlock />
      <LanguageBlock />
      <LogoutBlock />
    </div>
  )
}

export default function Settings() {

  return (
    <div>
      <link rel="stylesheet" type="text/css" href="" />

      <div className="row">
        <div id="acc-list" className="account-list" data-url="">
            <Menu />
            <GeneralSettings />
          </div>
      </div>

    </div>
  );
}
