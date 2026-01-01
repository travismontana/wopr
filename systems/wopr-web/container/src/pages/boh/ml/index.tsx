import { Link } from "react-router-dom";

export default function MLIndex() {
  return (
    <div className="panel">
      <h1>Machine Learning</h1>
      <p>Training data capture and management</p>

      <nav className="secondary-nav">
        <ul>
          <li><Link to="/boh/ml/imageCapture">Image Capture</Link> - Capture training images with controlled lighting</li>
          <li><Link to="/boh/ml/imageList">Image List</Link> - Browse and manage ML training images</li>
        </ul>
      </nav>
    </div>
  );
}