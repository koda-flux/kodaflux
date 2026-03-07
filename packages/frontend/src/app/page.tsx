import { Button } from "@/components/ui/button";

export default function Home() {
	return (
		<main className="h-screen w-full flex flex-col justify-center items-center gap-4">
			<h1 className="text-5xl font-bold">Hello from Frontend</h1>
			<Button>Click Me!</Button>
		</main>
	);
}
