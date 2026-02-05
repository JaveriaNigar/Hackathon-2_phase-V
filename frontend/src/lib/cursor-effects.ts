// cursor-effects.ts
// Utility functions for cursor interactive effects

/**
 * Adds cursor position tracking to an element for dynamic glow effects
 */
export function addCursorTracking(element: HTMLElement) {
  const handleMouseMove = (e: MouseEvent) => {
    const rect = element.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;
    
    element.style.setProperty('--x', `${x}%`);
    element.style.setProperty('--y', `${y}%`);
  };

  element.addEventListener('mousemove', handleMouseMove);
  
  // Clean up function
  return () => {
    element.removeEventListener('mousemove', handleMouseMove);
  };
}

/**
 * Creates a ripple effect at the click position
 */
export function createRipple(event: React.MouseEvent<HTMLElement>) {
  const button = event.currentTarget;
  const circle = document.createElement("span");
  const diameter = Math.max(button.clientWidth, button.clientHeight);
  const radius = diameter / 2;

  circle.style.width = circle.style.height = `${diameter}px`;
  circle.style.left = `${event.clientX - button.getBoundingClientRect().left - radius}px`;
  circle.style.top = `${event.clientY - button.getBoundingClientRect().top - radius}px`;
  circle.classList.add("ripple");

  const ripple = button.getElementsByClassName("ripple")[0];
  
  if (ripple) {
    ripple.remove();
  }

  button.appendChild(circle);
}

/**
 * Initializes cursor tracking for all elements with the 'cursor-glow' class
 */
export function initCursorGlowEffects() {
  const elements = document.querySelectorAll('.cursor-glow');
  const cleanupFunctions: Array<() => void> = [];

  elements.forEach(el => {
    if (el instanceof HTMLElement) {
      const cleanup = addCursorTracking(el);
      cleanupFunctions.push(cleanup);
    }
  });

  // Return cleanup function
  return () => {
    cleanupFunctions.forEach(cleanup => cleanup());
  };
}