import React from "react";
import { Link } from "react-router-dom";

function Navbar() {
  return (
    <div className="navbar">
      
      {/* Logo + nombre */}
      <div className="logo-container">
        <img src="/logo.png" alt="Logo" className="logo" />
        <span className="brand">CREDIS</span>
      </div>

      {/* Links */}
      <div className="nav-links">
        <Link to="/clientes">Clientes</Link>
        <Link to="/creditos">Créditos</Link>
      </div>

    </div>
  );
}

export default Navbar;