<script>
  import * as Card from '$lib/components/ui/card';
  import { Badge } from '$lib/components/ui/badge';
  import { Bookmark } from 'lucide-svelte';
  import { BookOpen, Utensils } from 'lucide-svelte';

  let { data } = $props();

  const recipes = $derived(data.recipes ?? []);

  const getImageUrl = (filename) => `/images/${filename}`;
</script>

<svelte:head>
  <title>Cookbook</title>
</svelte:head>

<article class="max-w-6xl mx-auto px-6 py-8">
  <header class="mb-8 p-6 rounded-2xl bg-amber-500/10 border border-amber-500/20">
    <div class="flex items-center gap-3">
      <div class="p-2.5 rounded-xl bg-amber-500 text-white shadow-xs">
        <BookOpen size={24} />
      </div>
      <div>
        <h1 class="text-3xl font-bold tracking-tight">My Cookbook</h1>
        <p class="text-sm text-muted-foreground mt-0.5">
          Your personal recipe collection ({recipes.length}
          {recipes.length === 1 ? 'recipe' : 'recipes'})
        </p>
      </div>
    </div>
  </header>

  {#if recipes.length === 0}
    <section class="border border-amber-500/20 rounded-2xl px-6 py-16 text-center bg-amber-500/5">
      <Utensils size={32} class="mx-auto mb-4 text-amber-500/60" />
      <h2 class="text-lg font-semibold mb-1">Your cookbook is empty</h2>
      <p class="text-sm text-muted-foreground max-w-sm mx-auto">
        Recipes you add will be stored here.
      </p>
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
