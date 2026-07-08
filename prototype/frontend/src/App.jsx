import React, { useEffect, useMemo, useState } from 'react';
import axios from 'axios';
import {
  AlertCircle,
  CheckCircle2,
  Copy,
  Trash2,
  ExternalLink,
  Link2,
  LogOut,
  Plus,
  Shield,
  Zap,
} from 'lucide-react';
import './index.css';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const addDays = (days) => {
  const date = new Date();
  date.setDate(date.getDate() + Number(days));
  return date.toISOString();
};

const formatDate = (value) => (value ? new Date(value).toLocaleDateString() : 'No expiry');
const daysLabel = (days) => (days ? `${days} days` : 'No expiry');
const tokenLabel = (limit) => (limit ? `${limit} links` : 'Unlimited links');

function App() {
  const [apiKey, setApiKey] = useState(localStorage.getItem('merchantKey') || '');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoginView, setIsLoginView] = useState(true);
  const [authLoading, setAuthLoading] = useState(false);
  const [authError, setAuthError] = useState('');
  const [loginKey, setLoginKey] = useState('');
  const [regCode, setRegCode] = useState('');
  const [regName, setRegName] = useState('');
  const [selectedPlan, setSelectedPlan] = useState('Free');

  const [plans, setPlans] = useState([]);
  const [profile, setProfile] = useState(null);
  const [strategies, setStrategies] = useState([]);
  const [configs, setConfigs] = useState([]);
  const [urls, setUrls] = useState([]);

  const [showConfigForm, setShowConfigForm] = useState(false);
  const [selectedStrategyId, setSelectedStrategyId] = useState('');
  const [validityDays, setValidityDays] = useState(30);

  const [showStratForm, setShowStratForm] = useState(false);
  const [stratName, setStratName] = useState('');
  const [stratType, setStratType] = useState('BASE62');
  const [stratLength, setStratLength] = useState(8);

  const [urlInput, setUrlInput] = useState('');
  const [selectedConfigId, setSelectedConfigId] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [copied, setCopied] = useState(false);
  const [notification, setNotification] = useState(null);

  const authHeaders = useMemo(() => ({ headers: { 'X-API-Key': apiKey } }), [apiKey]);
  const currentPlan = profile || plans.find((plan) => plan.name === selectedPlan);
  const remainingLinks = profile?.token_limit == null ? null : Math.max(profile.token_limit - profile.urls_created_count, 0);

  useEffect(() => {
    axios.get(`${API_BASE}/merchants/plans`).then((res) => {
      setPlans(res.data);
      if (res.data[0]) {
        setSelectedPlan(res.data[0].name);
        setValidityDays(res.data[0].url_validity_days || 3650);
      }
    }).catch(() => {});
    if (apiKey) validateAndLoadDashboard(apiKey, true);
  }, [apiKey]);

  const showNotification = (msg, type) => {
    setNotification({ msg, type });
    setTimeout(() => setNotification(null), 3000);
  };

  const copyToClipboard = async (text) => {
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
    showNotification('Copied to clipboard', 'success');
  };

  const loadData = async (key) => {
    const headers = { headers: { 'X-API-Key': key } };
    const [profileRes, confRes, stratsRes, urlRes] = await Promise.all([
      axios.get(`${API_BASE}/merchants/me`, headers),
      axios.get(`${API_BASE}/configs`, headers),
      axios.get(`${API_BASE}/strategies`),
      axios.get(`${API_BASE}/urls`, headers),
    ]);
    setProfile(profileRes.data);
    setConfigs(confRes.data);
    setStrategies(stratsRes.data);
    setUrls(urlRes.data);
    if (stratsRes.data.length > 0) setSelectedStrategyId(stratsRes.data[0].strategy_id);
    if (confRes.data.length > 0) setSelectedConfigId(confRes.data[0].config_id);
  };

  const validateAndLoadDashboard = async (key, silent = false) => {
    try {
      setAuthLoading(true);
      setAuthError('');
      await loadData(key);
      setApiKey(key);
      localStorage.setItem('merchantKey', key);
      setIsAuthenticated(true);
    } catch (err) {
      if (err.response?.status === 401 || err.response?.status === 403) {
        handleLogout();
        if (!silent) setAuthError('Invalid or inactive API key.');
      } else if (err.response) {
        if (!silent) setAuthError(err.response.data?.detail || `Server error (${err.response.status}).`);
      } else {
        if (!silent) setAuthError('Network error connecting to the server.');
      }
    } finally {
      setAuthLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    if (!regCode || !regName) return;
    try {
      setAuthLoading(true);
      setAuthError('');
      const res = await axios.post(`${API_BASE}/merchants`, {
        merchant_code: regCode,
        name: regName,
        plan: selectedPlan,
        account_details: `Registered on ${selectedPlan} plan`,
      });
      const newKey = res.data.api_key;
      alert(`Account provisioned successfully. Save this API key now; it will not be shown again:\n\n${newKey}`);
      await validateAndLoadDashboard(newKey);
    } catch (err) {
      setAuthError(err.response?.data?.detail || 'Registration failed');
    } finally {
      setAuthLoading(false);
    }
  };

  const handleLogout = () => {
    setApiKey('');
    setIsAuthenticated(false);
    setProfile(null);
    setConfigs([]);
    setUrls([]);
    setResult(null);
    localStorage.removeItem('merchantKey');
  };

  const handleCreateStrategy = async (e) => {
    e.preventDefault();
    if (!stratName || parseInt(stratLength, 10) < 6) {
      showNotification('Strategy name and length of at least 6 are required.', 'error');
      return;
    }
    try {
      setLoading(true);
      const name = stratName.toUpperCase().includes(stratType)
        ? stratName.toUpperCase()
        : `${stratName.toUpperCase()}_${stratType}`;
      const res = await axios.post(`${API_BASE}/strategies`, {
        name,
        output_length: parseInt(stratLength, 10),
      });
      setStrategies([res.data, ...strategies]);
      setSelectedStrategyId(res.data.strategy_id);
      setShowStratForm(false);
      setStratName('');
      setStratType('BASE62');
      setStratLength(8);
      showNotification('Strategy created.', 'success');
    } catch (err) {
      showNotification(err.response?.data?.detail || 'Failed to create strategy', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateConfig = async () => {
    try {
      setLoading(true);
      const res = await axios.post(`${API_BASE}/configs`, {
        strategy_id: selectedStrategyId,
        valid_until: addDays(validityDays),
        is_active: true,
      }, authHeaders);
      setConfigs([res.data, ...configs]);
      setSelectedConfigId(res.data.config_id);
      setShowConfigForm(false);
      showNotification('Strategy validity created.', 'success');
    } catch (err) {
      showNotification(err.response?.data?.detail || 'Failed to create strategy validity', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteConfig = async (configId) => {
    try {
      setLoading(true);
      await axios.delete(`${API_BASE}/configs/${configId}`, authHeaders);
      setConfigs(configs.filter((config) => config.config_id !== configId));
      if (selectedConfigId === configId) setSelectedConfigId('');
      showNotification('Strategy validity revoked.', 'success');
    } catch (err) {
      showNotification(err.response?.data?.detail || 'Failed to delete validity', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteUrl = async (urlId) => {
    try {
      setLoading(true);
      await axios.delete(`${API_BASE}/urls/${urlId}`, authHeaders);
      setUrls(urls.filter((url) => url.url_id !== urlId));
      await loadData(apiKey);
      showNotification('Short URL deleted.', 'success');
    } catch (err) {
      showNotification(err.response?.data?.detail || 'Failed to delete short URL', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleShorten = async (e) => {
    e.preventDefault();
    if (!urlInput || !selectedConfigId) {
      showNotification('Select a valid strategy and enter a URL.', 'error');
      return;
    }
    try {
      setLoading(true);
      const original_url = /^https?:\/\//i.test(urlInput) ? urlInput : `https://${urlInput}`;
      const res = await axios.post(`${API_BASE}/urls/shorten`, { original_url, config_id: selectedConfigId }, authHeaders);
      setResult(res.data);
      setUrlInput('');
      await loadData(apiKey);
      showNotification('URL shortened.', 'success');
    } catch (err) {
      showNotification(err.response?.data?.detail || 'Failed to shorten URL', 'error');
    } finally {
      setLoading(false);
    }
  };

  const getStrategy = (id) => strategies.find((strategy) => strategy.strategy_id === id);
  const activeConfigs = configs.filter((config) => config.is_active && new Date(config.valid_until) > new Date());

  if (!isAuthenticated) {
    return (
      <div className="auth-shell">
        <div className="card auth-card">
          <div className="brand-row">
            <Shield size={24} />
            <div>
              <h1>Protechy</h1>
              <p>URL shortening with plan limits and link validity.</p>
            </div>
          </div>

          <div className="tabs">
            <button className={`tab ${isLoginView ? 'active' : ''}`} onClick={() => { setAuthError(''); setIsLoginView(true); }}>Login</button>
            <button className={`tab ${!isLoginView ? 'active' : ''}`} onClick={() => { setAuthError(''); setIsLoginView(false); }}>Register</button>
          </div>

          {authError && <div className="alert">{authError}</div>}

          {isLoginView ? (
            <form onSubmit={(e) => { e.preventDefault(); validateAndLoadDashboard(loginKey); }}>
              <div className="input-group">
                <label className="input-label">API Key</label>
                <input type="password" placeholder="sec_..." className="input-field" value={loginKey} onChange={(e) => setLoginKey(e.target.value)} required />
              </div>
              <button type="submit" className="btn btn-primary full-width" disabled={authLoading}>
                {authLoading ? 'Authenticating...' : 'Sign In'}
              </button>
            </form>
          ) : (
            <form onSubmit={handleRegister}>
              <div className="input-group">
                <label className="input-label">Company Name</label>
                <input type="text" placeholder="Acme Corp" className="input-field" value={regName} onChange={(e) => setRegName(e.target.value)} required />
              </div>
              <div className="input-group">
                <label className="input-label">Merchant Code</label>
                <input type="text" placeholder="ACME_001" className="input-field" value={regCode} onChange={(e) => setRegCode(e.target.value)} required />
              </div>
              <div className="input-group">
                <label className="input-label">Select Plan</label>
                <select className="input-field" value={selectedPlan} onChange={(e) => setSelectedPlan(e.target.value)}>
                  {plans.map((plan) => (
                    <option key={plan.name} value={plan.name}>
                      {plan.name} - {tokenLabel(plan.token_limit)}, {daysLabel(plan.url_validity_days)}
                    </option>
                  ))}
                </select>
              </div>
              <button type="submit" className="btn btn-primary full-width" disabled={authLoading}>
                {authLoading ? 'Provisioning...' : 'Create Account'}
              </button>
            </form>
          )}
        </div>
      </div>
    );
  }

  return (
    <>
      <header className="app-header">
        <div className="logo-group">
          <Shield size={28} />
          <div>
            <div className="logo-text">Protechy Dashboard</div>
            <p>{profile?.name} - {profile?.plan} plan</p>
          </div>
        </div>
        <button onClick={handleLogout} className="btn btn-secondary compact-btn">
          <LogOut size={14} /> Sign Out
        </button>
      </header>

      <section className="metric-grid">
        <div className="metric"><span>Plan</span><strong>{profile?.plan}</strong></div>
        <div className="metric"><span>Used</span><strong>{profile?.urls_created_count}</strong></div>
        <div className="metric"><span>Remaining</span><strong>{remainingLinks == null ? 'Unlimited' : remainingLinks}</strong></div>
        <div className="metric"><span>Default Validity</span><strong>{daysLabel(currentPlan?.url_validity_days)}</strong></div>
      </section>

      <div className="dashboard-grid">
        <section className="card">
          <div className="section-head">
            <div>
              <h2><Shield size={20} /> Strategy Validity</h2>
              <p>Create a validity window for each shortening strategy.</p>
            </div>
            <button className="btn btn-secondary compact-btn" onClick={() => setShowConfigForm(!showConfigForm)}>
              <Plus size={16} /> {showConfigForm ? 'Close' : 'New'}
            </button>
          </div>

          {showConfigForm && (
            <div className="form-panel">
              <div className="strategy-grid">
                {strategies.map((strategy) => (
                  <button
                    type="button"
                    key={strategy.strategy_id}
                    className={`strategy-item ${selectedStrategyId === strategy.strategy_id ? 'active' : ''}`}
                    onClick={() => setSelectedStrategyId(strategy.strategy_id)}
                  >
                    <span className="strategy-title">{strategy.name}</span>
                    <span className="strategy-desc">{strategy.output_length} chars</span>
                  </button>
                ))}
              </div>
              <div className="inline-fields">
                <div className="input-group">
                  <label className="input-label">Validity Days</label>
                  <input type="number" min="1" max="3650" className="input-field" value={validityDays} onChange={(e) => setValidityDays(e.target.value)} />
                </div>
                <button className="btn btn-primary" onClick={handleCreateConfig} disabled={loading || !selectedStrategyId}>
                  Save Validity
                </button>
              </div>
              <button type="button" className="link-button" onClick={() => setShowStratForm(!showStratForm)}>
                Add custom strategy
              </button>
              {showStratForm && (
                <form className="inline-fields" onSubmit={handleCreateStrategy}>
                  <input className="input-field" placeholder="Strategy name" value={stratName} onChange={(e) => setStratName(e.target.value)} />
                  <select className="input-field" value={stratType} onChange={(e) => setStratType(e.target.value)}>
                    <option value="BASE62">Base62</option>
                    <option value="SHA256">SHA-256</option>
                    <option value="MD5">MD5</option>
                    <option value="RANDOM">Random</option>
                    <option value="UUIDV4">UUIDv4</option>
                    <option value="BASE64">Base64</option>
                  </select>
                  <input type="number" min="6" className="input-field small-input" value={stratLength} onChange={(e) => setStratLength(e.target.value)} />
                  <button className="btn btn-secondary" disabled={loading}>Add</button>
                </form>
              )}
            </div>
          )}

          <div className="config-list">
            {configs.length === 0 ? <div className="empty-state">No strategy validity windows yet.</div> : configs.map((config) => {
              const strategy = getStrategy(config.strategy_id);
              const isValid = config.is_active && new Date(config.valid_until) > new Date();
              return (
                <div key={config.config_id} className="config-item">
                  <div>
                    <div className="item-title">{strategy?.name || 'Unknown strategy'}</div>
                    <div className="item-meta">{strategy?.output_length || 0} chars - valid until {formatDate(config.valid_until)}</div>
                  </div>
                  <div className="row-actions">
                    <span className={`badge ${isValid ? 'active' : ''}`}>{isValid ? 'Valid' : 'Expired'}</span>
                    <button onClick={() => handleDeleteConfig(config.config_id)} className="danger-button" disabled={loading}>Revoke</button>
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        <section className="card">
          <h2><Zap size={20} /> Generate Link</h2>
          <form onSubmit={handleShorten}>
            <div className="input-group">
              <label className="input-label">Strategy Validity</label>
              <select className="input-field" value={selectedConfigId} onChange={(e) => setSelectedConfigId(e.target.value)} required>
                <option value="" disabled>Choose a valid strategy</option>
                {activeConfigs.map((config) => {
                  const strategy = getStrategy(config.strategy_id);
                  return (
                    <option key={config.config_id} value={config.config_id}>
                      {strategy?.name || 'Strategy'} - expires {formatDate(config.valid_until)}
                    </option>
                  );
                })}
              </select>
            </div>
            <div className="input-group">
              <label className="input-label">Destination URL</label>
              <input type="text" className="input-field" placeholder="https://example.com/long/path" value={urlInput} onChange={(e) => setUrlInput(e.target.value)} required />
            </div>
            <button type="submit" className="btn btn-primary" disabled={loading || activeConfigs.length === 0 || remainingLinks === 0}>
              <Link2 size={16} /> {loading ? 'Shortening...' : 'Shorten URL'}
            </button>
          </form>

          {result && (
            <div className="result-box">
              <div>
                <div className="eyebrow">Short URL</div>
                <div className="short-url-display">{result.short_url}</div>
                <p>Valid until {formatDate(result.valid_until)}</p>
              </div>
              <div className="button-row">
                <button className="btn btn-secondary compact-btn" onClick={() => copyToClipboard(result.short_url)}>
                  {copied ? <CheckCircle2 size={16} /> : <Copy size={16} />} {copied ? 'Copied' : 'Copy'}
                </button>
                <a href={result.short_url} target="_blank" rel="noreferrer" className="btn btn-primary compact-btn">
                  Open <ExternalLink size={16} />
                </a>
              </div>
            </div>
          )}
        </section>
      </div>

      <section className="card">
        <div className="section-head">
          <div>
            <h2><Link2 size={20} /> URL Inventory</h2>
            <p>See each destination, short domain, and whether it is still valid.</p>
          </div>
        </div>
        <div className="url-table">
          {urls.length === 0 ? <div className="empty-state">No URLs created yet.</div> : urls.map((url) => (
            <div key={url.url_id} className="url-row">
              <div>
                <a href={url.short_url} target="_blank" rel="noreferrer" className="item-title">{url.short_url}</a>
                <div className="item-meta">{url.original_url}</div>
              </div>
              <div className="url-status">
                <span className={`badge ${url.is_valid ? 'active' : ''}`}>{url.status}</span>
                <span>{formatDate(url.valid_until)}</span>
                <button className="icon-danger-button" onClick={() => handleDeleteUrl(url.url_id)} disabled={loading} title="Delete short URL">
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>

      {notification && (
        <div className={`notification ${notification.type}`}>
          {notification.type === 'success' ? <CheckCircle2 size={18} /> : <AlertCircle size={18} />}
          {notification.msg}
        </div>
      )}
    </>
  );
}

export default App;
