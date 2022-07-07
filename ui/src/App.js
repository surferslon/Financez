import 'devextreme/dist/css/dx.common.css';
import 'devextreme/dist/css/dx.light.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Header from './Components/Header'
import Reports from './Pages/Reports';
import Entries from './Pages/Entries';
import Settings from './Pages/Settings';


function App() {
  return (
    <BrowserRouter>
      <Header />
      <Routes>
        <Route exact path="/" element={ <Reports /> } />
        <Route path="/entries/" element={ <Entries /> } />
        <Route path="/settings/" element={ <Settings /> } />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
