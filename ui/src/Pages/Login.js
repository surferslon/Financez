import '../Styles/Login.css';
import { SubmitLogin } from "../Api/Main";
import { useNavigate } from "react-router-dom";
import React from 'react'


export default function Login(props) {
  const navigate = useNavigate();
  const { setUser } = props;
  const [error, setError] = React.useState('');
  const OnSubmit = e => {
    e.preventDefault();
    const username = e.target.username.value;
    const password = e.target.password.value;
    SubmitLogin(username, password)
      .then( response => {
        setUser(username);
        localStorage.setItem('user', username);
        navigate('/reports/', {replace: true});
      })
      .catch((err) => { setError(err.response.data['non_field_errors']); })
  }

  return (
    <div>

      <div className="frame">
          <div className="frame-header">Financez</div>
          <form className="auth-form" onSubmit={OnSubmit}>
            <input name='username'></input>
            <input name='password'></input>
            <input  type="hidden" name="next" value="next" />
            <button type="submit" value="login">Log in</button>
            <div className="error-list">
              {error}
            </div>
          </form>
      </div>

      <div className="frame signup-frame">
          <span> "Don't have an account?"</span>
          <a href=""></a>
      </div>

    </div>
  );
}
