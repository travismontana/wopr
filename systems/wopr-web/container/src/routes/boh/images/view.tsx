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
    const [isFullSize, setIsFullSize] = useState(false);
    const handleThumbnailClick = (imageUrl: string) => {
        setSelectedImage(imageUrl);
        setIsFullSize(false); // Start at fit-to-window
    };
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
                    const rawUrl = `/wopr/ml/${gameId}/${filename}`;
                    const thumbUrl = `/wopr/ml/thumbnails/${gameId}/thumbnail-${filename}`;
                    
                    return (
                        <div 
                            key={filename}
                            className="thumbnail-item"
                            onClick={() => handleThumbnailClick(rawUrl)}
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
                <div className="lightbox"
                    onClick={() => {
                        setSelectedImage(null);
                        setIsFullSize(false);
                    }}
                >
                    <div 
                        className={`lightbox-content ${isFullSize ? 'full-size' : 'fit-window'}`}
                        onClick={(e) => e.stopPropagation()}
                    >
                        <img 
                            src={selectedImage} 
                            alt="Full size"
                            onClick={() => setIsFullSize(!isFullSize)}
                            style={{ cursor: isFullSize ? 'zoom-out' : 'zoom-in' }}
                        />
                        <button 
                            className="close-btn"
                            onClick={(e) => {
                                e.stopPropagation();
                                setSelectedImage(null);
                                setIsFullSize(false);
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