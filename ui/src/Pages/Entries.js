import '../Styles/Entries.css';
import { useEffect, useState } from 'react';
import { fetchEntries } from '../Api/Main';


function NewEntryBlock() {
  return (
    <div className="row">
      <form method="POST" className="new-entry-form">
        <input type="date" />
        <input />
        <input />
        <input type="number" step="0.01"/>
        <input />
        <button>Add</button>
      </form>
    </div>
  )
}

function MainBookHeader() {
  return (
    <div className="row">
        <div className="main-book-header">
            <div>Date</div>
            <div>DR</div>
            <div>CR</div>
            <div style={{textAlign: "right"}}>Sum</div>
            <div style={{textAlign: "center"}}>Comment</div>
        </div>
    </div>
  )
}

function MainBookFilter() {
  return (
      <div className="row">
        <div className="main-book-settings">
          <input id="date-from" name="date-from" type="date" value="" />
          <label> - </label>
          <input id="date-to" name="date-to" type="date" value="" />
          <button id="show-entries"> show </button>
        </div>
      </div>
  )
}

function Entry({entry}) {
  const addZeroes = function( num ) {
      var value = Number(num);
      var res = num.toString().split(".");
      if(res.length == 1 || (res[1].length < 3)) { value = value.toFixed(3); }
      return value
  }
  return (
    <div className="main-book-row" key={entry.id}>
        <div className="main-book-item">{entry.date}</div>
        <div className="main-book-item">{entry.acc_dr__name}</div>
        <div className="main-book-item">{entry.acc_cr__name}</div>
        <div className="main-book-item" style={{ textAlign: "right" }}>{addZeroes(entry.total)}</div>
        <div className="main-book-item" style={{ paddingLeft: "10px" }}>{entry.comment}</div>
    </div>
  )
}

export default function Entries() {
  const [entries, setEntries] = useState([])

  useEffect(() => {
    fetchEntries().then((resp) => { setEntries(resp.data) })
  }, []);

  return (
    <div>

      <NewEntryBlock />

      <MainBookFilter />

      <MainBookHeader />

      <div className="row">
          <div className="main-book">
            { entries.map((e) => <Entry entry={e} />) }
          </div>
      </div>

    </div>
  );
}
