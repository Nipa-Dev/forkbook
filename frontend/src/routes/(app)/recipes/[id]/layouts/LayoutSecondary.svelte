<script>
  import { enhance } from '$app/forms';
  import { invalidateAll } from '$app/navigation';
  import { Badge } from '$lib/components/ui/badge';
  import { Star } from 'lucide-svelte';
  let { recipe } = $props();
  const isMain = (name) => name === 'Main' || name === 'Component: Main';

  let userRating = $state(0);
  let hoverRating = $state(0);

  $effect(() => {
    userRating = Math.round(recipe.average_rating ?? 0);
  });
</script>

<article class="max-w-6xl mx-auto px-6 py-8">
  <div class="grid grid-cols-1 lg:grid-cols-[400px_1fr] gap-16 items-start">
    <aside class="space-y-8">
      {#if recipe.image_url}
        <div class="rounded-xl overflow-hidden shadow-sm border">
          <img src={recipe.image_url} alt={recipe.title} class="w-full aspect-4/3 object-cover" />
        </div>
      {/if}
      <div class="pt-4 border-t space-y-4">
        <div class="flex items-center gap-8">
          <div class="flex flex-col">
            <span class="text-[10px] uppercase font-bold tracking-tighter text-muted-foreground"
              >Cook Time</span
            >
            <span class="text-sm font-medium">{recipe.cook_time_minutes} min</span>
          </div>
          <div class="flex flex-col">
            <span class="text-[10px] uppercase font-bold tracking-tighter text-muted-foreground"
              >Prep Time</span
            >
            <span class="text-sm font-medium">{recipe.prep_time_minutes ?? 0} min</span>
          </div>
        </div>
        {#if recipe.tags?.length > 0}
          <div class="flex flex-wrap gap-2 pt-1">
            {#each recipe.tags as tag}
              <Badge variant="secondary" class="text-xs font-normal px-2.5 py-0.5 rounded-md">
                {tag}
              </Badge>
            {/each}
          </div>
        {/if}

        <form method="POST" action="?/rateRecipe" use:enhance class="flex items-center gap-1 py-2">
          <input type="hidden" name="recipeId" value={recipe.id} />
          <div
            class="flex text-primary"
            onmouseleave={() => (hoverRating = 0)}
            role="group"
            aria-label="Rate this recipe"
          >
            {#each Array(5) as _, i}
              {@const starValue = i + 1}
              <button
                type="submit"
                name="rating"
                value={i + 1}
                class="focus:outline-none transition-transform active:scale-95"
                onmouseenter={() => (hoverRating = i + 1)}
                aria-label="Rate {starValue} out of 5 stars"
              >
                <Star
                  size={16}
                  fill={(hoverRating || userRating) >= starValue ? 'currentColor' : 'none'}
                />
              </button>
            {/each}
          </div>
          <span class="ml-2 text-xs font-medium text-muted-foreground">
            <span class="text-foreground font-bold">{recipe.average_rating}</span>
            ({recipe.total_ratings})
          </span>
        </form>
      </div>

      <section class="space-y-4">
        <h2 class="text-xl font-semibold border-b pb-1">Ingredients</h2>
        <div class="space-y-6">
          {#each recipe.components ?? [] as component}
            <div class="space-y-2">
              {#if !isMain(component.name)}
                <h3 class="text-xs font-bold uppercase tracking-wider text-primary">
                  {component.name}
                </h3>
              {/if}
              <ul class="list-disc pl-5 space-y-1 text-sm leading-relaxed">
                {#each component.ingredients ?? [] as ing}
                  <li>
                    {#if ing.amount}
                      <span class="font-medium">{ing.amount}</span>
                      {ing.unit ? ` ${ing.unit}` : ''}
                    {/if}
                    {ing.name}
                  </li>
                {/each}
              </ul>
            </div>
          {/each}
        </div>
      </section>

      <div class="pt-4 border-t space-y-6">
        {#if recipe.notes?.length > 0}
          <div class="space-y-1">
            <span
              class="text-[10px] uppercase font-bold tracking-tighter block text-muted-foreground"
              >Notes</span
            >
            <div class="text-sm leading-relaxed space-y-2">
              {#each recipe.notes as note}
                <p>{note}</p>
              {/each}
            </div>
          </div>
        {/if}

        {#if recipe.storage?.length > 0}
          <div class="space-y-1 pt-2">
            <span
              class="text-[10px] uppercase font-bold tracking-tighter block text-muted-foreground"
              >Storage</span
            >
            <div class="text-sm leading-relaxed space-y-2">
              {#each recipe.storage as item}
                <p>{item}</p>
              {/each}
            </div>
          </div>
        {/if}
      </div>
    </aside>

    <div class="space-y-12">
      <header class="border-b pb-6">
        <h1 class="text-3xl font-semibold tracking-tight mb-4">
          {recipe.title}
        </h1>
        {#if recipe.description}
          <p class="text-lg text-muted-foreground leading-relaxed line-clamp-3">
            {recipe.description}
          </p>
        {/if}
      </header>

      <section class="space-y-6">
        <h2 class="text-xl font-semibold border-b pb-1">Instructions</h2>
        <div class="space-y-8">
          {#each recipe.components ?? [] as component}
            <div class="space-y-3">
              {#if !isMain(component.name)}
                <h3 class="text-xs font-bold uppercase tracking-wider text-primary">
                  {component.name}
                </h3>
              {/if}
              <ol class="list-decimal pl-5 space-y-4 text-sm leading-relaxed">
                {#each component.steps ?? [] as step}
                  <li class="pl-1">
                    {step.description}
                  </li>
                {/each}
              </ol>
            </div>
          {/each}
        </div>
      </section>
    </div>
  </div>
</article>
