import axios from "axios";
import { API_BASE_URL } from "../Config";
import Cookies from 'js-cookie';

const apiClient = axios.create({
    withCredentials: true,
    baseURL: API_BASE_URL
})


export function SubmitSignup(username, password) {

}

export function SubmitLogin(username, password) {
  return apiClient.post('/api/users/login/', { username, password })
}

export function FetchReportData() {
  return apiClient.get('/api/entries/report_data/');
}

export function fetchEntries() {
  return apiClient.get('/api/entries/list/');
}

export function fetchAccounts() {
  return apiClient.get('/api/accounts/list/');
}

export function postNewEntry(date, acc_dr, acc_cr, total, comment) {
  return apiClient.post(
    '/api/entries/create/', { date, acc_dr, acc_cr, total, comment },
    {headers: { 'X-CSRFToken': Cookies.get('csrftoken') }}
  )
}

export function fetchAccDetails(acc_id, periodFrom, periodTo) {
  return apiClient.get(`/api/entries/report_details/${acc_id}?period-from=${periodFrom}&period-to=${periodTo}`)
}

export function fetchAccEntries(acc_id, month) {
  return apiClient.get(`/api/entries/report_entries/${acc_id}?month=${month}`)
}

export function fetchResults() {
  return apiClient.get('/api/accounts/results/')
}

export function fetchCurrencies() {
  return apiClient.get('/api/currencies/list/')
}

export function postCurrency(id) {
  return apiClient.patch(`/api/currencies/set/${id}`, {selected: true},
    {headers: { 'X-CSRFToken': Cookies.get('csrftoken') }}
  )
}
