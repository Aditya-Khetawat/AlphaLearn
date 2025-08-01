"use client";

import {
  TrendingUp,
  BarChart3,
  Users,
  BookOpen,
  Home,
  Settings,
} from "lucide-react";
import { usePathname } from "next/navigation";

// Shared navigation items
export const navItems = [
  { title: "Dashboard", icon: Home, href: "/" },
  { title: "Trade", icon: TrendingUp, href: "/trade" },
  { title: "Portfolio", icon: BarChart3, href: "/portfolio" },
  { title: "Leaderboard", icon: Users, href: "/leaderboard" },
  { title: "Learn", icon: BookOpen, href: "/learn" },
  { title: "Settings", icon: Settings, href: "/settings" },
];

export const useNavigation = () => {
  const pathname = usePathname();

  // Check if a nav item is active based on the current path
  const isActive = (href: string) => {
    if (href === "/" && pathname === "/") return true;
    if (href !== "/" && pathname.startsWith(href)) return true;
    return false;
  };

  return { navItems, isActive };
};
