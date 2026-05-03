export interface ImagePlaceholderProps {
  filename: string;
  bytes: number;
}

export function ImagePlaceholder({ filename, bytes }: ImagePlaceholderProps): JSX.Element {
  return (
    <div className="image-placeholder" role="region" aria-label={`Image placeholder for ${filename}`}>
      <div className="image-placeholder-card">
        <div className="image-placeholder-name">{filename}</div>
        <div className="image-placeholder-meta">{bytes.toLocaleString()} bytes</div>
        <div className="image-placeholder-note">binary content not previewed</div>
      </div>
    </div>
  );
}
