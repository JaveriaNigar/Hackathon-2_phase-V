// frontend/src/services/notifications.ts
import { getToken } from '@/lib/auth';
import apiClient from './api';

export interface Notification {
    id: string;
    task_id: string;
    user_id: string;
    message: string;
    scheduled_time: string;
    sent_status: 'pending' | 'sent';
    delivery_method: string;
    created_at: string;
    sent_at?: string;
}

/**
 * Helper function to extract user ID from JWT token
 */
const getUserIdFromToken = (): string => {
    const token = getToken();
    if (!token) {
        throw new Error('No authentication token found');
    }

    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        const userId = payload.userId || payload.sub;

        if (!userId) {
            throw new Error('User ID not found in token');
        }

        return userId;
    } catch (error) {
        console.error('Error decoding token:', error);
        throw new Error('Invalid token format');
    }
};

/**
 * Helper function to make authenticated API requests using unified apiClient
 */
const apiRequest = async (endpoint: string, options: any = {}) => {
    try {
        const method = (options.method || 'GET').toLowerCase();
        const config = {
            ...options,
            url: endpoint,
            method,
        };

        if (options.body && !options.data) {
            config.data = typeof options.body === 'string' ? JSON.parse(options.body) : options.body;
        }

        const response = await apiClient(config);
        return response.data;
    } catch (error: any) {
        console.error(`API request failed [${endpoint}]:`, error);
        throw new Error(error.response?.data?.detail || `HTTP error! status: ${error.response?.status}`);
    }
};

/**
 * Get all notifications for the current user
 */
export const getNotifications = async (sentStatus?: string): Promise<Notification[]> => {
    try {
        const userId = getUserIdFromToken();
        let url = `${userId}/notifications?t=${Date.now()}`;
        if (sentStatus) {
            url += `&sent_status=${sentStatus}`;
        }
        const notifications = await apiRequest(url);
        return notifications;
    } catch (error) {
        console.error('Error fetching notifications:', error);
        throw error;
    }
};

/**
 * Mark a notification as sent
 */
export const markAsSent = async (notificationId: string): Promise<Notification> => {
    try {
        const userId = getUserIdFromToken();
        const notification = await apiRequest(`${userId}/notifications/${notificationId}/mark-sent`, {
            method: 'PUT',
        });
        return notification;
    } catch (error) {
        console.error('Error marking notification as sent:', error);
        throw error;
    }
};
