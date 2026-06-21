import { api } from '$lib/server/api';

export async function load({ url, fetch }) {
    try {
        const tag = url.searchParams.get('tag');
        const search = url.searchParams.get('search');
        const page = url.searchParams.get('page') ?? '1';
        const count = url.searchParams.get('page_size') ?? '10';

        const params = new URLSearchParams();

        if (tag) params.set('tag', tag);
        if (search) params.set('search', search);

        params.set('page', page)
        params.set('page_size', count)

        const query = params.toString()
            ? `?${params.toString()}`
            : '';

        return {
            recipes: await api(`/recipes/${query}`, {}, fetch)
        };
    } catch (e) {
        console.error(e);

        return {
            recipes: {
                items: [],
                total: 0,
                page: 1,
                page_size: 10,
            },
            error: 'Could not load recipes.'
        };
    }
}