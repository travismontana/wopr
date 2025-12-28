import React, { useEffect, useMemo, useRef, useState } from "react";
import "./css/theme.css";

const apiUrl1 = (window as any).ENV?.WOPR_API_URL || "https://wopr-api.studio.abode.tailandtraillabs.org";

const apiUrl = `${apiUrl1}/api/v1`;

export default function SystemPage() {

  return (
    <div className="infocontent">
      <h1>System Configuration</h1>
      <p>System configuration options will be available here.</p>
    </div>
  );
}