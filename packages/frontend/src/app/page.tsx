"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { ExternalLink, FileText, Github, Loader2 } from "lucide-react";
import { useEffect, useRef } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { z } from "zod";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
	Empty,
	EmptyDescription,
	EmptyHeader,
	EmptyMedia,
	EmptyTitle,
} from "@/components/ui/empty";
import {
	Form,
	FormControl,
	FormField,
	FormItem,
	FormMessage,
} from "@/components/ui/form";
import {
	InputGroup,
	InputGroupAddon,
	InputGroupInput,
} from "@/components/ui/input-group";

import { type Project, useKodafluxStore } from "@/store/useKodafluxStore";

const API_URL = process.env.NEXT_PUBLIC_API_URL;

const formSchema = z.object({
	repo_url: z
		.string()
		.min(1, "Repository URL is required")
		.url("Must be a valid URL")
		.refine(
			(url) => url.startsWith("https://github.com/"),
			"Must be a valid GitHub repository URL",
		),
});

type FormValues = z.infer<typeof formSchema>;

export default function Home() {
	const { isGenerating, setIsGenerating, projects, setProjects } =
		useKodafluxStore();
	const projectCountRef = useRef(0);

	const form = useForm<FormValues>({
		resolver: zodResolver(formSchema),
		defaultValues: {
			repo_url: "",
		},
	});

	const isDisabled = form.formState.isSubmitting || isGenerating;

	// Polling for projects
	useEffect(() => {
		const fetchProjects = async () => {
			try {
				const response = await fetch(`${API_URL}/projects`);
				if (response.ok) {
					const data: Project[] = await response.json();

					// Check if a new project was added during generation
					if (isGenerating && data.length > projectCountRef.current) {
						const newProject = data[0];
						setIsGenerating(false);
						form.reset();
						toast.success("Docs ready!", {
							description: (
								<a
									href={newProject?.site_url}
									target="_blank"
									rel="noopener noreferrer"
									className="text-primary underline underline-offset-4 hover:text-primary/80"
								>
									{newProject?.site_url}
								</a>
							),
							duration: 30000,
						});
					}

					projectCountRef.current = data.length;
					setProjects(data);
				}
			} catch (error) {
				console.error("Failed to fetch projects:", error);
			}
		};

		fetchProjects();
		const interval = setInterval(fetchProjects, 10000);
		return () => clearInterval(interval);
	}, [isGenerating, setIsGenerating, setProjects, form]);

	const onSubmit = async (values: FormValues) => {
		try {
			setIsGenerating(true);
			const response = await fetch(`${API_URL}/projects/create`, {
				method: "POST",
				headers: {
					"Content-Type": "application/json",
				},
				body: JSON.stringify({ repo_url: values.repo_url }),
			});

			if (!response.ok) {
				throw new Error("Failed to create project");
			}
		} catch (error) {
			console.error("Error creating project:", error);
			setIsGenerating(false);
			toast.error("Failed to start generation", {
				description: "Please try again later.",
			});
		}
	};

	return (
		<main className="min-h-screen bg-background">
			{/* Hero Section */}
			<section className="flex min-h-[60vh] flex-col items-center justify-center px-4 py-16">
				<div className="mx-auto w-full max-w-xl text-center">
					<img alt="KodaFlux Logo" src="/logo.png" />
					<p className="mt-2 text-lg text-muted-foreground text-balance">
						Drop a GitHub repo. Get a documentation site.
					</p>

					<Form {...form}>
						<form
							onSubmit={form.handleSubmit(onSubmit)}
							className="mt-8 space-y-4"
						>
							<FormField
								control={form.control}
								name="repo_url"
								render={({ field }) => (
									<FormItem>
										<FormControl>
											<InputGroup data-disabled={isDisabled || undefined}>
												<InputGroupAddon align="inline-start">
													<Github className="size-4" />
												</InputGroupAddon>
												<InputGroupInput
													placeholder="https://github.com/owner/repo"
													disabled={isDisabled}
													{...field}
												/>
											</InputGroup>
										</FormControl>
										<FormMessage />
									</FormItem>
								)}
							/>

							<Button
								type="submit"
								size="lg"
								className="w-full"
								disabled={isDisabled}
							>
								{isDisabled ? (
									<>
										<Loader2 className="size-4 animate-spin" />
										Generating...
									</>
								) : (
									"Generate Docs"
								)}
							</Button>

							<p className="text-sm text-muted-foreground">
								{
									"We'll scan your dependencies and generate a full documentation site."
								}
							</p>

							{isGenerating && (
								<p className="text-sm text-muted-foreground animate-pulse">
									{
										"⏳ Analysing repository and generating docs... this may take a few minutes."
									}
								</p>
							)}
						</form>
					</Form>
				</div>
			</section>

			{/* Projects Gallery Section */}
			<section className="border-t border-border px-4 py-16">
				<div className="mx-auto max-w-6xl">
					<h2 className="mb-8 text-2xl font-semibold text-foreground">
						Previously Generated Projects
					</h2>

					{projects.length === 0 ? (
						<Empty className="border">
							<EmptyHeader>
								<EmptyMedia variant="icon">
									<FileText className="size-5" />
								</EmptyMedia>
								<EmptyTitle>No projects yet</EmptyTitle>
								<EmptyDescription>
									Generate your first one above.
								</EmptyDescription>
							</EmptyHeader>
						</Empty>
					) : (
						<div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
							{projects.map((project, index) => (
								<Card
									key={project.id}
									className="animate-in fade-in duration-500"
									style={{ animationDelay: `${index * 50}ms` }}
								>
									<CardHeader className="pb-2">
										<div className="flex items-start justify-between gap-2">
											<CardTitle className="text-base font-bold">
												{project.project_name}
											</CardTitle>
											<Badge
												variant="secondary"
												className="shrink-0 bg-green-500/10 text-green-500 border-green-500/20"
											>
												{project.status}
											</Badge>
										</div>
									</CardHeader>
									<CardContent className="space-y-4">
										<a
											href={project.repo_url}
											target="_blank"
											rel="noopener noreferrer"
											className="block truncate text-sm text-muted-foreground hover:text-foreground hover:underline"
										>
											{project.repo_url}
										</a>
										<Button variant="outline" size="sm">
											<a
												href={project.site_url}
												target="_blank"
												rel="noopener noreferrer"
											>
												View Docs
												<ExternalLink className="ml-2 size-3" />
											</a>
										</Button>
									</CardContent>
								</Card>
							))}
						</div>
					)}
				</div>
			</section>
		</main>
	);
}
