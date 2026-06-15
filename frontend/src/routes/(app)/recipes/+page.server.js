import { api } from '$lib/server/api';

export async function load({ url, fetch }) {
    try {
        const tag = url.searchParams.get('tag');
        const search = url.searchParams.get('search');

        const params = new URLSearchParams();

        if (tag) params.set('tag', tag);
        if (search) params.set('search', search);

        const query = params.toString()
            ? `?${params.toString()}`
            : '';

        return {
            recipes: await api(`/recipes/${query}`, {}, fetch)
        };
    } catch (e) {
        console.error(e);

        return {
            recipes: [],
            error: 'Could not load recipes.'
        };
    }
}