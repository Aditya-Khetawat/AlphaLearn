"use client";

import { useState, useEffect, useMemo } from "react";
import { Settings, User, Bell } from "lucide-react";

import { MainLayout } from "@/components/layout/main-layout";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { useApp } from "@/context/app-context";

export default function SettingsPage() {
  const { user, portfolio } = useApp();
  const [activeTab, setActiveTab] = useState("account");

  // Memoize user balance to prevent flickering - consistent with main layout
  const userBalance = useMemo(() => {
    // Priority: portfolio cash > user balance > default 100000
    if (portfolio?.cash !== undefined && portfolio.cash !== null) {
      return portfolio.cash;
    }
    return user?.balance ?? 100000;
  }, [user?.balance, portfolio?.cash]);

  // Form states - use memoized values to prevent flickering
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");

  // Memoized form values to prevent unnecessary updates
  const memoizedUserName = useMemo(() => user?.name || "", [user?.name]);
  const memoizedUserEmail = useMemo(() => user?.email || "", [user?.email]);

  // Update form fields when user data loads - only when values actually change
  useEffect(() => {
    if (memoizedUserName && fullName !== memoizedUserName) {
      setFullName(memoizedUserName);
    }
  }, [memoizedUserName, fullName]);

  useEffect(() => {
    if (memoizedUserEmail && email !== memoizedUserEmail) {
      setEmail(memoizedUserEmail);
    }
  }, [memoizedUserEmail, email]);

  // Memoized avatar initials to prevent recalculation
  const avatarInitials = useMemo(() => {
    if (!user?.name) return "U";
    return user.name
      .split(" ")
      .map((n: string) => n[0])
      .join("")
      .toUpperCase();
  }, [user?.name]);

  // Notification settings
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [pushNotifications, setPushNotifications] = useState(true);
  const [marketAlerts, setMarketAlerts] = useState(false);
  const [portfolioUpdates, setPortfolioUpdates] = useState(true);

  const handleSaveAccount = () => {
    // TODO: Implement account save functionality
    console.log("Saving account settings:", { fullName, email });
  };

  const handleSaveNotifications = () => {
    // TODO: Implement notification save functionality
    console.log("Saving notification settings:", {
      emailNotifications,
      pushNotifications,
      marketAlerts,
      portfolioUpdates,
    });
  };

  return (
    <MainLayout>
      <div className="container mx-auto p-6 max-w-4xl">
        <div className="flex items-center gap-2 mb-6">
          <Settings className="h-6 w-6" />
          <h1 className="text-3xl font-bold">Settings</h1>
        </div>

        <Tabs
          value={activeTab}
          onValueChange={setActiveTab}
          className="space-y-6"
        >
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="account" className="flex items-center gap-2">
              <User className="h-4 w-4" />
              Account
            </TabsTrigger>
            <TabsTrigger
              value="notifications"
              className="flex items-center gap-2"
            >
              <Bell className="h-4 w-4" />
              Notifications
            </TabsTrigger>
          </TabsList>

          <TabsContent value="account" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Profile Information</CardTitle>
                <CardDescription>
                  Update your account details and profile information.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex flex-col md:flex-row gap-6 items-start">
                  <div className="flex flex-col items-center gap-2">
                    <Avatar className="h-24 w-24">
                      <AvatarImage src={user?.avatarUrl || ""} />
                      <AvatarFallback className="text-lg">
                        {avatarInitials}
                      </AvatarFallback>
                    </Avatar>
                    <Button variant="outline" size="sm">
                      Change Avatar
                    </Button>
                  </div>

                  <div className="flex-1 space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="full-name">Full Name</Label>
                        <Input
                          id="full-name"
                          value={fullName}
                          onChange={(e) => setFullName(e.target.value)}
                          placeholder="Enter your full name"
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="email">Email</Label>
                        <Input
                          id="email"
                          type="email"
                          value={email}
                          onChange={(e) => setEmail(e.target.value)}
                          placeholder="Enter your email"
                        />
                      </div>
                    </div>
                  </div>
                </div>

                <div className="flex justify-end">
                  <Button onClick={handleSaveAccount}>Save Changes</Button>
                </div>
              </CardContent>
            </Card>

            {user && (
              <Card>
                <CardHeader>
                  <CardTitle>Account Balance</CardTitle>
                  <CardDescription>
                    Your current trading balance.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-green-600">
                    ₹{userBalance.toLocaleString()}
                  </div>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          <TabsContent value="notifications" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Notification Preferences</CardTitle>
                <CardDescription>
                  Manage how you receive notifications and alerts.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Email Notifications</Label>
                      <p className="text-sm text-muted-foreground">
                        Receive notifications via email
                      </p>
                    </div>
                    <Switch
                      checked={emailNotifications}
                      onCheckedChange={setEmailNotifications}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Push Notifications</Label>
                      <p className="text-sm text-muted-foreground">
                        Receive push notifications in your browser
                      </p>
                    </div>
                    <Switch
                      checked={pushNotifications}
                      onCheckedChange={setPushNotifications}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Market Alerts</Label>
                      <p className="text-sm text-muted-foreground">
                        Get alerts for significant market movements
                      </p>
                    </div>
                    <Switch
                      checked={marketAlerts}
                      onCheckedChange={setMarketAlerts}
                    />
                  </div>

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Portfolio Updates</Label>
                      <p className="text-sm text-muted-foreground">
                        Receive updates about your portfolio performance
                      </p>
                    </div>
                    <Switch
                      checked={portfolioUpdates}
                      onCheckedChange={setPortfolioUpdates}
                    />
                  </div>
                </div>

                <div className="flex justify-end">
                  <Button onClick={handleSaveNotifications}>
                    Save Preferences
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </MainLayout>
  );
}
