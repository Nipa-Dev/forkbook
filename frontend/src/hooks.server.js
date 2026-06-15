import { redirect } from "@sveltejs/kit";
import { api } from "$lib/server/api.js";

export async function handle({ event, resolve }) {
    const { fetch, cookies, url, request } = event
    const token = event.cookies.get("session_token");

    const { pathname, search } = event.url;

    const isAuthPage = pathname === "/login" || pathname.startsWith("/signup");
    const isApiRoute = pathname.startsWith("/api") || pathname.startsWith("/auth");


    let isValid = false;

    if (token) {
        try {
            // If this succeeds, user data is returned directly
            const userData = await api("/auth/users/me", {
                headers: {
                    Authorization: `Bearer ${token}`,
                }, fetch});

            event.locals.user = userData;
            isValid = true;

        } catch (err) {
            const errorMessage = err.message || "";

            if (errorMessage.includes("401") || errorMessage.includes("403")) {
                // Token is invalid -> wipe it
                event.cookies.delete("session_token", { path: "/" });
                isValid = false;
            } else {
                // Catch-all for 500s or network drops: let the user keep their
                // cookie but flag the session as degraded so components can adapt.
                console.warn("Backend error or offline. Degrading session state:", err);
                isValid = true;
                event.locals.user = { isDegradedSession: true };
            }
        }
    }

    if (isApiRoute) {
        if (!isValid && !pathname.startsWith("/auth")) {
            return new Response(JSON.stringify({ error: "Unauthorized" }), {
                status: 401,
                headers: { "Content-Type": "application/json" }
            });
        }
        return resolve(event);
    }

    if (!isValid && !isAuthPage) {
        const fromUrl = pathname + search;
        throw redirect(303, `/login?redirectTo=${encodeURIComponent(fromUrl)}`);
    }

    if (isValid && isAuthPage) {
        // If they just submitted a form, let it process, otherwise redirect
        if (event.request.method !== "POST") {
            throw redirect(303, "/");
        }
    }

    return resolve(event);
}
