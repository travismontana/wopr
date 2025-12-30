import React, { useState, useEffect } from 'react';
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
    gameId: string;  // Can be game name or ID
    pieceId?: number; // Optional piece filter
}

// Base URL for image server
const IMAGE_BASE_URL = 'https://wopr-images.studio.abode.tailandtraillabs.org/ml';

export default function ImageGallery({ gameId }: ImageGalleryProps) {
    const [images, setImages] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        loadImages();
    }, [gameId]);

    async function loadImages() {
        setLoading(true);
        setError(null);
        
        try {
            // Fetch from wopr-api mlimages endpoint filtered by game_id
            const res = await fetch(url);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            
            const data: MLImageMetadata[] = await res.json();
            
            // Transform to react-image-gallery format
            const galleryImages = data
                .filter(img => img.filename) // Skip any without filename
                .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()) // Newest first
                .map(img => ({
                    original: `${IMAGE_BASE_URL}/${gameId}/${img.filename}`,
                    thumbnail: `${IMAGE_BASE_URL}/thumbnails/${gameId}/thumbnail-${img.filename}`,
                    description: img.filename,
                    originalTitle: `${img.filename} (${img.object_rotation || 0}° rotation)`,
                    // Store metadata for potential use
                    metadata: {
                        id: img.id,
                        piece_id: img.piece_id,
                        rotation: img.object_rotation,
                        position: img.object_position,
                        color_temp: img.color_temp,
                        light_intensity: img.light_intensity
                    }
                }));
            
            setImages(galleryImages);
        } catch (e: any) {
            setError(e.message);
        } finally {
            setLoading(false);
        }
    }

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
                onErrorImageURL="/placeholder-image.jpg" // Optional fallback
            />
        </div>
    );
}