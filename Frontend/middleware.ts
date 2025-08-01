import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

// This middleware handles authentication routing
export function middleware(request: NextRequest) {
  // Check if the user is authenticated
  const token = request.cookies.get("alphalearn_token")?.value;
  const isAuthenticated = !!token;

  // Define auth pages and protected pages
  const isAuthPage =
    request.nextUrl.pathname === "/login" ||
    request.nextUrl.pathname === "/register";

  const isProtectedPage =
    request.nextUrl.pathname === "/portfolio" ||
    request.nextUrl.pathname === "/trade" ||
    request.nextUrl.pathname === "/settings";

  // Redirect logged-in users away from auth pages
  if (isAuthPage && isAuthenticated) {
    return NextResponse.redirect(new URL("/", request.url));
  }

  // Redirect unauthenticated users to login when trying to access protected pages
  if (isProtectedPage && !isAuthenticated) {
    const url = new URL("/login", request.url);
    url.searchParams.set("redirect", request.nextUrl.pathname);
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}

// Configure the middleware to run on specific paths
export const config = {
  matcher: ["/portfolio", "/trade", "/settings", "/login", "/register"],
};
