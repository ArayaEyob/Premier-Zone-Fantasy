import './App.css';
import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout/layout';
import Home from './components/Home/home';
import StatsDashboard from './components/StatsDashboard/StatsDashboard';
import Teams from './components/Teams/teams';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="stats" element={<StatsDashboard />} />
        <Route path="teams" element={<Teams />} />
      </Route>
    </Routes>
  );
}

export default App;
