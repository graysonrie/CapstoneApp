import { convertFileSrc } from "@tauri-apps/api/core";

interface Props {
  path: string;
  className?: string;
  altText?: string;
}

export default function LocalImage({ path, className, altText }: Props) {
  return <img src={convertFileSrc(path)} alt={altText} className={className} />;
}
