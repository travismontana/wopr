import React, { useEffect, useMemo, useRef, useState } from "react";
import "./css/theme.css";

const apiUrl = (window as any).ENV?.WOPR_API_URL || "https://wopr-api.studio.abode.tailandtraillabs.org";


type StatusState =
  | { type: "ok" | "error" | "info"; message: string; path?: string }
  | null;

export default function MLPage() {
    const ImageTypes = [
        "setup", 
        "capture", 
        "move", 
        "thumbnail"];

    const ObjectRotations = [ 0, 45, 90, 135, 180, 225, 270, 315];

    const ObjectPositions = [
        { value: "center", label: "Center" },
        { value: "topLeft", label: "Top Left" },
        { value: "topRight", label: "Top Right" },
        { value: "bottomLeft", label: "Bottom Left" },
        { value: "bottomRight", label: "Bottom Right" },
        { value: "topEdge", label: "Top Edge" },
        { value: "bottomEdge", label: "Bottom Edge" },
        { value: "leftEdge", label: "Left Edge" },
        { value: "rightEdge", label: "Right Edge" },
        { value: "nearCenter", label: "Near Center" },
        { value: "random", label: "Random" }
        ];

    type ObjPos = typeof ObjectPositions[number]["value"];

    const ColorTemperatures = ["neutral", "hot", "cold"];

    const LightIntensities = [100, 90, 80, 70, 60, 50, 40, 30, 20, 10];

    const [status, setStatus] = useState<StatusState>(null);
    const [busy, setBusy] = useState<boolean>(false);
    
    const [showCaptureDialog, setShowCaptureDialog] = useState(false);
    const [showViewDialog, setShowViewDialog] = useState(false);

    const [gameName, setGameName] = useState<string>("dune_imperium");
    type ImgType = typeof ImageTypes[number];
    const [subject, setImgType] = useState<ImgType>("setup");
    const [objrotation, setObjRotation] = useState<number>(0);
    const [objposition, setObjPosition] = useState<ObjPos>("center");
    const [colortemperature, setColorTemperature] = useState<string>("neutral");
    const [lightintensity, setLightIntensity] = useState<number>(70);

    const [showGallery, setShowGallery] = useState<boolean>(false);

    const [CameraDictResponse, setCameraDictResponse] = useState<Record<number, CameraInfo>>({});

    function toggleCaptureDialog() {
        if (busy) return;
        setStatus(null);
        setShowCaptureDialog((v) => !v);
    }

    function toggleViewDialog() {
        if (busy) return;
        setStatus(null);
        setShowViewDialog((v) => !v);
    }

    function setStatusMessage(type: "info" | "error" | "success", message: string, path?: string) {
        setStatus({ type, message, path });
    }

    function clearStatusMessage() {
        setStatus(null);
    }  

    function setBusyState(isBusy: boolean) {
        setBusy(isBusy);
    }

    function onChangePageSize(v: PageSize) {
        setPageSize(v);
        setPage(1);
    }

    async function getCameraDict(id: number) {
        try {
            console.log("Fetching camera dictionary from:", `${apiUrl}/api/v1/cameras/1`);
            const res = await fetch(`${apiUrl}/api/v1/cameras/1`);  // ← Fixed: fetch(...) not fetch`...`
            
            if (!res.ok) {
                throw new Error(`Error fetching camera dictionary: ${res.statusText}`);  // ← Fixed: Error(...) not Error`...`
            }
            
            const raw = (await res.json()) as CameraDictResponse;
            const cameraDict: Record<number, CameraInfo> = {};
            raw.cameras.forEach((cam) => {
                cameraDict[cam.id] = cam;
            });
            return cameraDict;
        }
        catch (error) {
            console.error("Error fetching camera dictionary:", error);
            throw error;  // Re-throw so caller knows it failed
        }

    }

    // Add missing state
    const [page, setPage] = useState(1);
    const [pageSize, setPageSize] = useState<number | "all">(10);
    const [totalCount, setTotalCount] = useState(0);

    // Add missing function
    async function doCapture() {
        setBusy(true)
        setStatus({ type: "info", message: "Capturing…" });
        const camdict = await getCameraDict(1);
        console.log("Capture not implemented yet");
    }

    // Add missing computed value
    const canGo = gameName.length > 0;

    return (  
        <section>
        <div className="panel">
            <h1 className="text-2xl font-bold mb-4">Machine Learning Page</h1>
            <p>Welcome to the Machine Learning page of WOPR Web!</p>

            <div className="actions">
                <button className="button" onClick={toggleCaptureDialog}>
                    {showCaptureDialog ? "Close Capture Image" : "Capture Image"}
                </button>
                <button className="button" onClick={toggleViewDialog}>
                    {showViewDialog ? "Close View Images" : "View Images"}
                </button>
            </div>

            {status && (
                <div className={`status status-${status.type}`}>
                {status.message}
                {status.path && (
                    <>
                    :{" "}
                    <a href={status.path} target="_blank" rel="noreferrer">
                    {status.path}
                    </a>
                    </>
                )}
                </div>
            )}

            {showCaptureDialog && (
                <div className="dialog">
                    <h2 className="text-xl font-bold mb-2">Capture Image Dialog</h2>
                    <div className="wopr-dialog-backdrop" role="dialog" aria-modal="true">
                        <div className="wopr-dialog">
                            <div className="form">
                                <label>
                                    Game Name:
                                    <input 
                                    type="text" 
                                    name="gameName" 
                                    value={gameName} 
                                    onChange={(e) => setGameName(e.target.value)}
                                    placeholder="dune_imperium"
                                    />
                                </label>
                                <br></br>
                                <label>
                                    Image Type
                                    <select value={subject} onChange={(e) => setImgType(e.target.value as ImgType)}>
                                        {ImageTypes.map((type) => (
                                            <option key={type} value={type}>
                                                {type.charAt(0).toUpperCase() + type.slice(1)}
                                            </option>
                                        ))}
                                    </select>
                                </label>
                                <br></br>
                                <label>
                                    Object Rotation
                                    <select value={objrotation} onChange={(e) => setObjRotation(Number(e.target.value))}>
                                        {ObjectRotations.map((angle) => (
                                            <option key={angle} value={angle}>
                                                {angle}°
                                            </option>
                                        ))}
                                    </select>
                                </label>
                                <br></br>
                                <label>
                                    Object Position (0 is referenced to North on the game playfield, or just pick one to be zero)
                                    <select value={objposition} onChange={(e) => setObjPosition(e.target.value as ObjPos)}>
                                        {ObjectPositions.map((pos) => (
                                            <option key={pos.value} value={pos.value}>
                                                {pos.label}
                                            </option>
                                        ))}
                                    </select>
                                </label>
                                <br></br>   
                                <label>
                                    Color Temperature
                                    <select value={colortemperature} onChange={(e) => setColorTemperature(e.target.value)}>
                                        {ColorTemperatures.map((temp) => (
                                            <option key={temp} value={temp}>
                                                {temp.charAt(0).toUpperCase() + temp.slice(1)}
                                            </option>
                                        ))}
                                    </select>
                                </label>
                                <br></br>
                                <label>
                                    Light Intensity
                                    <select value={lightintensity} onChange={(e) => setLightIntensity(Number(e.target.value))}>
                                        {LightIntensities.map((intensity) => (
                                            <option key={intensity} value={intensity}>
                                                {intensity}%
                                            </option>
                                        ))}
                                    </select>
                                </label>
                            </div>
                            <div className="wopr-dialog-actions">
                                <button onClick={toggleCaptureDialog} disabled={busy}>
                                    Close
                                </button>
                                <button onClick={doCapture} disabled={!canGo}>
                                    {busy ? "Capturing…" : "Go"}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {showViewDialog && (
                <div className="dialog">
                    <h2 className="text-xl font-bold mb-2">View Images Dialog</h2>
                    <p>This is where the view images functionality would go.</p>
                </div>
            )}

        </div>
        </section>
    ); 
}