import { fail, redirect } from "@sveltejs/kit";
import { api } from "$lib/server/api.js";

export const actions = {
    login: async ({ request, cookies, url }) => {
        const data = await request.formData();
        const username = data.get("username");
        const password = data.get("password");

        if (!username || !password) {
            return fail(400, { message: "Email and password are required" });
        }

        try {
            const apiFormData = new URLSearchParams();
            apiFormData.append("username", username.toString());
            apiFormData.append("password", password.toString());

            const responseData = await api("/auth/token", {
                method: "POST",
                headers: {
                    "content-type": "application/x-www-form-urlencoded",
                },
                body: apiFormData.toString(),
            });
            const { access_token } = responseData;

            cookies.set("session_token", access_token, {
                path: "/",
                httpOnly: true,
                sameSite: "lax",
                secure: process.env.NODE_ENV === "production",
                maxAge: 60 * 60 * 24,
            });
        } catch (err) {
            if (err.message?.includes("401")) {
                return fail(401, { message: "Invalid email or password." });
            }

            console.error("Login system error:", err);
            return fail(500, { message: "Internal server error. Try again later." });
        }

        const redirectTo = url.searchParams.get("redirectTo") || "/";
        throw redirect(303, redirectTo);
    },
}
