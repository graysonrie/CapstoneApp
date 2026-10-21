import { Badge } from "@/components/ui/badge";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import Image from "next/image";
import { PlantRarity } from "../types/profileTypes";

interface Props {
  id: number;
  imageBase64: string | null;
  commonName: string;
  scientificName: string;
  rarity: PlantRarity | null;
  foundOn: string;
}
const RARITY_VARIANT: Record<PlantRarity, "outline" | "secondary" | "default"> =
  {
    Common: "default",
    Uncommon: "secondary",
    Rare: "outline",
  };

export default function FoundPlantComponent({
  id,
  imageBase64,
  foundOn,
  commonName,
  scientificName,
  rarity,
}: Props) {
  return (
    <Card key={id} size="sm" className="gap-3">
      <CardHeader className=" ">
        <CardTitle className="leading-tight">{commonName}</CardTitle>
        <CardDescription className="italic">{scientificName}</CardDescription>

        {imageBase64 ? (
          <Image
            src={imageBase64}
            alt=""
            className="mx-auto h-20 rounded-2xl object-cover"
            width={80}
            height={80}
          />
        ) : (
          <div className="mx-4 h-20 rounded-2xl bg-muted" aria-hidden />
        )}
      </CardHeader>
      <CardContent className="flex flex-col items-center justify-between gap-1">
        {rarity ? (
          <Badge variant={RARITY_VARIANT[rarity]}>{rarity}</Badge>
        ) : (
          <span />
        )}
        <span className="text-xs text-muted-foreground">{foundOn}</span>
      </CardContent>
    </Card>
  );
}
