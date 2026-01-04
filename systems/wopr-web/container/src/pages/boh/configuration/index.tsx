import { Link } from "react-router-dom";

export default function ConfigurationIndex() {
  const items = [
    { to: "/boh/configuration/apiview", title: "APIView", desc: "View of the configuration as seen from the API" },
  ];

  return (
    <div className="page">
      <div className="navList">
        {items.map((i) => (
          <div key={i.to} className="navItem">
            <Link to={i.to}><button>{i.title}</button></Link>
            <span className="desc"> - {i.desc}</span>
          </div>
        ))}
      </div>
    </div>
  );
}