import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { GlassCard } from "@/components/ui/glass-card";
import { GradientText } from "@/components/ui/gradient-text";
import { Sparkles } from "lucide-react";

export default function LoginPage() {
    return (
        <GlassCard className="p-8">
            <div className="mb-6 flex flex-col items-center space-y-2 text-center">
                <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/20">
                    <Sparkles className="h-6 w-6 text-primary" />
                </div>
                <h1 className="text-2xl font-bold tracking-tight">
                    Welcome back to <GradientText>SkillForge</GradientText>
                </h1>
                <p className="text-sm text-muted-foreground">
                    Enter your email to sign in to your account
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
                            <div className="flex items-center justify-between">
                                <Label htmlFor="password">Password</Label>
                                <Link href="#" className="ml-auto inline-block text-sm underline-offset-4 hover:underline">
                                    Forgot your password?
                                </Link>
                            </div>
                            <Input
                                id="password"
                                type="password"
                                className="bg-transparent"
                            />
                        </div>
                        <Link href="/dashboard">
                            <Button className="w-full bg-primary hover:bg-primary/90 mt-2">
                                Sign In with Email
                            </Button>
                        </Link>
                    </div>
                </form>

                <div className="relative">
                    <div className="absolute inset-0 flex items-center">
                        <span className="w-full border-t border-white/10" />
                    </div>
                    <div className="relative flex justify-center text-xs uppercase">
                        <span className="bg-background px-2 text-muted-foreground">
                            Or continue with
                        </span>
                    </div>
                </div>

                <Button variant="outline" className="w-full bg-white/5 hover:bg-white/10">
                    GitHub
                </Button>
                <div className="mt-4 text-center text-sm">
                    Don&apos;t have an account?{" "}
                    <Link href="/auth/signup" className="underline font-bold text-primary">
                        Sign up
                    </Link>
                </div>
            </div>
        </GlassCard>
    );
}
