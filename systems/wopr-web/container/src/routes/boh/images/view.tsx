import React, { useEffect, useMemo, useRef, useState } from "react";

interface NginxFileEntry {
    name: string;
    type: 'file' | 'directory';
    mtime: string;
    size: number;
}

interface ImageGalleryProps {
    gameId: string;
}

export default function ImageGallery({ gameId }: ImageGalleryProps) {
    const [images, setImages] = useState<string[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [selectedImage, setSelectedImage] = useState<string | null>(null);

    useEffect(() => {
        loadImages();
    }, [gameId]);

    async function loadImages() {
        setLoading(true);
        setError(null);
        
        try {
            // Fetch directory listing as JSON from nginx
            const res = await fetch(`/wopr/ml/${gameId}/`);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            
            const entries: NginxFileEntry[] = await res.json();
            
            // Filter for image files only
            const imageFiles = entries
                .filter(e => e.type === 'file')
                .filter(e => /\.(jpe?g|png|gif|webp)$/i.test(e.name))
                .map(e => e.name)
                .sort();
            
            setImages(imageFiles);
        } catch (e: any) {
            setError(e.message);
        } finally {
            setLoading(false);
        }
    }

    if (loading) {
        return <div className="gallery-loading">Loading images...</div>;
    }

    if (error) {
        return <div className="gallery-error">Error loading {gameId}: {error}</div>;
    }

    if (images.length === 0) {
        return <div className="gallery-empty">No images found in {gameId}</div>;
    }

    return (
        <div className="image-gallery">
            <div className="gallery-header">
                <h2>{gameId}</h2>
                <span className="image-count">{images.length} images</span>
            </div>
            
            <div className="thumbnail-grid">
                {images.map((filename) => {
                    const rawUrl = `/remote/wopr/ml/${gameId}/${filename}`;
                    const thumbUrl = `/remote/wopr/ml/thumbnails/${gameId}/${filename}`;
                    
                    return (
                        <div 
                            key={filename}
                            className="thumbnail-item"
                            onClick={() => setSelectedImage(rawUrl)}
                        >
                            <img 
                                src={thumbUrl}
                                alt={filename}
                                loading="lazy"
                                onError={(e) => {
                                    // Thumbnail doesn't exist, use raw
                                    const target = e.currentTarget;
                                    target.src = rawUrl;
                                    target.classList.add('no-thumb');
                                }}
                            />
                            <div className="thumbnail-label">{filename}</div>
                        </div>
                    );
                })}
            </div>

            {selectedImage && (
                <div 
                    className="lightbox"
                    onClick={() => setSelectedImage(null)}
                >
                    <div className="lightbox-content">
                        <img src={selectedImage} alt="Full size" />
                        <button 
                            className="close-btn"
                            onClick={(e) => {
                                e.stopPropagation();
                                setSelectedImage(null);
                            }}
                        >
                            ✕
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}