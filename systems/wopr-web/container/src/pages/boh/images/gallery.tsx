import React, { useState, useEffect, useCallback } from 'react';
import ImageGallery from 'react-image-gallery';
import 'react-image-gallery/styles/css/image-gallery.css';

interface MLImageMetadata {
    id: number;
    filename: string;
    game_id: number;
    piece_id?: number;
    object_rotation?: number;
    object_position?: string;
    color_temp?: string;
    light_intensity?: string;
    created_at: string;
    updated_at: string;
}

interface ImageGalleryProps {
    gameId: string;
}

// Base URL for image server
const IMAGE_BASE_URL = 'https://wopr-images.studio.abode.tailandtraillabs.org/wopr/ml';
const API_BASE_URL = 'https://wopr-api.studio.abode.tailandtraillabs.org';

export default function ImageGallery({ gameId }: ImageGalleryProps) {
    const [images, setImages] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Memoize loadImages to prevent recreation on every render
    const loadImages = useCallback(async () => {
        setLoading(true);
        setError(null);
        if (!gameId) {
            console.warn('ImageGallery: gameId is undefined, skipping fetch');
            setLoading(false);
            return;
        }
        
        try {
            //gameId = 1;
            const url = `${API_BASE_URL}/api/v1/mlimages?game_id=${gameId}&limit=1000`;
            const res = await fetch(url);
            
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            
            const data: MLImageMetadata[] = await res.json();
            
            console.log(`Loaded ${data.length} images for game ${gameId}`);
            
            // Transform to react-image-gallery format
            const galleryImages = data
                .filter(img => img.filename)
                .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
                .map(img => {
                    const original = `${IMAGE_BASE_URL}/${gameId}/${img.filename}`;
                    const thumbnail = `${IMAGE_BASE_URL}/thumbnails/${gameId}/thumbnail-${img.filename}`;
                    
                    return {
                        original: original,
                        thumbnail: thumbnail,
                        description: img.filename,
                        originalTitle: `${img.filename} (${img.object_rotation || 0}° rotation)`,
                        renderThumbInner: () => (
                            <img
                                src={thumbnail}
                                alt={img.filename}
                                onError={(e) => {
                                    e.currentTarget.src = original;
                                }}
                            />
                        )
                    };
                });
            
            setImages(galleryImages);
        } catch (e: any) {
            console.error('Load error:', e);
            setError(e.message);
        } finally {
            setLoading(false);
        }
    }, [gameId]); // Only recreate if gameId changes

    // Only run when loadImages changes (which only happens when gameId changes)
    useEffect(() => {
        loadImages();
    }, [loadImages]);

    if (loading) {
        return <div className="gallery-loading">Loading images from database...</div>;
    }

    if (error) {
        return <div className="gallery-error">Error loading images for {gameId}: {error}</div>;
    }

    if (images.length === 0) {
        return <div className="gallery-empty">No images found in database for game: {gameId}</div>;
    }

    return (
        <div className="image-gallery-container">
            <div className="gallery-header">
                <h2>Game: {gameId}</h2>
                <span className="image-count">{images.length} images</span>
            </div>
            
            <ImageGallery
                items={images}
                showPlayButton={true}
                showFullscreenButton={true}
                showThumbnails={true}
                lazyLoad={true}
                slideOnThumbnailOver={false}
                showIndex={true}
                showBullets={false}
                infinite={true}
            />
        </div>
    );
}