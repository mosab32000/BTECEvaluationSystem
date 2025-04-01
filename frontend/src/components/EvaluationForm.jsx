import React, { useState } from 'react';
import { Card, Form, Button, Alert, Spinner } from 'react-bootstrap';
import api from '../services/api';

const EvaluationForm = () => {
  const [task, setTask] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!task.trim()) {
      setError('Please enter your BTEC task submission');
      return;
    }
    
    setLoading(true);
    setError('');
    setResult(null);
    
    try {
      const response = await api.evaluateTask(task);
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.message || 'Evaluation failed. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  // Helper function to extract and highlight the grade
  const formatGrade = (gradeText) => {
    if (!gradeText) return null;
    
    const gradeMapping = {
      'distinction': 'grade-distinction',
      'merit': 'grade-merit',
      'pass': 'grade-pass',
      'fail': 'grade-fail'
    };
    
    // Check for any of the grade words in the text
    for (const [grade, className] of Object.entries(gradeMapping)) {
      if (gradeText.toLowerCase().includes(grade)) {
        return (
          <div className="mb-3">
            <strong>Grade: </strong>
            <span className={className}>{grade.toUpperCase()}</span>
          </div>
        );
      }
    }
    
    return null;
  };

  return (
    <div className="form-container my-4">
      <h2 className="text-center mb-4">BTEC Task Evaluation</h2>
      
      <Card className="mb-4">
        <Card.Body>
          <Form onSubmit={handleSubmit}>
            <Form.Group className="mb-3" controlId="taskSubmission">
              <Form.Label>Task Submission</Form.Label>
              <Form.Control 
                as="textarea" 
                rows={10} 
                value={task}
                onChange={(e) => setTask(e.target.value)}
                placeholder="Enter your BTEC task submission here..."
                required
              />
            </Form.Group>
            
            {error && <Alert variant="danger">{error}</Alert>}
            
            <div className="d-grid">
              <Button 
                variant="primary" 
                type="submit" 
                disabled={loading}
                size="lg"
              >
                {loading ? (
                  <>
                    <Spinner
                      as="span"
                      animation="border"
                      size="sm"
                      role="status"
                      aria-hidden="true"
                    />
                    {' '}Evaluating...
                  </>
                ) : (
                  'Submit for Evaluation'
                )}
              </Button>
            </div>
          </Form>
        </Card.Body>
      </Card>
      
      {result && (
        <Card className="evaluation-card">
          <Card.Header>
            <h5>Evaluation Results</h5>
          </Card.Header>
          <Card.Body>
            {formatGrade(result.grade)}
            
            <div className="mb-3">
              <div>
                <pre style={{ whiteSpace: 'pre-wrap', fontSize: '1rem' }}>
                  {result.grade}
                </pre>
              </div>
            </div>
            
            <hr />
            
            <div className="mt-3">
              <strong>Verification Hash:</strong>
              <div className="audit-hash">{result.audit_hash}</div>
              <small className="text-muted">
                This hash verifies the integrity of this evaluation on the blockchain.
              </small>
            </div>
          </Card.Body>
        </Card>
      )}
    </div>
  );
};

export default EvaluationForm;
