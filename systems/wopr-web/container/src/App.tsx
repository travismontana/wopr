import { Routes, Route, Link } from 'react-router-dom';

const Page = ({ title }: { title: string }) => (
  <div style={{ padding: 24 }}>
    <h1>{title}</h1>
  </div>
);

export default function App() {
  return (
    <div>
      <nav style={{ padding: 12, borderBottom: '1px solid #333' }}>
        <Link to="/">Dashboard</Link> |{" "}
        <Link to="/games">Games</Link> |{" "}
        <Link to="/images">Images</Link> |{" "}
        <Link to="/ml">ML</Link>
      </nav>

      <Routes>
        <Route path="/" element={<Page title="Dashboard" />} />
        <Route path="/games" element={<Page title="Games" />} />
        <Route path="/images" element={<Page title="Images" />} />

        <Route path="/ml" element={<Page title="ML Home" />} />
        <Route path="/ml/pieces" element={<Page title="Piece Library" />} />
        <Route path="/ml/label" element={<Page title="Label Workbench" />} />
        <Route path="/ml/datasets" element={<Page title="Datasets" />} />
        <Route path="/ml/train" element={<Page title="Training Jobs" />} />
      </Routes>
    </div>
  );
}
