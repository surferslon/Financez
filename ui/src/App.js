import 'devextreme/dist/css/dx.common.css';
import 'devextreme/dist/css/dx.light.css';
import { useEffect, useState } from 'react'
import { BrowserRouter, Routes, Route, Outlet, Navigate } from 'react-router-dom'
import Cookies from 'js-cookie';
import Entries from './Pages/Entries';
import Header from './Components/Header';
import Footer from './Components/Footer';
import Login from './Pages/Login'
import Reports from './Pages/Reports';
import Settings from './Pages/Settings';


const AppLayout = ({setUser}) => {
  const loggedInUser = localStorage.getItem("user");

  useEffect(() => {
    if (loggedInUser) {
      setUser(loggedInUser);
    }
  }, []);

  if (!loggedInUser) {
    localStorage.clear();
    Cookies.remove('csrftoken')
    return <Navigate to="/login" replace />;
  }

  return (
    <>
      <Header />
      <Outlet />
      {/* <Footer /> */}
    </>
  )
};

const LoginLayout = () => (
  <Outlet />
);


function App() {
  const [user, setUser] = useState(null);
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginLayout />}>
          <Route path="/login/" element={ <Login setUser={setUser} /> } />
        </Route>
        <Route path="/" element={<AppLayout setUser={setUser} /> } >
          <Route path="/reports/" element={ <Reports /> } />
          <Route path="/entries/" element={ <Entries /> } />
          <Route path="/settings/" element={ <Settings /> } />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
