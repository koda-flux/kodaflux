import { create } from "zustand";

export type Project = {
	id: number;
	project_name: string;
	repo_url: string;
	site_url: string;
	status: string;
};

type KodafluxStore = {
	isGenerating: boolean;
	setIsGenerating: (v: boolean) => void;

	projects: Project[];
	setProjects: (projects: Project[]) => void;
	prependProject: (project: Project) => void;
};

export const useKodafluxStore = create<KodafluxStore>((set) => ({
	isGenerating: false,
	setIsGenerating: (v) => set({ isGenerating: v }),

	projects: [],
	setProjects: (projects) => set({ projects }),
	prependProject: (project) =>
		set((state) => ({ projects: [project, ...state.projects] })),
}));
