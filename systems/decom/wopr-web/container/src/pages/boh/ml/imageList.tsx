import React, { useState, useEffect } from 'react';
import ImageGallery from 'react-image-gallery';
import 'react-image-gallery/styles/css/image-gallery.css';

interface MLImageMetadata {
    id: number;
    uuid: string;
    filename: string;
    object_rotation: number;
    object_position: string;
    color_temp: string;
    light_intensity: number;
    game_uuid: number;
    piece_id: number;
    status: string;
    user_created: string | null;
    date_created: string;
    user_updated: string | null;
    date_updated: string | null;
}

export function MLGallery() {
    const [images, setImages] = useState<any[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        loadImages();
    }, []);

    async function loadImages() {
        setLoading(true);
        setError(null);

        try {
            const res = await fetch('https://wopr-api.studio.abode.tailandtraillabs.org/api/v1/mlimages?limit=100&offset=0');
            if (!res.ok) throw new Error(`HTTP ${res.status}`);

            const data: MLImageMetadata[] = await res.json();

            const galleryImages = data.map(img => {
                const imageUrl = `https://images.studio.abode.tailandtraillabs.org/ml/incoming/${img.filename}`;
                const thumbnailUrl = `https://thumbor.studio.abode.tailandtraillabs.org/unsafe/300x0/ml/incoming/${img.filename}`;

                return {
                    original: imageUrl,
                    thumbnail: thumbnailUrl,
                    description: img.filename
                };
            });

            setImages(galleryImages);
        } catch (e: any) {
            console.error('Load error:', e);
            setError(e.message);
        } finally {
            setLoading(false);
        }
    }

    if (loading) return <div>Loading images...</div>;
    if (error) return <div>Error: {error}</div>;
    if (images.length === 0) return <div>No images found</div>;

    return (
        <div className="gallery">
            <h2>{images.length} images</h2>
            <ImageGallery
                items={images}
                showPlayButton={true}
                showFullscreenButton={true}
                showThumbnails={true}
                lazyLoad={true}
            />
        </div>
    );
}