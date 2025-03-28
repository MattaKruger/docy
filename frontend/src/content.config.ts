import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

const tasks = defineCollection({
  loader: glob({ pattern: "**/*.{md, mdx}", base: "./src/tasks" }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
  }),
});

export const collections = { tasks };
