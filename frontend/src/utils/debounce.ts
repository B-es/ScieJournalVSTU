export function debounce<Args extends unknown[]>(fn: (...args: Args) => void, waitMs: number) {
  let timeoutId: ReturnType<typeof setTimeout> | undefined;

  function debounced(...args: Args) {
    if (timeoutId) clearTimeout(timeoutId);
    timeoutId = setTimeout(() => fn(...args), waitMs);
  }

  debounced.cancel = () => {
    if (timeoutId) clearTimeout(timeoutId);
  };

  return debounced;
}
