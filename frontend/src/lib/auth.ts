// frontend/src/lib/auth.ts
// Service for handling JWT token storage and retrieval

const TOKEN_KEY = 'todo-app-jwt';
const AUTH_STATUS_KEY = 'isLoggedIn';

/**
 * Store JWT token in localStorage
 * @param token - The JWT token to store
 */
export const storeToken = (token: string): void => {
  if (typeof window !== 'undefined') {
    localStorage.setItem(TOKEN_KEY, token);
    // Also set the auth status to true
    localStorage.setItem(AUTH_STATUS_KEY, 'true');
  }
};

/**
 * Retrieve JWT token from localStorage
 * @returns The stored JWT token or null if not found
 */
export const getToken = (): string | null => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem(TOKEN_KEY);
  }
  return null;
};

/**
 * Remove JWT token from localStorage (logout)
 */
export const removeToken = (): void => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem(TOKEN_KEY);
    // Also set the auth status to false
    localStorage.removeItem(AUTH_STATUS_KEY);
  }
};

/**
 * Check if user is authenticated (token exists and is not expired)
 * @returns Boolean indicating if user is authenticated
 */
export const isAuthenticated = (): boolean => {
  if (typeof window !== 'undefined') {
    // Check if the user is marked as logged in
    const isLoggedIn = localStorage.getItem(AUTH_STATUS_KEY) === 'true';
    if (!isLoggedIn) {
      return false;
    }

    // If logged in, also verify the token exists (we'll skip expiration check for now to fix redirect issue)
    const token = getToken();
    if (!token) {
      return false;
    }

    try {
      // Decode the token to check if it's expired
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Date.now() / 1000;

      // Return true if token is not expired
      return payload.exp > currentTime;
    } catch (error) {
      // If there's an error decoding the token, just check if it exists
      // This handles cases where the token might not be a proper JWT
      console.warn('Error decoding token, falling back to existence check:', error);
      return !!token;
    }
  }
  return false;
};

/**
 * Set the authentication status in localStorage
 * @param status - Boolean indicating if user is logged in
 */
export const setAuthStatus = (status: boolean): void => {
  if (typeof window !== 'undefined') {
    localStorage.setItem(AUTH_STATUS_KEY, status ? 'true' : 'false');
  }
};

/**
 * Get the authentication status from localStorage
 * @returns Boolean indicating if user is logged in
 */
export const getAuthStatus = (): boolean => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem(AUTH_STATUS_KEY) === 'true';
  }
  return false;
};