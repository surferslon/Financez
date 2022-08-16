import '../Styles/Entries.css';
import { useEffect, useState } from 'react';
import { fetchEntries, fetchAccounts, postNewEntry } from '../Api/Main';
import AccountTreeModal from '../Components/AccountTreeModal';


function NewEntryBlock({accList, setEntries}) {
  const [date, setDate] = useState()
  const [comment, setComment] = useState()
  const [sum, setSum] = useState()
  const [newDrAcc, setNewDrAcc] = useState("");
  const [newCrAcc, setNewCrAcc] = useState("");
  const [accTreeIsOpen, setAccTreeIsOpen] = useState(false);
  const [targetAcc, setTargetAcc] = useState('')
  const [err, setErr] = useState('')

  const handleClick = (targetAcc) => {
    setTargetAcc(targetAcc);
    setAccTreeIsOpen(true);
  }
  const handleSubmit = (e) => {
    e.preventDefault();
    postNewEntry(date, newDrAcc.id, newCrAcc.id, sum, comment)
      .then((resp) => {
        setNewCrAcc({'name': ''});
        setNewDrAcc({'name': ''});
        setSum('');
        setComment('');
        fetchEntries().then(({ data }) => { console.log('data', data); setEntries(data) })
      })
      .catch((err) => {setErr('err')})
  }

  return (
    <>

      <div className="row">
        <form className="new-entry-form">
          <input onChange={(e) => setDate(e.target.value)} type="date" />
          <input onClick={e => handleClick('dr')} value={newDrAcc.name} />
          <input onClick={e => handleClick('cr')} value={newCrAcc.name} />
          <input onChange={(e) => setSum(e.target.value)} type="number" step="0.01" value={sum} />
          <input onChange={(e) => setComment(e.target.value)} value={comment} />
          <button onClick={handleSubmit}>Add</button>
        </form>
      </div>

      {accTreeIsOpen && <AccountTreeModal
        setAccTreeIsOpen={setAccTreeIsOpen}
        accList={accList}
        targetAcc={targetAcc}
        targetFuncs={{'dr': setNewDrAcc, 'cr': setNewCrAcc}}
        />
      }

    </>
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
          <input id="date-from" name="date-from" type="date"  />
          <label> - </label>
          <input id="date-to" name="date-to" type="date"  />
          <button id="show-entries"> show </button>
        </div>
      </div>
  )
}

function Entry({entry}) {
  const addZeroes = function( num ) {
      var value = Number(num);
      var res = num.toString().split(".");
      if(res.length === 1 || (res[1].length < 3)) { value = value.toFixed(3); }
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
  const [entries, setEntries] = useState([]);
  const [accList, setAccList] = useState([]);

  useEffect(() => {
    fetchEntries().then((resp) => { setEntries(resp.data) })
    fetchAccounts().then(({ data }) => { setAccList(data) })
  }, []);

  return (
    <div>

      <NewEntryBlock accList={accList} setEntries={setEntries} />

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
