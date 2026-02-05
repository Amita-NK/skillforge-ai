import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { GlassCard } from "@/components/ui/glass-card";
import { GradientText } from "@/components/ui/gradient-text";
import { Sparkles } from "lucide-react";

export default function SignupPage() {
    return (
        <GlassCard className="p-8">
            <div className="mb-6 flex flex-col items-center space-y-2 text-center">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/20">
                    <Sparkles className="h-6 w-6 text-primary" />
                </div>
                <h1 className="text-2xl font-bold tracking-tight">
                    Create an account
                </h1>
                <p className="text-sm text-muted-foreground">
                    Start your adaptive learning journey today
                </p>
            </div>

            <div className="grid gap-6">
                <form>
                    <div className="grid gap-4">
                        <div className="grid gap-2">
                            <Label htmlFor="email">Email</Label>
                            <Input
                                id="email"
                                placeholder="name@example.com"
                                type="email"
                                autoCapitalize="none"
                                autoComplete="email"
                                autoCorrect="off"
                                className="bg-transparent"
                            />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="password">Password</Label>
                            <Input
                                id="password"
                                type="password"
                                className="bg-transparent"
                            />
                        </div>
                        <Link href="/dashboard">
                            <Button className="w-full bg-primary hover:bg-primary/90 mt-2">
                                Create Account
                            </Button>
                        </Link>
                    </div>
                </form>

                <div className="mt-4 text-center text-sm">
                    Already have an account?{" "}
                    <Link href="/auth/login" className="underline font-bold text-primary">
                        Sign in
                    </Link>
                </div>
            </div>
        </GlassCard>
    );
}
