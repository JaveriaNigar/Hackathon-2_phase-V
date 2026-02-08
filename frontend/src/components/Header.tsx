'use client';

import { getToken } from '@/lib/auth';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { logout } from '@/services/auth';
import { useEffect, useState } from 'react';

import { getNotifications } from '@/services/notifications';

const Header = () => {
    const [token, setToken] = useState<string | null>(null);
    const [notifCount, setNotifCount] = useState(0);
    const pathname = usePathname();
    const isDashboardPage = pathname === '/dashboard';
    const isAgentPage = pathname === '/agent';

    useEffect(() => {
        // Only run on the client side
        setToken(getToken());

        if (getToken()) {
            const fetchCount = async () => {
                try {
                    const data = await getNotifications('sent');
                    setNotifCount(data.length);
                } catch (err) {
                    console.error('Error fetching notification count:', err);
                }
            };
            fetchCount();
            const interval = setInterval(fetchCount, 60000); // Check every minute
            return () => clearInterval(interval);
        }
    }, []);

    const handleLogout = async () => {
        try {
            await logout(); // Call the logout service to remove the token
        } finally {
            window.location.href = '/login'; // Redirect to login after logout
        }
    };

    if (isAgentPage) {
        return null;
    }

    return (
        <header className="bg-card-bg">
            <div className="container mx-auto px-4 py-4 flex justify-between items-center">
                <Link href="/" className="text-xl font-bold bg-gradient-to-r from-ai-blue to-ai-purple bg-clip-text text-transparent font-lexend">
                    AI Todo App
                </Link>
                <nav>
                    {token && (isDashboardPage || isAgentPage) ? (
                        <div className="flex items-center space-x-4">
                            {isDashboardPage && (
                                <Link href="/agent">
                                    <button
                                        className="btn-ai-gradient px-4 py-2 text-sm rounded-lg ripple-effect"
                                    >
                                        Ask Todo Agent
                                    </button>
                                </Link>
                            )}
                            {isAgentPage && (
                                <Link href="/dashboard">
                                    <button
                                        className="btn-ai-gradient px-4 py-2 text-sm rounded-lg ripple-effect"
                                    >
                                        Dashboard
                                    </button>
                                </Link>
                            )}
                            <div className="relative cursor-pointer hover:opacity-80 transition-opacity mr-2">
                                <span className="text-xl">🔔</span>
                                {notifCount > 0 && (
                                    <span className="absolute -top-1 -right-1 bg-ai-purple text-white text-[10px] w-4 h-4 rounded-full flex items-center justify-center font-bold">
                                        {notifCount}
                                    </span>
                                )}
                            </div>
                            <button
                                onClick={handleLogout}
                                className="btn-ai-gradient px-8 py-4 text-lg rounded-lg ripple-effect"
                            >
                                Logout
                            </button>
                        </div>
                    ) : (
                        <div className="flex space-x-4">
                            {!token && (
                                <>
                                    <Link href="/login" className="text-foreground hover:text-ai-blue transition-colors">
                                        Login
                                    </Link>
                                    <Link href="/signup" className="text-foreground hover:text-ai-blue transition-colors">
                                        Sign Up
                                    </Link>
                                </>
                            )}
                        </div>
                    )}
                </nav>
            </div>
        </header>
    );
};

export default Header;
