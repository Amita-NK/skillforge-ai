import { AIChat, Visualizer } from "@/components/student/LessonComponents";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { ChevronLeft } from "lucide-react";
import Link from "next/link";

export default function LessonPage({ params }: { params: { id: string } }) {
    return (
        <div className="flex h-[calc(100vh-6rem)] flex-col gap-4">
            {/* Header */}
            <div className="flex items-center justify-between border-b border-white/5 pb-4">
                <div className="flex items-center gap-4">
                    <Link href="/learn">
                        <Button variant="ghost" size="icon">
                            <ChevronLeft className="h-5 w-5" />
                        </Button>
                    </Link>
                    <div>
                        <h1 className="text-lg font-bold">Module: {params.id}</h1>
                        <p className="text-xs text-muted-foreground">Interactive Session</p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    {/* Mode Toggles could go here */}
                </div>
            </div>

            {/* Split Interface */}
            <div className="grid h-full flex-1 gap-4 lg:grid-cols-2">
                {/* Left: Chat / Theory */}
                <div className="flex h-full flex-col overflow-hidden rounded-xl border border-white/10 bg-black/20 backdrop-blur-sm">
                    <Tabs defaultValue="chat" className="flex h-full flex-col">
                        <div className="border-b border-white/5 px-4 pt-2">
                            <TabsList className="bg-transparent">
                                <TabsTrigger value="chat">AI Tutor</TabsTrigger>
                                <TabsTrigger value="notes">Notes</TabsTrigger>
                                <TabsTrigger value="quiz">Quiz</TabsTrigger>
                            </TabsList>
                        </div>
                        <TabsContent value="chat" className="mt-0 flex-1 overflow-hidden">
                            <AIChat />
                        </TabsContent>
                        <TabsContent value="notes" className="p-4">
                            <p className="text-muted-foreground">Smart notes will appear here.</p>
                        </TabsContent>
                    </Tabs>
                </div>

                {/* Right: Visuals / Code */}
                <div className="flex h-full flex-col overflow-hidden rounded-xl border border-white/10 bg-black/20 backdrop-blur-sm">
                    <Tabs defaultValue="visual" className="flex h-full flex-col">
                        <div className="border-b border-white/5 px-4 pt-2">
                            <TabsList className="bg-transparent">
                                <TabsTrigger value="visual">Visualizer</TabsTrigger>
                                <TabsTrigger value="code">Code Lab</TabsTrigger>
                            </TabsList>
                        </div>
                        <TabsContent value="visual" className="mt-0 flex-1">
                            <Visualizer />
                        </TabsContent>
                        <TabsContent value="code" className="mt-0 flex-1 p-4">
                            <textarea className="h-full w-full resize-none rounded-lg bg-black/50 p-4 font-mono text-sm outline-none" placeholder="// Write code here..." />
                        </TabsContent>
                    </Tabs>
                </div>
            </div>
        </div>
    );
}
