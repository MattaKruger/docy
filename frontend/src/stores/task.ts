import { atom, map } from "nanostores";

export const activeTask = atom(false);

export type Task = {
  id: string;
  name: string;
};

type TaskDisplayInfo = Pick<Task, "id" | "name">;

export const tasks = map<Record<string, Task>>({});
export function addTask({ id, name }: TaskDisplayInfo) {
  tasks.setKey(id, { id, name });
}
