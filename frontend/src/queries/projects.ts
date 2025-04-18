import { ref } from "vue";
import { useRoute } from "vue-router";
import { defineQuery, useQuery, useMutation, defineMutation } from "@pinia/colada";

import { getProjectsApiV1ProjectsGet, getProjectApiV1ProjectsProjectIdGet, createProjectApiV1ProjectsPost, type ProjectUpdate} from "@/client";
import { type ProjectIn, type ProjectType } from "@/client";


const route = useRoute()


export const useGetProjects = defineQuery(() => {
  const { state, ...rest } = useQuery({
    key: () => ['projects'],
    query: () => getProjectsApiV1ProjectsGet()
  });
  return {
    ...rest,
    projects: state.value.data?.data,
  }
})


export const useGetProject = defineQuery(() => {
  const { state, ...rest } = useQuery({
    key: () => ['projects', route.params.id as string],
    query: () => getProjectApiV1ProjectsProjectIdGet({
      path: {
        project_id: parseInt(route.params.id as string, 10)
      }
    })
  });
  return {
    ...rest,
    project: state.value.data?.data
  }
})


export const useCreateProject = defineMutation(() => {
  const projectIn = ref<ProjectIn>({
    name: '',
    project_type: 'code',
    framework: ''
  });
  const { mutate, ...mutation } = useMutation({
    mutation: async (projectIn: ProjectIn) => await createProjectApiV1ProjectsPost({
      body: projectIn
    })
  });
  return {
    ...mutation,
    createProject: () => mutate(projectIn.value),
    projectIn
  }
})


export const useUpdateProject = defineMutation(() => {
  const projectUpdate = ref<ProjectUpdate>({

  })
})
