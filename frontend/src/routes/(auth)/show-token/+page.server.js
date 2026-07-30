import { redirect } from '@sveltejs/kit';

export const load = async ({ cookies }) => {
  const token = cookies.get('session_token');

  if (!token) {
    redirect(303, '/login');
  }

  return {
    token
  };
};
