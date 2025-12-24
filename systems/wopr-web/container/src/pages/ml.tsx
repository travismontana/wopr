import React, { useEffect, useMemo, useRef, useState } from "react";
import "./css/theme.css";

const apiUrl = (window as any).ENV?.WOPR_API_URL || "https://wopr-api.studio.abode.tailandtraillabs.org";


type StatusState =
  | { type: "ok" | "error" | "info"; message: string; path?: string }
  | null;

export default function MLPage() {

    const gameList = [
        { value: "dune_imperium", label: "Dune Imperium" },
        { value: "cyberpunk_red", label: "Cyberpunk Red" },]

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

    // Placeholder until the api is more .
    const pieces =[
        { value: "1", label: "1_solari" },
        { value: "2", label: "5_solari" },
        { value: "3", label: "1_spice" },
        { value: "4", label: "5_spice" },
        { value: "5", label: "infantry" },
        { value: "6", label: "cavalry" },
        { value: "7", label: "siege_engine" },
        { value: "8", label: "agent" },
        { value: "9", label: "hero" },
        { value: "10", label: "ornithopter" },
        { value: "11", label: "fremen_warrior" },
        { value: "12", label: "sandworm" },
        { value: "13", label: "carryall" },
        { value: "14", label: "deployer" },
        { value: "15", label: "obj_15" },
        { value: "16", label: "obj_16" },
        { value: "17", label: "obj_17" },
        { value: "18", label: "obj_18" },
        { value: "19", label: "obj_19" },
        { value: "20", label: "obj_20" },
        { value: "21", label: "obj_21" },
        { value: "22", label: "obj_22" },
        { value: "23", label: "obj_23" },
        { value: "24", label: "obj_24" },
        { value: "25", label: "obj_25" },
        { value: "26", label: "obj_26" },
        { value: "27", label: "obj_27" },
        { value: "28", label: "obj_28" },
        { value: "29", label: "obj_29" },
        { value: "30", label: "obj_30" },
        { value: "31", label: "obj_31" },
        { value: "32", label: "obj_32" },
        { value: "33", label: "obj_33" },
        { value: "34", label: "obj_34" },
        { value: "35", label: "obj_35" },
        { value: "36", label: "obj_36" },
        { value: "37", label: "obj_37" },
        { value: "38", label: "obj_38" },
        { value: "39", label: "obj_39" },
        { value: "40", label: "obj_40" },
        { value: "41", label: "obj_41" },
        { value: "42", label: "obj_42" },
        { value: "43", label: "obj_43" },
        { value: "44", label: "obj_44" },
        { value: "45", label: "obj_45" },
        { value: "46", label: "obj_46" },
        { value: "47", label: "obj_47" },
        { value: "48", label: "obj_48" },
        { value: "49", label: "obj_49" },
        { value: "50", label: "obj_50" }
    ]

    type ObjPos = typeof ObjectPositions[number]["value"];

    const ColorTemperatures = ["neutral", "hot", "cold"];

    const LightIntensities = [100, 90, 80, 70, 60, 50, 40, 30, 20, 10];

    const [status, setStatus] = useState<StatusState>(null);
    const [busy, setBusy] = useState<boolean>(false);
    
    const [showCaptureDialog, setShowCaptureDialog] = useState(false);
    const [showViewDialog, setShowViewDialog] = useState(false);

    const [gameName, setGameName] = useState<string>("dune_imperium");
    const [pieceName, setPieceName] = useState<string>("1_solari");
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
            raw.camera.forEach((cam) => {
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



    async function doCapture() {
        setBusy(true)
        setStatus({ type: "info", message: "Capturing…" });
        const camdict = await getCameraDict(1);
        console.log("Got camera dictionary:", camdict);
        const url = camdict[1]?.url;
        const port = camdict[1]?.port || "5000";
        if (!url) {
            setStatus({ type: "error", message: "Camera not found" });
            setBusy(false);
            return;
        } else {
        // subject, objrotation, objposition, colortemperature, lightintensity
        // Here you would add the logic to capture the image using the camera URL and parameters
        // For now, we just log the parameters
        console.log("Capturing image with parameters:");
        console.log("Game Name:", gameName);
        console.log("Image Type:", subject);
        console.log("Piece Name:", pieceName);
        console.log("Object Rotation:", objrotation);
        console.log("Object Position:", objposition);
        console.log("Color Temperature:", colortemperature);
        console.log("Light Intensity:", lightintensity);
        

        // subject, objrotation, objposition, colortemperature, lightintensity
        // Here you would add the logic to capture the image using the camera URL and parameters
        const gameId = gameName;
        const timestamp = new Date()
            .toISOString()
            .replace(/[-:]/g, '')
            .replace('T', '-')
            .slice(0, 15);  // "20241222-143022"
        const randomId = Math.random().toString(36).substring(2, 8);  // e.g., "7k3x9m"
        // ${pieceName}-${objposition}-rot${objrotation}-pct${lightintensity}-temp${colortemperature}-${timestamp}

        const fName = `${pieceName}-${objposition}-rot${objrotation}-pct${lightintensity}-temp${colortemperature}-${timestamp}-${randomId}`;
        const subjectName = fName;
        const sequence = 1; // You might want to manage sequence differently

        try {
            const res = await fetch(`${apiUrl}/api/v1/cameras/capture`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    captureType: "ml_capture",
                    game_id: gameId.trim(),
                    subject: subject.trim(),
                    subject_name: subjectName.trim(),
                    sequence: Number(sequence),
                   }),
            });

            const raw = (await res.text()).trim();
            if (!res.ok) throw new Error(`HTTP ${res.status}: ${raw}`);

            const httpPath = raw.startsWith("/remote/wopr/")
                ? `/wopr/${raw.slice("/remote/wopr/".length)}`
                : raw;

            setStatus({ type: "ok", message: "Saved", path: httpPath });

            setSequence((s) => s + 1);
            setShowCaptureDialog(false);
            } catch (e: any) {
            setStatus({ type: "error", message: e?.message ?? String(e) });
            } finally {
            setBusy(false);
            }

        }
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
                                    Game Name
                                    <select value={gameName} onChange={(e) => setGameName(e.target.value)}>
                                        {gameList.map((game) => (
                                            <option key={game.value} value={game.value}>
                                                {game.label}
                                            </option>
                                        ))}
                                    </select>
                                </label>
                                <br></br>
                                <label>
                                    Piece Name:
                                    <select value={pieceName} onChange={(e) => setPieceName(e.target.value)}>
                                        {pieces.map((piece) => (
                                            <option key={piece.value} value={piece.value}>
                                                {piece.label}
                                            </option>
                                        ))}
                                    </select>
                                </label>
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