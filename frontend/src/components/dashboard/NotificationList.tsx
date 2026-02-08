// frontend/src/components/dashboard/NotificationList.tsx
import React, { useState, useEffect } from 'react';
import { getNotifications, Notification } from '@/services/notifications';

const NotificationList: React.FC = () => {
    const [notifications, setNotifications] = useState<Notification[]>([]);
    const [loading, setLoading] = useState(true);

    const fetchNotifications = async () => {
        try {
            // Fetch only "sent" notifications to show to the user
            const data = await getNotifications('sent');
            // Sort by scheduled time descending (newest first)
            const sortedData = data.sort((a, b) =>
                new Date(b.scheduled_time).getTime() - new Date(a.scheduled_time).getTime()
            );
            setNotifications(sortedData);
        } catch (error) {
            console.error('Error fetching notifications:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchNotifications();
        // Refresh notifications every 2 minutes
        const interval = setInterval(fetchNotifications, 120000);
        return () => clearInterval(interval);
    }, []);

    if (loading && notifications.length === 0) {
        return null; // Don't show anything while initial loading
    }

    if (notifications.length === 0) {
        return (
            <div className="bg-card-bg border border-border rounded-xl p-4 mb-8 card-ai-style fade-in">
                <h3 className="text-lg font-semibold text-ai-blue mb-2 flex items-center">
                    <span className="mr-2">🔔</span> Reminders
                </h3>
                <p className="text-foreground/70 text-sm">No recent reminders. You're all caught up!</p>
            </div>
        );
    }

    return (
        <div className="bg-card-bg border border-border rounded-xl p-4 mb-8 card-ai-style fade-in">
            <h3 className="text-lg font-semibold text-ai-blue mb-4 flex items-center">
                <span className="mr-2">🔔</span> Recent Reminders
            </h3>
            <div className="space-y-3 max-h-60 overflow-y-auto pr-2 custom-scrollbar">
                {notifications.slice(0, 5).map((notification) => (
                    <div
                        key={notification.id}
                        className="p-3 bg-[#1a1a1a] border border-border/50 rounded-lg hover:border-ai-blue/50 transition-all duration-300"
                    >
                        <div className="flex justify-between items-start">
                            <p className="text-sm text-foreground font-medium">{notification.message}</p>
                            <span className="text-[10px] text-foreground/40 whitespace-nowrap ml-2">
                                {new Date(notification.scheduled_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </span>
                        </div>
                        <p className="text-[10px] text-ai-cyan/70 mt-1">
                            {new Date(notification.scheduled_time).toLocaleDateString()}
                        </p>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default NotificationList;
