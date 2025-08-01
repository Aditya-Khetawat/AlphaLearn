"use client";

import React, { ReactNode, useState, useEffect, useMemo } from "react";
import {
  Moon,
  Sun,
  ChevronDown,
  Activity,
  Settings,
  LogOut,
  User,
} from "lucide-react";
import { useTheme } from "next-themes";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useApp } from "@/context/app-context";

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { SimpleSwitch } from "@/components/ui/simple-switch";
import { navItems, useNavigation } from "@/components/layout/navigation";

interface LayoutProps {
  children: ReactNode;
}

export function MainLayout({ children }: LayoutProps) {
  const { theme, setTheme, resolvedTheme } = useTheme();
  const { isActive } = useNavigation();
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [mounted, setMounted] = useState(false);
  const router = useRouter();
  const { user, logout, isLoading, portfolio } = useApp();

  // Handle hydration mismatch with next-themes
  useEffect(() => {
    setMounted(true);
  }, []);

  // Simplified theme state
  const isDarkMode = resolvedTheme === "dark";

  // Basic theme toggle function
  function handleThemeToggle(checked: boolean) {
    setTheme(checked ? "dark" : "light");
  }

  // Handle logout
  function handleLogout() {
    logout();
    router.push("/login");
  }

  // Memoize user balance to prevent flickering - use portfolio cash if available, otherwise user balance
  const userBalance = useMemo(() => {
    // Priority: portfolio cash > user balance > default 100000
    if (portfolio?.cash !== undefined && portfolio.cash !== null) {
      return portfolio.cash;
    }
    return user?.balance ?? 100000;
  }, [user?.balance, portfolio?.cash]);

  return (
    <SidebarProvider>
      <div className="grid min-h-screen w-full md:grid-cols-[auto_1fr]">
        <Sidebar className="hidden border-r bg-background md:block">
          <SidebarHeader className="flex h-16 items-center border-b px-3">
            <Link
              href="/"
              className="flex items-center gap-2 font-semibold py-2.5 pl-0.5"
            >
              <Activity className="h-5 w-5 text-blue-500" />
              <span>AlphaLearn</span>
            </Link>
          </SidebarHeader>
          <SidebarContent className="px-3 py-2">
            <SidebarMenu className="space-y-1.5">
              {navItems.map((item) => (
                <SidebarMenuItem
                  key={item.href}
                  className={isActive(item.href) ? "bg-accent/70" : ""}
                >
                  <Link
                    href={item.href}
                    className="flex items-center gap-3 px-3.5 py-2 rounded-md hover:bg-accent/50 w-full transition-colors"
                  >
                    <item.icon className="h-4 w-4" />
                    {item.title}
                  </Link>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarContent>
        </Sidebar>
        <div className="flex flex-col">
          <header className="flex h-16 items-center border-b px-6">
            <div className="w-full flex justify-between items-center">
              {/* Mobile sidebar trigger */}
              <div className="md:hidden">
                <SidebarTrigger>
                  <Button variant="outline" size="icon">
                    <Activity className="h-5 w-5" />
                  </Button>
                </SidebarTrigger>
              </div>

              <div className="ml-auto flex items-center gap-4">
                {/* Theme toggle */}
                <div className="flex items-center space-x-2">
                  <Sun className="h-4 w-4" />
                  {/* Conditional rendering based on mounted state */}
                  {mounted ? (
                    <SimpleSwitch
                      checked={isDarkMode}
                      onCheckedChange={handleThemeToggle}
                    />
                  ) : (
                    <button
                      className="w-11 h-6 bg-gray-200 rounded-full p-1"
                      aria-label="Loading theme toggle"
                      disabled
                    >
                      <div className="w-4 h-4 bg-white rounded-full" />
                    </button>
                  )}
                  <Moon className="h-4 w-4" />
                </div>

                {/* User dropdown or login button */}
                {user ? (
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button
                        variant="ghost"
                        className="relative flex items-center gap-2 rounded-full px-2"
                      >
                        <Avatar className="h-8 w-8">
                          <AvatarImage src={user?.avatarUrl || ""} />
                          <AvatarFallback>
                            {user?.name
                              ? user.name
                                  .split(" ")
                                  .map((n: string) => n[0])
                                  .join("")
                                  .toUpperCase()
                              : "U"}
                          </AvatarFallback>
                        </Avatar>
                        <span className="hidden md:inline-block">
                          {user?.name || "User"}
                        </span>
                        <ChevronDown className="ml-auto h-4 w-4 opacity-50" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end" className="w-56">
                      <DropdownMenuLabel>
                        <div className="flex flex-col space-y-1">
                          <p className="text-sm font-medium leading-none">
                            {user?.name || "User"}
                          </p>
                          <p className="text-xs leading-none text-muted-foreground">
                            {user?.email || "Loading..."}
                          </p>
                          <p className="text-xs leading-none text-green-600 font-medium">
                            Balance: ₹{userBalance.toLocaleString()}
                          </p>
                        </div>
                      </DropdownMenuLabel>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem asChild>
                        <Link
                          href="/settings"
                          className="flex items-center w-full"
                        >
                          <Settings className="mr-2 h-4 w-4" />
                          <span>Settings</span>
                        </Link>
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        className="text-red-500 cursor-pointer"
                        onClick={handleLogout}
                      >
                        <LogOut className="mr-2 h-4 w-4" />
                        <span>Log out</span>
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                ) : (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => router.push("/login")}
                  >
                    <User className="mr-2 h-4 w-4" />
                    Log in
                  </Button>
                )}
              </div>
            </div>
          </header>

          {/* Mobile sidebar */}
          <SidebarContent className="fixed inset-y-0 left-0 z-50 flex w-3/4 flex-col bg-background md:hidden">
            <SidebarHeader className="flex h-16 items-center border-b px-3">
              <Link
                href="/"
                className="flex items-center gap-2 font-semibold py-2.5 pl-0.5"
              >
                <Activity className="h-5 w-5 text-blue-500" />
                <span>AlphaLearn</span>
              </Link>
              <SidebarTrigger className="ml-auto">
                <Button variant="ghost" size="icon">
                  <ChevronDown className="h-4 w-4" />
                </Button>
              </SidebarTrigger>
            </SidebarHeader>
            <SidebarMenu className="px-3 py-2 space-y-1.5">
              {navItems.map((item) => (
                <SidebarMenuItem
                  key={item.href}
                  className={isActive(item.href) ? "bg-accent/70" : ""}
                >
                  <Link
                    href={item.href}
                    className="flex items-center gap-3 px-3.5 py-2 rounded-md hover:bg-accent/50 w-full transition-colors"
                  >
                    <item.icon className="h-4 w-4" />
                    {item.title}
                  </Link>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarContent>

          <main className="flex-1 p-6">{children}</main>
        </div>
      </div>
    </SidebarProvider>
  );
}
