import { fail, redirect } from '@sveltejs/kit';
import { api } from '$lib/server/api.js';

export const actions = {
  signup: async ({ request, cookies, url }) => {
    const data = await request.formData();
    const username = data.get('username');
    const password = data.get('password');
    const passwordConfirm = data.get('password-confirm');
    const email = data.get('email');

    if (!username || !email || !password || !passwordConfirm) {
      return fail(400, {
        message: 'All fields are required',
        values: { username, email }
      });
    }

    if (password !== passwordConfirm) {
      return fail(400, {
        message: 'Passwords do not match',
        values: { username, email }
      });
    }

    try {
      const apiPayload = {
        username: username.toString(),
        email: email.toString(),
        password: password.toString()
      };

      await api('/auth/add-user', {
        method: 'POST',
        headers: {
          'content-type': 'application/json'
        },
        body: JSON.stringify(apiPayload)
      });

      const tokenFormData = new URLSearchParams();
      tokenFormData.append('username', username.toString());
      tokenFormData.append('password', password.toString());
      const responseData = await api('/auth/token', {
        method: 'POST',
        headers: {
          'content-type': 'application/x-www-form-urlencoded'
        },
        body: tokenFormData.toString()
      });
      const { access_token } = responseData;

      cookies.set('session_token', access_token, {
        path: '/',
        httpOnly: true,
        sameSite: 'lax',
        secure: process.env.NODE_ENV === 'production',
        maxAge: 60 * 60 * 24
      });
    } catch (err) {
      if (err.status === 409 || err.message?.includes('409')) {
        return fail(409, {
          message: 'Username or email is already taken.',
          values: { username, email }
        });
      }
      console.error('Signup system error:', err);
      return fail(500, { message: 'Internal server error. Try again later.' });
    }

    const redirectTo = url.searchParams.get('redirectTo') || '/';
    redirect(303, redirectTo);
  }
};
