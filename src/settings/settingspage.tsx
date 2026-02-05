import { GlassCard } from "@/components/ui/glass-card";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Globe, Mic, Wifi, Eye, Moon, Monitor } from "lucide-react";

export default function SettingsPage() {
    return (
        <div className="max-w-4xl space-y-8">
            <div>
                <h1 className="text-3xl font-bold">Settings</h1>
                <p className="text-muted-foreground">Manage your preferences and accessibility options.</p>
            </div>

            <div className="grid gap-6">
                {/* General Preferences */}
                <section className="space-y-4">
                    <h2 className="text-xl font-semibold">General</h2>
                    <GlassCard className="space-y-6 p-6" gradient={false}>
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-4">
                                <div className="p-2 bg-blue-500/10 rounded-lg text-blue-400">
                                    <Globe className="h-5 w-5" />
                                </div>
                                <div>
                                    <p className="font-medium">Language</p>
                                    <p className="text-sm text-muted-foreground">Select your learning language</p>
                                </div>
                            </div>
                            <Button variant="outline" className="w-[140px]">English (US)</Button>
                        </div>

                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-4">
                                <div className="p-2 bg-purple-500/10 rounded-lg text-purple-400">
                                    <Wifi className="h-5 w-5" />
                                </div>
                                <div>
                                    <p className="font-medium">Offline Mode</p>
                                    <p className="text-sm text-muted-foreground">Cache lessons for offline access</p>
                                </div>
                            </div>
                            <Switch />
                        </div>
                    </GlassCard>
                </section>

                {/* Accessibility from Prompt */}
                <section className="space-y-4">
                    <h2 className="text-xl font-semibold">Accessibility & Appearance</h2>
                    <GlassCard className="space-y-6 p-6" gradient={false}>
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-4">
                                <div className="p-2 bg-pink-500/10 rounded-lg text-pink-400">
                                    <Mic className="h-5 w-5" />
                                </div>
                                <div>
                                    <p className="font-medium">Text-to-Speech</p>
                                    <p className="text-sm text-muted-foreground">Read lesson content aloud</p>
                                </div>
                            </div>
                            <Switch />
                        </div>

                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-4">
                                <div className="p-2 bg-green-500/10 rounded-lg text-green-400">
                                    <Eye className="h-5 w-5" />
                                </div>
                                <div>
                                    <p className="font-medium">High Contrast Mode</p>
                                    <p className="text-sm text-muted-foreground">Increase visibility for better readability</p>
                                </div>
                            </div>
                            <Switch />
                        </div>

                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-4">
                                <div className="p-2 bg-yellow-500/10 rounded-lg text-yellow-400">
                                    <Monitor className="h-5 w-5" />
                                </div>
                                <div>
                                    <p className="font-medium">Dyslexia Friendly Font</p>
                                    <p className="text-sm text-muted-foreground">Use OpenDyslexic or similar fonts</p>
                                </div>
                            </div>
                            <Switch />
                        </div>
                    </GlassCard>
                </section>
            </div>
        </div>
    );
}
