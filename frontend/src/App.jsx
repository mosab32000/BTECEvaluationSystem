import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Login from './components/Login';
import Register from './components/Register';
import EvaluationForm from './components/EvaluationForm';
import AuditLog from './components/AuditLog';
import { Container, Navbar, Nav } from 'react-bootstrap';

function Header() {
  const { isAuthenticated, logout } = React.useContext(AuthContext);
  
  return (
    <Navbar bg="dark" variant="dark" expand="lg" className="mb-4">
      <Container>
        <Navbar.Brand href="/">BTEC Evaluation System</Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="ms-auto">
            {isAuthenticated ? (
              <>
                <Nav.Link href="/evaluate">New Evaluation</Nav.Link>
                <Nav.Link href="/evaluations">My Evaluations</Nav.Link>
                <Nav.Link onClick={logout}>Logout</Nav.Link>
              </>
            ) : (
              <>
                <Nav.Link href="/login">Login</Nav.Link>
                <Nav.Link href="/register">Register</Nav.Link>
              </>
            )}
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <Header />
        <Container>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route 
              path="/evaluate" 
              element={
                <ProtectedRoute>
                  <EvaluationForm />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/evaluations" 
              element={
                <ProtectedRoute>
                  <AuditLog />
                </ProtectedRoute>
              } 
            />
            <Route path="/" element={<Navigate to="/evaluate" />} />
          </Routes>
        </Container>
      </Router>
    </AuthProvider>
  );
}

export default App;
