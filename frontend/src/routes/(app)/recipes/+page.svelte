<script>
  import * as Card from "$lib/components/ui/card";
  import { Badge } from "$lib/components/ui/badge";
  import RecipeSearch from "$lib/components/RecipeSearch.svelte";

  let { data } = $props();

  // Helper to sum ingredients across all components
  const getIngredientCount = (recipe) => {
    return (
      recipe.components?.reduce(
        (sum, comp) => sum + (comp.ingredients?.length ?? 0),
        0,
      ) ?? 0
    );
  };
</script>

<!--
<div class="absolute right-4 top-4">
  <ModeToggle />
</div> -->

<div class="p-4 flex justify-between items-center">
  <RecipeSearch />
</div>

<div class="p-4 grid gap-3 grid-cols-2 sm:grid-cols-3 lg:grid-cols-4">
  {#each data.recipes as recipe (recipe.id)}
    <a href={`/recipes/${recipe.id}`} class="block h-full">
      <Card.Root class="h-full overflow-hidden hover:shadow-md transition">
        {#if recipe.image_url}
          <img
            src={recipe.image_url}
            alt={recipe.title}
            class="w-full aspect-4/3 max-h-40 object-cover"
            loading="lazy"
          />
        {:else}
          <div
            class="w-full aspect-4/3 max-h-40 bg-muted flex items-center justify-center text-sm text-muted-foreground"
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
