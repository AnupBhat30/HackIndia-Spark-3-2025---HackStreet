import { useEffect, useState } from 'react';
import { Brain, LineChart, Lock, CircleDot } from 'lucide-react';
import { Link } from 'react-router-dom';

function Home() {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  type Position =
    | 'absolute'
    | 'relative'
    | 'fixed'
    | 'static'
    | 'sticky'
    | 'inherit'
    | 'initial'
    | 'unset';

  const floatingCircleStyle = (i: number) => ({
    position: 'absolute' as Position,
    left: `${Math.random() * 100}%`,
    top: `${Math.random() * 100}%`,
    animation: `float-${i % 5} ${Math.random() * 5 + 5}s ease-in-out infinite`,
  });

  const blobStyle = (
    top: string,
    left: string,
    color: string,
    delay = '0s'
  ) => ({
    position: 'absolute' as Position,
    top,
    left,
    width: '24rem',
    height: '24rem',
    backgroundColor: color,
    borderRadius: '50%',
    filter: 'blur(100px)',
    animation: 'pulse 0.5s ease-in-out infinite',
    animationDelay: delay,
  });

  const featureCardStyle = (index: number) => ({
    backgroundColor: '#ffffff',
    padding: '1.5rem',
    borderRadius: '1rem',
    transform: isVisible ? 'translateY(0)' : 'translateY(40px)',
    opacity: isVisible ? 1 : 0,
    transition: `all 0.5s ease ${index * 0.2}s`,
    boxShadow: isVisible ? '0 4px 20px rgba(0,0,0,0.05)' : 'none',
    cursor: 'pointer',
  });

  return (
    <div
      style={{
        minHeight: '100vh',
        background: 'linear-gradient(to bottom, #4B0082, #EE82EE)',
        color: 'white',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Inline CSS keyframes */}
      <style>
        {`
        @keyframes float-0 {
          0% { transform: translateY(0px); }
          50% { transform: translateY(-20px); }
          100% { transform: translateY(0px); }
        }
        @keyframes float-1 {
          0% { transform: translateY(0px); }
          50% { transform: translateY(-30px); }
          100% { transform: translateY(0px); }
        }
        @keyframes float-2 {
          0% { transform: translateY(0px); }
          50% { transform: translateY(-15px); }
          100% { transform: translateY(0px); }
        }
        @keyframes float-3 {
          0% { transform: translateY(0px); }
          50% { transform: translateY(-25px); }
          100% { transform: translateY(0px); }
        }
        @keyframes float-4 {
          0% { transform: translateY(0px); }
          50% { transform: translateY(-35px); }
          100% { transform: translateY(0px); }
        }
        @keyframes pulse {
          0%, 100% { transform: scale(1); opacity: 0.6; }
          50% { transform: scale(1.1); opacity: 0.8; }
        }
        .get-started-btn, .calculate-repayment-btn {
          display: inline-flex;
          align-items: center;
          margin: 70px 10px;
          background-color: #300654;
          color: white;
          padding: 1rem 2rem;
          border-radius: 0.5rem;
          font-size: 1.125rem;
          font-weight: 600;
          text-decoration: none;
          transition: transform 0.3s, background-color 0.3s;
        }
        .get-started-btn:hover, .calculate-repayment-btn:hover {
          background-color: #51217a;
          transform: scale(1.25);
        }
        `}
      </style>

      {/* Background Circles + Blobs */}
      <div
        style={{
          position: 'absolute',
          inset: 0,
          pointerEvents: 'none',
          overflow: 'hidden',
        }}
      >
        {[...Array(20)].map((_, i) => (
          <div key={i} style={floatingCircleStyle(i)}>
            <CircleDot
              style={{
                width: `${Math.random() * 40 + 20}px`,
                height: `${Math.random() * 40 + 20}px`,
                color: 'rgba(255, 255, 255, 0.4)',
              }}
            />
          </div>
        ))}
        <div
          style={blobStyle('25%', '20%', 'rgba(209, 250, 229, 0.3)')}
        />
        <div
          style={blobStyle('70%', '70%', 'rgba(236, 253, 245, 0.4)', '2s')}
        />
      </div>

      {/* Navbar */}
      <nav
        style={{
          position: 'fixed',
          top: 0,
          width: '100%',
          backgroundColor: 'transparent',
          zIndex: 50,
        }}
      >
        <div
          style={{
            maxWidth: '1200px',
            margin: '0 auto',
            padding: '1rem 1.5rem',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Brain style={{ width: 32, height: 32, color: 'white' }} />
            <span style={{ fontSize: '1.25rem', fontWeight: 'bold' }}>
              FinAI
            </span>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div
        style={{
          paddingTop: '8rem',
          paddingBottom: '6rem',
          paddingLeft: '1rem',
          paddingRight: '1rem',
          textAlign: 'center',
        }}
      >
        <div
          style={{
            transform: isVisible ? 'translateY(0)' : 'translateY(40px)',
            opacity: isVisible ? 1 : 0,
            transition: 'all 1s ease',
          }}
        >
          <h1
            style={{
              fontSize: '3rem',
              fontWeight: 'bold',
              marginBottom: '1.5rem',
              color: 'white',
            }}
          >
            Get Smart Financial Advice, Powered by AI + Knowledge Graphs
          </h1>
          <p
            style={{
              fontSize: '1.25rem',
              color: 'white',
              maxWidth: '700px',
              margin: '0 auto 3rem',
            }}
          >
            Make informed financial decisions with our AI-powered platform that
            combines cutting-edge technology with comprehensive financial
            knowledge.
          </p>
          <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem' }}>
            <Link
              to="/chat"
              className="get-started-btn"
            >
              <Brain
                style={{ width: '24px', height: '24px', marginRight: '0.5rem' }}
              />
              Chat Now
            </Link>
            <Link
              to="/calc"
              className="calculate-repayment-btn"
            >
              Calculate Repayment
            </Link>
          </div>
        </div>

        {/* Feature Cards */}
        <div
          style={{
            maxWidth: '1200px',
            margin: '0 auto',
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '2rem',
          }}
        >
          {[
            {
              icon: (
                <Brain
                  style={{ width: '32px', height: '32px', color: 'black' }}
                />
              ),
              title: 'AI-Powered Insights',
              description:
                'Advanced algorithms provide personalized financial recommendations',
            },
            {
              icon: (
                <LineChart
                  style={{ width: '32px', height: '32px', color: 'black' }}
                />
              ),
              title: 'Real-time Analysis',
              description:
                'Up-to-date market data and trend analysis at your fingertips',
            },
            {
              icon: (
                <Lock
                  style={{ width: '32px', height: '32px', color: 'black' }}
                />
              ),
              title: 'Secure & Private',
              description:
                'Your financial data is protected with enterprise-grade security',
            },
          ].map((feature, index) => (
            <div
              key={index}
              style={featureCardStyle(index)}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'scale(1.05)';
                e.currentTarget.style.boxShadow =
                  '0 4px 20px rgba(0,0,0,0.1)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'scale(1)';
                e.currentTarget.style.boxShadow =
                  '0 4px 20px rgba(0,0,0,0.05)';
              }}
            >
              <div style={{ marginBottom: '1rem' }}>{feature.icon}</div>
              <h3
                style={{
                  fontSize: '1.25rem',
                  fontWeight: 600,
                  marginBottom: '0.5rem',
                  color: 'black',
                }}
              >
                {feature.title}
              </h3>
              <p style={{ color: 'black' }}>{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Home;