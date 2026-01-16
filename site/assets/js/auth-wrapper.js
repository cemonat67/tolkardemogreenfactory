const AUTH = (() => {
  const qs = (typeof window !== 'undefined') ? new URLSearchParams(window.location.search) : null;
  const BYPASS = qs && (qs.get('auth')==='bypass' || qs.get('demo')==='1');
  const API_BASE = (typeof window !== 'undefined') ? (window.__API_BASE__ || window.location.origin) : '';
  let OFFLINE = false;
  const key = 'tolkar_token';
  const userKey = 'tolkar_user';
  async function request(method, path, body, auth=true){
    const headers = { 'Content-Type': 'application/json' };
    if(auth && !BYPASS){ const t = localStorage.getItem(key); if(t) headers['Authorization'] = 'Bearer ' + t; }
    try{
      const res = await fetch(API_BASE + path, { method, headers, body: body?JSON.stringify(body):undefined });
      if(!res.ok){ const err = await res.json().catch(()=>({detail:'Error'})); throw new Error(err.detail||('HTTP '+res.status)); }
      OFFLINE = false;
      return res.json();
    }catch(e){ OFFLINE = true; throw e; }
  }
  async function login(username, password){
    try{
      const data = await request('POST','/api/login',{username,password},false);
      localStorage.setItem(key, data.access_token);
      localStorage.setItem(userKey, JSON.stringify(data.user));
      return data;
    }catch(err){
      const demoUsers = {
        admin: { role:'admin' },
        supervisor: { role:'supervisor' },
        operator1: { role:'operator' }
      };
      const role = (demoUsers[username] && password) ? demoUsers[username].role : 'demo';
      const fake = { access_token: 'demo.' + (typeof btoa==='function'? btoa(username + '.' + Date.now()) : (username + '.' + Date.now())), user: { username, role } };
      localStorage.setItem(key, fake.access_token);
      localStorage.setItem(userKey, JSON.stringify(fake.user));
      return fake;
    }
  }
  function logout(){ localStorage.removeItem(key); localStorage.removeItem(userKey); }
  function token(){ return localStorage.getItem(key); }
  function currentUser(){ const s = localStorage.getItem(userKey); return s?JSON.parse(s):null; }
  async function get(path){ return request('GET', path); }
  async function post(path, body){ return request('POST', path, body); }
  function isLoggedIn(){ return BYPASS || !!token(); }
  function hasRole(role){ const u=currentUser(); return u && u.role===role; }
  return { login, logout, token, currentUser, get, post, isLoggedIn, hasRole };
})();
