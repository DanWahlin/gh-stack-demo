export function validateTaskTitle(title) {
  if (typeof title !== 'string' || !title.trim()) {
    throw new TypeError('Task title is required');
  }

  return title.trim();
}

export function createTask(title) {
  return {
    id: crypto.randomUUID(),
    title: validateTaskTitle(title),
    completed: false,
  };
}
