import { ref } from "vue";
import { defineStore } from "pinia";
import { client } from "./client";
import type { components } from "../api";

export const useProjectStore = defineStore("project", () => {
  const projects = ref<components["schemas"]["ProjectOut"][]>([]);
  const currentProject = ref<components["schemas"]["ProjectOut"] | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  async function fetchProjects() {
    loading.value = true;
    error.value = null;
    try {
      const { data, error: apiError } = await client.GET("/api/v1/projects/");

      if (apiError) {
        throw new Error(apiError.message || "Failed to fetch projects");
      }

      projects.value = data || [];
    } catch (err) {
      console.error("Error fetching projects:", err);
      error.value = err instanceof Error ? err.message : "Unknown error occurred";
    } finally {
      loading.value = false;
    }
  }

  async function getProject(projectId: number) {
    loading.value = true;
    error.value = null;
    try {
      const { data, error: apiError } = await client.GET(`/api/v1/projects/${projectId}`, {
        params: {
          project_id: projectId
        }
      });

      if (apiError) {
        throw new Error(apiError.message || "Failed to fetch project");
      }

      currentProject.value = data || null;
      return data;
    } catch (err) {
      console.error(`Error fetching project ${projectId}:`, err);
      error.value = err instanceof Error ? err.message : "Unknown error occurred";
      return null;
    } finally {
      loading.value = false;
    }
  }

  async function createProject(projectData: components["schemas"]["ProjectIn"]) {
    loading.value = true;
    error.value = null;
    try {
      const { data, error: apiError } = await client.POST("/api/v1/projects/", {
        body: projectData
      });

      if (apiError) {
        throw new Error(apiError.message || "Failed to create project");
      }

      // Refresh projects list after creating a new one
      await fetchProjects();
      return data;
    } catch (err) {
      console.error("Error creating project:", err);
      error.value = err instanceof Error ? err.message : "Unknown error occurred";
      return null;
    } finally {
      loading.value = false;
    }
  }

  async function updateProject(projectId: number, projectData: components["schemas"]["ProjectUpdate"]) {
    loading.value = true;
    error.value = null;
    try {
      const { data, error: apiError } = await client.PUT(`/api/v1/projects/${projectId}`, {
        body: projectData
      });

      if (apiError) {
        throw new Error(apiError.message || "Failed to update project");
      }

      // Refresh the current project and projects list
      if (currentProject.value && currentProject.value.id === projectId) {
        await getProject(projectId);
      }
      await fetchProjects();

      return data;
    } catch (err) {
      console.error(`Error updating project ${projectId}:`, err);
      error.value = err instanceof Error ? err.message : "Unknown error occurred";
      return null;
    } finally {
      loading.value = false;
    }
  }

  // Get all projects for a specific user
  async function getUserProjects(userId: number) {
    loading.value = true;
    error.value = null;
    try {
      const { data, error: apiError } = await client.GET(`/api/v1/users/${userId}/projects`, {});

      if (apiError) {
        throw new Error(apiError.message || "Failed to fetch user projects");
      }

      return data || [];
    } catch (err) {
      console.error(`Error fetching projects for user ${userId}:`, err);
      error.value = err instanceof Error ? err.message : "Unknown error occurred";
      return [];
    } finally {
      loading.value = false;
    }
  }

  return {
    projects,
    currentProject,
    loading,
    error,

    fetchProjects,
    getProject,
    createProject,
    updateProject,
    getUserProjects
  };
});
