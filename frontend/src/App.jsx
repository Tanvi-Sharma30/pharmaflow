
import './App.css'

function App() {
  return (
    <div className="app">
      {/* Navbar */}
      <header className="navbar">
        <div className="logo">
          <span className="logo-icon">+</span>
          <span>Pharma<span className="green">Flow</span></span>
        </div>

        <nav>
          <a href="#features">Features</a>
          <a href="#how-it-works">How it works</a>
          <a href="#about">About</a>
        </nav>

        <div className="nav-actions">
          <button className="login-btn">Log in</button>
          <button className="primary-btn">Get started</button>
        </div>
      </header>

      {/* Hero Section */}
      <main className="hero-section">
        <div className="hero-content">
          <div className="eyebrow">
            <span className="dot"></span>
            SMART PHARMACY INVENTORY
          </div>

          <h1>
            Your pharmacy,
            <br />
            <span>always in control.</span>
          </h1>

          <p className="hero-description">
            Manage medicine batches, track sellable stock, and dispense
            medicines by earliest expiry. PharmaFlow helps pharmacies stay
            organized and prevent expired stock from going out.
          </p>

          <div className="hero-buttons">
            <button className="primary-btn large">
              Get started <span>→</span>
            </button>

            <button className="secondary-btn large">
              See how it works <span>↗</span>
            </button>
          </div>

          <div className="trust-text">
            <span>✓</span> Built for smarter pharmacy operations
          </div>
        </div>

        {/* Dashboard Preview */}
        <div className="dashboard-wrapper">
          <div className="dashboard">
            <div className="dashboard-top">
              <div className="window-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <span>PharmaFlow dashboard</span>
              <span>•••</span>
            </div>

            <div className="dashboard-body">
              <aside className="sidebar">
                <div className="side-logo">+</div>
                <div className="side-item active">▦</div>
                <div className="side-item">▤</div>
                <div className="side-item">⚑</div>
                <div className="side-item">⚙</div>
              </aside>

              <div className="dashboard-content">
                <div className="dashboard-heading">
                  <div>
                    <small>Overview</small>
                    <h3>Good morning, Pharmacist</h3>
                  </div>
                  <div className="avatar">T</div>
                </div>

                <div className="stats">
                  <div className="stat-card">
                    <small>Total medicines</small>
                    <strong>128</strong>
                    <span>↗ Active medicines</span>
                  </div>

                  <div className="stat-card">
                    <small>Sellable stock</small>
                    <strong>2,450</strong>
                    <span>✓ In-date units</span>
                  </div>
                </div>

                <div className="inventory-card">
                  <div className="inventory-heading">
                    <strong>Medicine inventory</strong>
                    <span>View all →</span>
                  </div>

                  <div className="table-header">
                    <span>Medicine</span>
                    <span>Stock</span>
                    <span>Status</span>
                  </div>

                  <div className="medicine-row">
                    <span><i className="medicine-icon blue"></i>Paracetamol</span>
                    <span>240</span>
                    <b>In date</b>
                  </div>

                  <div className="medicine-row">
                    <span><i className="medicine-icon purple"></i>Amoxicillin</span>
                    <span>180</span>
                    <b>In date</b>
                  </div>

                  <div className="medicine-row">
                    <span><i className="medicine-icon yellow"></i>Cetirizine</span>
                    <span>75</span>
                    <b className="warning">Expiring soon</b>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="expiry-alert">
            <div className="alert-icon">!</div>
            <div>
              <strong>Expiry alert</strong>
              <small>Batch PCM001 expires soon</small>
            </div>
          </div>
        </div>
      </main>

      {/* Features */}
      <section id="features" className="features-section">
        <p className="eyebrow">WHY PHARMAFLOW</p>
        <h2>Everything your pharmacy needs.</h2>

        <div className="feature-grid">
          <div className="feature-card">
            <span>📦</span>
            <h3>Smart inventory</h3>
            <p>Track medicines and batches in one organized place.</p>
          </div>

          <div className="feature-card">
            <span>⏳</span>
            <h3>FEFO dispensing</h3>
            <p>Dispense the earliest-expiring stock first.</p>
          </div>

          <div className="feature-card">
            <span>🔔</span>
            <h3>Expiry alerts</h3>
            <p>Stay informed about medicines nearing expiry.</p>
          </div>
        </div>
      </section>
    </div>
  )
}

export default App