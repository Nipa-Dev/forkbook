export async function load({ fetch, url }) {
  try {
    const tag = url.searchParams.get("tag");
    const search = url.searchParams.get("search");

    const params = new URLSearchParams();

    if (tag) params.set("tag", tag);
    if (search) params.set("search", search);

    const query = params.toString() ? `?${params.toString()}` : "";

    const res = await fetch(`/api/recipes/${query}`);

    if (!res.ok) {
      throw new Error(`Failed to fetch: ${res.status}`);
    }

    const recipes = await res.json();

    return { recipes };
  } catch (e) {
    console.error(e);
    return { recipes: [], error: "Could not load recipes." };
  }
}
