interface Props {
  path: string;
  base64?: string;
}

export function ImagePlaceholder({ path, base64 }: Props) {
  const src = base64 ? `data:image/${path.endsWith(".png") ? "png" : "jpeg"};base64,${base64}` : `/api/file?path=${encodeURIComponent(path)}`;
  return (
    <div className="image-placeholder" data-testid="image-placeholder">
      <img src={src} alt={path} loading="lazy" />
      <p className="image-meta">{path}</p>
    </div>
  );
}
