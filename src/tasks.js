export function createTask(title) {
  return {
    id: crypto.randomUUID(),
    title,
    completed: false,
  };
}

export function isValidTask(task) {
  return Boolean(task?.title?.trim());
}
