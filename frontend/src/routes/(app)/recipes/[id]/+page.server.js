import { api } from "$lib/server/api";

export async function load({ params, url, fetch}) {
  const tag = url.searchParams.get("tag");
  const search = url.searchParams.get("search");
  const layout = url.searchParams.get("layout") || "A";

  const forwardParams = new URLSearchParams();
  if (tag) forwardParams.set("tag", tag);
  if (search) forwardParams.set("search", search);

  forwardParams.set("layout", layout);

  const queryString = forwardParams.toString()
    ? `?${forwardParams.toString()}`
    : "";

  const recipeData = await api(`/recipes/${params.id}${queryString}`, {}, fetch);

  return {
    recipe: recipeData,
    layout: layout,
  };
}
