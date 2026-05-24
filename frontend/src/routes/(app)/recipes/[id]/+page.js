export async function load({ params, fetch, url }) {
  const res = await fetch(`/api/recipes/${params.id}`);

  if (!res.ok) {
    throw new Error("Failed to load recipe");
  }

  const recipe = await res.json();

  const layoutParam = url.searchParams.get("layout");

  return {
    recipe,
    layout: layoutParam?.toUpperCase() ?? "A",
  };
}
