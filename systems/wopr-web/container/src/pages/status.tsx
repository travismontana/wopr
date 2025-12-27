import React, { useEffect, useMemo, useRef, useState } from "react";
import "./css/theme.css";

const apiUrl = (window as any).ENV?.WOPR_API_URL || "https://wopr-api.studio.abode.tailandtraillabs.org";

