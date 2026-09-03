import { Button } from "@/components/ui/button";
import Link from "next/link";

export default function PlantScreenshotPage() {
  return (
    <div>
      I am PlantScreenshotPage
      <Button>
        <Link href={"/home"}>Back to home</Link>
      </Button>
    </div>
  );
}
