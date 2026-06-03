import { redirect } from "@sveltejs/kit";
import { api } from "$lib/server/api.js";

export async function handle({ event, resolve }) {
    const token = event.cookies.get("session_token");

    const isLoginPage = event.url.pathname === "/login";
    const isAuthApi = event.url.pathname.startsWith("/auth");

    // Don't intercept form submissions hitting the login endpoint
    if (isLoginPage && event.request.method === "POST") {
        return resolve(event);
    }

    let isValid = false;

    if (token) {
        try {
            // If this succeeds, user data is returned directly
            const userData = await api("/auth/users/me", {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });

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

    if (!isValid && !isLoginPage && !isAuthApi) {
        const fromUrl = event.url.pathname + event.url.search;
        throw redirect(303, `/login?redirectTo=${encodeURIComponent(fromUrl)}`);
    }

    if (isValid && isLoginPage) {
        throw redirect(303, "/");
    }

    return resolve(event);
}
