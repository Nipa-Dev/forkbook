<script>
  import { page } from "$app/state";
  import * as Card from "$lib/components/ui/card";
  import { Badge } from "$lib/components/ui/badge";
  import RecipeSearch from "$lib/components/RecipeSearch.svelte";
  import * as Pagination from "$lib/components/ui/pagination";
  let { data } = $props();

  const getIngredientCount = (recipe) => {
    return (
      recipe.components?.reduce(
        (sum, comp) => sum + (comp.ingredients?.length ?? 0),
        0,
      ) ?? 0
    );
  };
  
  const totalPages = $derived(Math.ceil(data.recipes.total / data.recipes.page_size));

  const buildPageUrl = (newPage) => {
    const params = new URLSearchParams(page.url.searchParams);
    params.set("page", newPage);
    return `?${params.toString()}`;
  };

  const pages = $derived.by(() =>
    Array.from({ length: totalPages }, (_, i) => i + 1)
  );

</script>


<div class="p-4 flex justify-between items-center">
  <RecipeSearch />
</div>

<div class="p-4 grid gap-3 grid-cols-2 sm:grid-cols-3 lg:grid-cols-4">
  {#each data.recipes.items as recipe (recipe.id)}
    <a
      href={`/recipes/${recipe.id}`}
      data-sveltekit-preload-data="tap"
      class="block h-full"
    >
      <Card.Root class="h-full overflow-hidden hover:shadow-md transition">
        {#if recipe.image_url}
          <img
            src={recipe.image_url}
            alt={recipe.title}
            class="w-full aspect-4/3 lg:aspect-video object-cover"
            loading="lazy"
          />
        {:else}
          <div
            class="w-full aspect-4/3 lg:aspect-video bg-muted flex items-center justify-center text-sm text-muted-foreground"
          >
            No image
          </div>
        {/if}

        <Card.Header>
          <Card.Title class="text-base line-clamp-2">
            {recipe.title}
          </Card.Title>

          {#if recipe.description}
            <p class="text-sm text-muted-foreground line-clamp-2">
              {recipe.description}
            </p>
          {/if}
        </Card.Header>

        <Card.Content class="space-y-1">
          <div class="flex flex-wrap gap-2 items-center">
            {#each recipe.tags ?? [] as tag}
              <Badge variant="secondary">{tag}</Badge>
            {/each}

            {#if recipe.difficulty}
              <Badge variant="outline" class="capitalize"
                >{recipe.difficulty}</Badge
              >
            {/if}
          </div>

          <div class="text-sm text-muted-foreground flex gap-3 flex-wrap">
            {#if recipe.time_minutes}
              <span>{recipe.time_minutes} min</span>
            {/if}

            <span>
              {getIngredientCount(recipe)} ingredients
            </span>
          </div>
        </Card.Content>
      </Card.Root>
    </a>
  {/each}
</div>
{#if totalPages > 1}
  <Pagination.Root class="py-6">
    <Pagination.Content>

      {#if data.recipes.page > 1}
        <Pagination.Item>
          <a
            href={buildPageUrl(data.recipes.page - 1)}
            class="inline-flex h-9 items-center rounded-md px-3 text-sm hover:bg-accent"
          >
            Previous
          </a>
        </Pagination.Item>
      {/if}

      {#each pages as pageNumber}
        <Pagination.Item>
          <a
            href={buildPageUrl(pageNumber)}
            class={`inline-flex h-9 w-9 items-center justify-center rounded-md text-sm ${
              pageNumber === data.recipes.page
                ? "border bg-background"
                : "hover:bg-accent"
            }`}
          >
            {pageNumber}
          </a>
        </Pagination.Item>
      {/each}

      {#if data.recipes.page < totalPages}
        <Pagination.Item>
          <a
            href={buildPageUrl(data.recipes.page + 1)}
            class="inline-flex h-9 items-center rounded-md px-3 text-sm hover:bg-accent"
          >
            Next
          </a>
        </Pagination.Item>
      {/if}

    </Pagination.Content>
  </Pagination.Root>
{/if}