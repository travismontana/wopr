interface ImageGalleryProps {
    gameId: string;
    imageFiles: string[];  // Just the filenames
}

export function ImageGallery({ gameId, imageFiles }: ImageGalleryProps) {
    const [selectedImage, setSelectedImage] = useState<string | null>(null);
    
    const images = imageFiles.map(filename => {
        const rawUrl = `/wopr/ml/raw/${gameId}/${filename}`;
        const thumbnailUrl = `/wopr/ml/thumbnails/${gameId}/${filename}`;
        
        return {
            filename,
            rawUrl,
            thumbnailUrl,
            // We'll check thumbnail existence by trying to load it
        };
    });

    return (
        <div className="image-gallery">
            <div className="gallery-header">
                <h2>{gameId}</h2>
                <span className="image-count">{images.length} images</span>
            </div>
            
            <div className="thumbnail-grid">
                {images.map((img) => (
                    <div 
                        key={img.filename}
                        className="thumbnail-item"
                        onClick={() => setSelectedImage(img.rawUrl)}
                    >
                        <img 
                            src={img.thumbnailUrl}
                            alt={img.filename}
                            loading="lazy"
                            onError={(e) => {
                                // Thumbnail doesn't exist, use raw image
                                e.currentTarget.src = img.rawUrl;
                                e.currentTarget.classList.add('no-thumb');
                            }}
                        />
                        <div className="thumbnail-label">{img.filename}</div>
                    </div>
                ))}
            </div>

            {selectedImage && (
                <div 
                    className="lightbox"
                    onClick={() => setSelectedImage(null)}
                >
                    <img src={selectedImage} alt="Full size" />
                    <button className="close-btn">✕</button>
                </div>
            )}
        </div>
    );
}