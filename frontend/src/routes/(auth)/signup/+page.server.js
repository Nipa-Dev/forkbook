import { fail, redirect } from "@sveltejs/kit";
import { api } from "$lib/server/api.js";

export const actions = {
    signup: async ({ request, cookies, url }) => {
        const data = await request.formData();
        const username = data.get("username");
        const password = data.get("password");
        const passwordConfirm = data.get("password-confirm");
        const email = data.get("email");

        if (password !== passwordConfirm) {
            return fail(400, { message: "Passwords do not match" });
        }
        
        if (!username || !password || !email) {
            return fail(400, { message: "Email and password are required" });
        }

        try {
            const apiPayload = {
                    username: username.toString(),
                    email: email.toString(),
                    password: password.toString()
                };


            const registerResponse = await api("/auth/add-user", {
                method: "POST",
                headers: {
                    "content-type": "application/json",
                },
                body: JSON.stringify(apiPayload),
            });

            const tokenFormData = new URLSearchParams();
            tokenFormData.append("username", username.toString());
            tokenFormData.append("password", password.toString());
            const responseData = await api("/auth/token", {
                method: "POST",
                headers: {
                    "content-type": "application/x-www-form-urlencoded",
                },
                body: tokenFormData.toString(),
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
