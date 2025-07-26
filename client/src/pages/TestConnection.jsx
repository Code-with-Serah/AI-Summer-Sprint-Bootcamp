import React, { useState } from 'react';

const TestConnection = () => {
  const [movie, setMovie] = useState('');
  const [results, setResults] = useState([]);
  const [error, setError] = useState('');

  const handleFetch = async () => {
    try {
      setError('');
      const res = await fetch(`http://localhost:5000/recommend?movie=${encodeURIComponent(movie)}`);
      if (!res.ok) throw new Error('Request failed');
      const data = await res.json();
      setResults(data);
    } catch (err) {
      setError('Failed to fetch recommendations.');
      setResults([]);
    }
  };

  return (
    <div style={{ padding: '2rem', fontFamily: 'Arial' }}>
      <h2>Test Backend Connection</h2>
      <input
        type="text"
        placeholder="Enter movie name"
        value={movie}
        onChange={(e) => setMovie(e.target.value)}
        style={{ padding: '0.5rem', width: '300px' }}
      />
      <button onClick={handleFetch} style={{ marginLeft: '1rem', padding: '0.5rem' }}>
        Fetch Recommendations
      </button>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      <ul>
        {results.map((movie, i) => (
          <li key={i}>{movie.Name} - {movie.Genre} ({movie.Score})</li>
        ))}
      </ul>
    </div>
  );
};

export default TestConnection;
