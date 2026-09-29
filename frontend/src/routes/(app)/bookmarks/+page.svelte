<script>
  import * as Card from '$lib/components/ui/card';
  import { Badge } from '$lib/components/ui/badge';
  import { Bookmark } from 'lucide-svelte';

  let { data } = $props();

  const recipes = $derived(data.recipes ?? []);

  const getImageUrl = (filename) => `/images/${filename}`;
</script>

<svelte:head>
  <title>Bookmarks</title>
</svelte:head>

<article class="max-w-6xl mx-auto px-6 py-8">
  <header class="mb-10">
    <div class="flex items-center gap-3 mb-3">
      <Bookmark size={20} class="text-primary" fill="currentColor" />

      <h1 class="text-3xl font-semibold tracking-tight">Bookmarks</h1>
    </div>

    <p class="text-muted-foreground">
      Your bookmarked recipes. You have {recipes.length} bookmarked recipes
    </p>
  </header>

  {#if recipes.length === 0}
    <section class="border rounded-xl px-6 py-16 text-center">
      <Bookmark size={28} class="mx-auto mb-4 text-muted-foreground" />

      <h2 class="text-lg font-semibold mb-2">Your cookbook is empty</h2>

      <p class="text-sm text-muted-foreground">Recipes you bookmark will appear here.</p>
    </section>
  {:else}
    <div class="grid gap-3 grid-cols-2 sm:grid-cols-3 lg:grid-cols-4">
      {#each recipes as recipe (recipe.id)}
        <a href={`/recipes/${recipe.id}`} data-sveltekit-preload-data="tap" class="block h-full">
          <Card.Root class="h-full overflow-hidden hover:shadow-md transition">
            {#if recipe.image_thumb_filename}
              <img
                src={getImageUrl(recipe.image_thumb_filename)}
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
                {#each recipe.tags ?? [] as tag (tag)}
                  <Badge variant="secondary">
                    {tag}
                  </Badge>
                {/each}

                {#if recipe.difficulty}
                  <Badge variant="outline" class="capitalize">
                    {recipe.difficulty}
                  </Badge>
                {/if}
              </div>

              <div class="text-sm text-muted-foreground flex gap-3 flex-wrap">
                {#if recipe.cook_time_minutes}
                  <span>
                    {recipe.cook_time_minutes} min
                  </span>
                {/if}

                <span> </span>
              </div>
            </Card.Content>
          </Card.Root>
        </a>
      {/each}
    </div>
  {/if}
</article>
