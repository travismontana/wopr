import React, { useEffect, useMemo, useRef, useState } from "react";
import "./css/theme.css";

export default function MLPage() {
    return (  
    <div className="panel">
        <h1 className="text-2xl font-bold mb-4">Machine Learning Page</h1>
        <p>Welcome to the Machine Learning page of WOPR Web!</p>

        <div className="actions">
            <button className="button">Capture Image</button>
            <button className="button">View Images</button>
        </div>
    </div>
    ); 
}