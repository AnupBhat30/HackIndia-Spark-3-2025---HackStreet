import React, { useState } from 'react';

const CalculatorPage: React.FC = () => {
  const [income, setIncome] = useState('');
  const [expenses, setExpenses] = useState('');
  const [interestRate, setInterestRate] = useState('');
  const [tenure, setTenure] = useState('');
  const [result, setResult] = useState<{ maxEMI: string; loanAmount: string } | null>(null);

  const calculateLoan = () => {
    const monthlyIncome = parseFloat(income);
    const monthlyExpenses = parseFloat(expenses);
    const annualRate = parseFloat(interestRate);
    const loanTenureYears = parseFloat(tenure);

    if (
      isNaN(monthlyIncome) ||
      isNaN(monthlyExpenses) ||
      isNaN(annualRate) ||
      isNaN(loanTenureYears)
    ) {
      alert('Please enter all values correctly.');
      return;
    }

    const maxEMI = (monthlyIncome - monthlyExpenses) * 0.4;
    const R = annualRate / 12 / 100;
    const N = loanTenureYears * 12;

    const numerator = Math.pow(1 + R, N) - 1;
    const denominator = R * Math.pow(1 + R, N);
    const loanAmount = maxEMI * (numerator / denominator);

    setResult({
      maxEMI: maxEMI.toFixed(2),
      loanAmount: loanAmount.toFixed(2),
    });
  };

  // Generate floating dollar signs
  const dollarSigns = Array.from({ length: 30 }).map((_, index) => {
    const left = Math.random() * 100;
    const size = Math.random() * 30 + 10;
    const duration = Math.random() * 10 + 5;
    const delay = Math.random() * 5;
    const opacity = Math.random() * 0.5 + 0.3;

    return (
      <span
        key={index}
        style={{
          position: 'absolute',
          top: '-5%',
          left: `${left}%`,
          fontSize: `${size}px`,
          animation: `floatUp ${duration}s linear infinite`,
          animationDelay: `${delay}s`,
          color: '#ffffff77',
          userSelect: 'none',
          opacity,
        }}
      >
        $
      </span>
    );
  });

  return (
    <div
      style={{
        position: 'relative',
        background: 'linear-gradient(to bottom, #300654, #EE82EE)',
        color: 'white',
        width: '200vh',
        minHeight: '100vh',
        padding: '2rem',
        fontFamily: 'Arial, sans-serif',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        overflow: 'hidden',
      }}
    >
      {/* Back to Home Button */}
      <a
        href="/"
        style={{
          position: 'absolute',
          top: '1.5rem',
          left: '2rem',
          zIndex: 2,
          color: 'white',
          textDecoration: 'none',
          backgroundColor: '#56038a',
          padding: '0.5rem 1rem',
          borderRadius: '8px',
          fontWeight: 'bold',
          fontSize: '0.95rem',
          boxShadow: '0 4px 10px rgba(0,0,0,0.2)',
          transition: 'background 0.3s ease-in-out',
        }}
        onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = '#7e02cc')}
        onMouseLeave={(e) => (e.currentTarget.style.backgroundColor = '#56038a')}
      >
        ← Back to Home
      </a>

      {/* Floating dollar signs */}
      <div style={{ position: 'absolute', width: '100%', height: '100%', zIndex: 0 }}>
        {dollarSigns}
      </div>

      {/* Calculator Content */}
      <div
        style={{
          backgroundColor: 'rgba(72, 3, 115,0.1)',
          padding: '2.5rem',
          borderRadius: '15px',
          maxWidth: '500px',
          width: '100%',
          boxShadow: '0 12px 20px rgba(0,0,0,0.1)',
          zIndex: 1,
        }}
      >
        <h1 style={{ textAlign: 'center', marginBottom: '2rem' }}>
          Loan Affordability Calculator
        </h1>

        {/* Income Input */}
        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem' }}>
            Monthly Income (₹):
          </label>
          <input
            type="number"
            value={income}
            onChange={(e) => setIncome(e.target.value)}
            placeholder="e.g. 60000"
            style={inputStyle}
          />
        </div>

        {/* Expenses Input */}
        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem' }}>
            Monthly Expenses / EMIs (₹):
          </label>
          <input
            type="number"
            value={expenses}
            onChange={(e) => setExpenses(e.target.value)}
            placeholder="e.g. 20000"
            style={inputStyle}
          />
        </div>

        {/* Interest Rate Input */}
        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem' }}>
            Interest Rate (% per year):
          </label>
          <input
            type="number"
            value={interestRate}
            onChange={(e) => setInterestRate(e.target.value)}
            placeholder="e.g. 10"
            style={inputStyle}
          />
        </div>

        {/* Tenure Input */}
        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem' }}>
            Tenure (years):
          </label>
          <input
            type="number"
            value={tenure}
            onChange={(e) => setTenure(e.target.value)}
            placeholder="e.g. 10"
            style={inputStyle}
          />
        </div>

        {/* Calculate Button */}
        <button
          onClick={calculateLoan}
          style={{
            width: '100%',
            backgroundColor: 'white',
            color: '#300654',
            padding: '0.9rem',
            fontWeight: 'bold',
            fontSize: '1rem',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            transition: 'all 0.3s ease-in-out',
          }}
        >
          Calculate
        </button>

        {/* Results */}
        {result && (
          <div
            style={{
              marginTop: '2rem',
              padding: '1rem',
              background: 'linear-gradient(to bottom, #56038a, #7e02cc)',
              borderRadius: '8px',
              textAlign: 'left',
            }}
          >
            <h3 style={{ marginBottom: '1rem' }}>📊 Results</h3>
            <p>
              <strong>Max EMI:</strong> ₹{result.maxEMI}/month
            </p>
            <p>
              <strong>Loan You Can Afford:</strong> ₹{result.loanAmount}
            </p>
            <p style={{ marginTop: '1rem', fontSize: '0.95rem', opacity: 0.9 }}>
              ✅ Based on your income and expenses, you can afford a monthly EMI of ₹
              {result.maxEMI}.
              <br />
              With {interestRate}% interest over {tenure} years, you may be eligible
              for a loan of around ₹{result.loanAmount}.
            </p>
          </div>
        )}
      </div>

      {/* Floating animation style */}
      <style>{`
        @keyframes floatUp {
          0% {
            transform: translateY(100vh) scale(1);
          }
          100% {
            transform: translateY(-10vh) scale(1.5);
          }
        }
      `}</style>
    </div>
  );
};

const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: '0.8rem',
  borderRadius: '8px',
  border: '1px solid #fff',
  background: 'rgba(255,255,255,0.1)',
  color: 'white',
  fontSize: '1rem',
  outline: 'none',
};

export default CalculatorPage;
