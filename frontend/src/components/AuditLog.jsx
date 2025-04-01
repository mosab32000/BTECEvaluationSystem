import React, { useState, useEffect } from 'react';
import { Card, ListGroup, Alert, Spinner, Badge } from 'react-bootstrap';
import api from '../services/api';

const AuditLog = () => {
  const [evaluations, setEvaluations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  useEffect(() => {
    const fetchEvaluations = async () => {
      try {
        const response = await api.getEvaluations();
        setEvaluations(response.data);
      } catch (err) {
        setError('Failed to load evaluations. Please try again later.');
        console.error('Error fetching evaluations:', err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchEvaluations();
  }, []);

  // Helper function to format date
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-GB', {
      dateStyle: 'medium',
      timeStyle: 'short'
    }).format(date);
  };

  // Helper function to get appropriate badge for grade
  const getGradeBadge = (grade) => {
    if (!grade) return null;
    
    const lowerGrade = grade.toLowerCase();
    if (lowerGrade.includes('distinction')) {
      return <Badge bg="success">Distinction</Badge>;
    } else if (lowerGrade.includes('merit')) {
      return <Badge bg="info">Merit</Badge>;
    } else if (lowerGrade.includes('pass')) {
      return <Badge bg="warning">Pass</Badge>;
    } else if (lowerGrade.includes('fail')) {
      return <Badge bg="danger">Fail</Badge>;
    }
    return null;
  };

  if (loading) {
    return (
      <div className="text-center my-5">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
        <p className="mt-2">Loading your evaluations...</p>
      </div>
    );
  }

  if (error) {
    return <Alert variant="danger">{error}</Alert>;
  }

  if (evaluations.length === 0) {
    return (
      <Alert variant="info">
        You haven't submitted any tasks for evaluation yet.
      </Alert>
    );
  }

  return (
    <div>
      <h2 className="mb-4">Your Evaluation History</h2>
      
      {evaluations.map((evaluation) => (
        <Card key={evaluation.id} className="mb-4 evaluation-card">
          <Card.Header className="d-flex justify-content-between align-items-center">
            <div>
              <h5 className="mb-0">Evaluation #{evaluation.id}</h5>
              <div className="evaluation-timestamp">
                {formatDate(evaluation.submitted_at)}
              </div>
            </div>
            <div>
              {getGradeBadge(evaluation.grade)}
            </div>
          </Card.Header>
          
          <Card.Body>
            <Card.Title>Task Submission</Card.Title>
            <Card.Text style={{ whiteSpace: 'pre-wrap' }}>
              {evaluation.task}
            </Card.Text>
            
            <hr />
            
            <Card.Title>AI Evaluation</Card.Title>
            <Card.Text style={{ whiteSpace: 'pre-wrap' }}>
              {evaluation.grade}
            </Card.Text>
          </Card.Body>
          
          <Card.Footer>
            <small className="text-muted">Blockchain Verification Hash:</small>
            <div className="audit-hash">{evaluation.audit_hash}</div>
          </Card.Footer>
        </Card>
      ))}
    </div>
  );
};

export default AuditLog;
