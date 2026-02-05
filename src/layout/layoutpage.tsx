import { AppSidebar } from "@/components/layout/AppSidebar";
import { AppHeader } from "@/components/layout/AppHeader";

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="min-h-screen bg-background text-foreground">
            <AppSidebar />
            <div className="pl-64 transition-all">
                <AppHeader />
                <main className="p-6">
                    {children}
                </main>
            </div>
        </div>
    );
}
