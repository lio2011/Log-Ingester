import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';  // Import the updated CSS file

const BASE_URL = "http://localhost:3000";

function App() {
  const [logs, setLogs] = useState([]);
  const [message, setMessage] = useState('');
  const [level, setLevel] = useState('');
  const [traceId, setTraceId] = useState('');
  const [spanId, setSpanId] = useState('');
  const [size, setSize] = useState(10);
  const [timeFrame, setTimeFrame] = useState('24h');  // New state for time frame
  const [error, setError] = useState('');  // Error state to handle validation message
  const [additionalFields, setAdditionalFields] = useState([]);  // New state for additional dynamic fields

  useEffect(() => {
    fetchLogs();
  }, []);

  const fetchLogs = async () => {
    try {
      const response = await axios.get(`${BASE_URL}/logs`, {
        params: { size },
        headers: {
          "Authorization": "ApiKey bjJwQlA1UUJCbkdpMTg3VVFrOTk6aF85RG1EUDRSY0tNWE5wak9tVm9KQQ==" // Add your actual API key here
        }
      });
      setLogs(response.data.Response);
    } catch (error) {
      console.error("Error fetching logs", error);
    }
  };

  const addAdditionalField = () => {
    setAdditionalFields([...additionalFields, { key: '', value: '' }]); // Add a new empty field to the array
  };

  const handleFieldChange = (index, event) => {
    const values = [...additionalFields];
    values[index][event.target.name] = event.target.value; // Update the specific field
    setAdditionalFields(values);
  };

  const removeField = (index) => {
    const values = [...additionalFields];
    values.splice(index, 1); // Remove the field at the given index
    setAdditionalFields(values);
  };

  const searchLogs = async () => {
    // Check if all fields are empty except for time_frame
    if (!message && !level && !traceId && !spanId && !timeFrame && additionalFields.length === 0) {
      setError('Please fill in at least one field before searching.');  // Set error message
      return;  // Stop the function execution
    }

    setError('');  // Clear error message if validation passes

    const additionalParams = additionalFields.reduce((acc, field) => {
      if (field.key && field.value) {
        acc[field.key] = field.value; // Add custom fields to query params
      }
      return acc;
    }, {});

    try {
      const response = await axios.get(`${BASE_URL}/search`, {
        params: {
          message,
          level,
          trace_id: traceId,
          span_id: spanId,
          size,
          time_frame: timeFrame,
          ...additionalParams,  // Include additional fields in query params
        },
        headers: {
          "Authorization": "ApiKey bjJwQlA1UUJCbkdpMTg3VVFrOTk6aF85RG1EUDRSY0tNWE5wak9tVm9KQQ==" // Add your actual API key here
        }
      });
      setLogs(response.data.Response);
    } catch (error) {
      console.error("Error searching logs", error);
    }
  };

  return (
    <div className="App">
      <h1>Log Viewer</h1>

      {/* Display error message if all fields are empty */}
      {error && <div className="error-message">{error}</div>}

      {/* Search logs */}
      <section>
        <h2>Search Logs</h2>
        <div className="form-group">
          <label htmlFor="message">Message :</label>
          <input
            id="message"
            type="text"
            placeholder="Message"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
          />
        </div>
        <div className="form-group">
          <label htmlFor="level">Level :</label>
          <input
            id="level"
            type="text"
            placeholder="Level"
            value={level}
            onChange={(e) => setLevel(e.target.value)}
          />
        </div>
        <div className="form-group">
          <label htmlFor="traceId">Trace ID :</label>
          <input
            id="traceId"
            type="text"
            placeholder="Trace ID"
            value={traceId}
            onChange={(e) => setTraceId(e.target.value)}
          />
        </div>
        <div className="form-group">
          <label htmlFor="spanId">Span ID :</label>
          <input
            id="spanId"
            type="text"
            placeholder="Span ID"
            value={spanId}
            onChange={(e) => setSpanId(e.target.value)}
          />
        </div>
        <div className="form-group">
          <label htmlFor="timeFrame">Time Frame :</label>
          <input
            id="timeFrame"
            type="text"
            placeholder="e.g., 1h, 5m"
            value={timeFrame}
            onChange={(e) => setTimeFrame(e.target.value)}
          />
          <pre> e.g., 4d, 1h, 5m</pre>
        </div>

        {/* Dynamic Additional Fields */}
        {additionalFields.map((field, index) => (
          <div className="form-group" key={index}>
            <label htmlFor={`additionalFieldKey${index}`}>Key:</label>
            <input
              id={`additionalFieldKey${index}`}
              type="text"
              name="key"
              placeholder="Field Key"
              value={field.key}
              onChange={(e) => handleFieldChange(index, e)}
            />
            <label htmlFor={`additionalFieldValue${index}`}>Value:</label>
            <input
              id={`additionalFieldValue${index}`}
              type="text"
              name="value"
              placeholder="Field Value"
              value={field.value}
              onChange={(e) => handleFieldChange(index, e)}
            />
            
            {/* Remove Button */}
            <button
              type="button"
              className="remove"
              onClick={() => removeField(index)}
            >
              Remove
            </button>
          </div>
        ))}

        {/* Add Custom Field Button */}
        <span>
  <div className="button-container">
    <button type="button" className="add" onClick={addAdditionalField}>
      Add Custom Field
    </button>
    <button type="button" className="search" onClick={searchLogs}>
      Search Logs
    </button>
  </div>
</span>
      </section>

      {/* Display Logs */}
      <section>
        <h2>Logs</h2>
        <ul>
          {logs.map((log, index) => (
            <li key={index}>
              <strong>{log._source.timestamp}</strong> - Level : {log._source.level} - Message : {log._source.message} - Trace ID : {log._source.traceId} - Span ID : {log._source.spanId}
              <hr className='horizontal-rule'></hr>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}

export default App;
