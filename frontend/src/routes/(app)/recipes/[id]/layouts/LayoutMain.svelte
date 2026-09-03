<script>
  import { enhance } from '$app/forms';
  import { Badge } from '$lib/components/ui/badge';
  import { Star, Bookmark, CheckCircle } from 'lucide-svelte';

  let { recipe } = $props();

  let userRating = $state(0);
  let hoverRating = $state(0);
  let bookmarkedState = $state(false);
  let madeState = $state(false);
  const getImageUrl = (filename) => `/images/${filename}`;

  $effect(() => {
    userRating = Math.round(recipe.average_rating ?? 0);
    bookmarkedState = !!recipe.is_bookmarked;
    madeState = !!recipe.is_made;
  });
</script>

<article class="max-w-4xl mx-auto px-6 py-8">
  <header class="space-y-5 mb-10">
    {#if recipe.image_hero_filename}
      <div class="rounded-xl overflow-hidden border">
        <img
          src={getImageUrl(recipe.image_hero_filename)}
          alt={recipe.title}
          class="w-full aspect-16/7 object-cover"
        />
      </div>
    {/if}

    <div class="space-y-4">
      <div class="space-y-3">
        <h1 class="text-3xl font-semibold tracking-tight">
          {recipe.title}
        </h1>

        {#if recipe.description}
          <p class="text-lg text-muted-foreground leading-relaxed max-w-3xl">
            {recipe.description}
          </p>
        {/if}
      </div>

      {#if recipe.tags?.length}
        <div class="flex flex-wrap gap-2">
          {#each recipe.tags as tag, i (i)}
            <Badge variant="secondary" class="text-xs font-normal px-2.5 py-0.5 rounded-md">
              {tag}
            </Badge>
          {/each}
        </div>
      {/if}
    </div>
  </header>

  <section class="border-y py-5 mb-8">
    <div class="grid grid-cols-3 gap-x-8 gap-y-5 w-fit">
      <div class="flex flex-col">
        <span class="text-[10px] uppercase font-bold tracking-wider text-muted-foreground">
          Prep
        </span>
        <span class="text-sm">
          {recipe.prep_time_minutes != null ? `${recipe.prep_time_minutes} min` : '--'}
        </span>
      </div>

      <div class="flex flex-col">
        <span class="text-[10px] uppercase font-bold tracking-wider text-muted-foreground">
          Cook
        </span>
        <span class="text-sm">
          {recipe.cook_time_minutes != null ? `${recipe.cook_time_minutes} min` : '--'}
        </span>
      </div>

      <div class="flex flex-col">
        <span class="text-[10px] uppercase font-bold tracking-wider text-muted-foreground">
          Rating
        </span>

        <div class="flex items-center gap-2">
          <form method="POST" action="?/rateRecipe" use:enhance>
            <input type="hidden" name="recipeId" value={recipe.id} />

            <div
              class="flex text-primary"
              onmouseleave={() => (hoverRating = 0)}
              role="group"
              aria-label="Rate this recipe"
            >
              {#each Array(5).fill(0) as _, i}
                {@const starValue = i + 1}

                <button
                  type="submit"
                  name="rating"
                  value={starValue}
                  class="focus:outline-none transition-transform active:scale-95 cursor-pointer bg-transparent border-none p-0"
                  onmouseenter={() => (hoverRating = starValue)}
                  aria-label="Rate {starValue} out of 5 stars"
                >
                  <Star
                    size={16}
                    fill={(hoverRating || userRating) >= starValue ? 'currentColor' : 'none'}
                  />
                </button>
              {/each}
            </div>
          </form>

          <span class="text-xs font-medium">
            {recipe.average_rating ?? 0}
          </span>
        </div>
      </div>

      <div class="flex flex-col">
        <span class="text-[10px] uppercase font-bold tracking-wider text-muted-foreground">
          Servings
        </span>
        <span class="text-sm">
          {recipe.servings ?? '--'}
        </span>
      </div>

      <div class="flex flex-col">
        <span class="text-[10px] uppercase font-bold tracking-wider text-muted-foreground">
          Difficulty
        </span>
        <span class="text-sm capitalize">
          {recipe.difficulty ?? '--'}
        </span>
      </div>
    </div>
  </section>

  <div class="flex items-center gap-5 mb-12">
    <form method="POST" action="?/toggleBookmark" use:enhance>
      <input type="hidden" name="active" value={bookmarkedState ? 'false' : 'true'} />

      <button
        type="submit"
        class="flex items-center gap-2 text-xs font-medium hover:text-foreground cursor-pointer bg-transparent border-none p-0"
        aria-label={bookmarkedState ? 'Remove bookmark' : 'Bookmark recipe'}
      >
        <Bookmark
          size={16}
          class={bookmarkedState ? 'text-primary' : 'text-muted-foreground'}
          fill={bookmarkedState ? 'currentColor' : 'none'}
        />

        <span>
          {bookmarkedState ? 'Bookmarked' : 'Add Bookmark'}
        </span>
      </button>
    </form>

    <form method="POST" action="?/toggleMade" use:enhance>
      <input type="hidden" name="active" value={madeState ? 'false' : 'true'} />

      <button
        type="submit"
        class="flex items-center gap-2 text-xs font-medium hover:text-foreground cursor-pointer bg-transparent border-none p-0"
        aria-label={madeState ? 'Mark as unmade' : 'Mark Made'}
      >
        <CheckCircle
          size={16}
          fill="none"
          class={madeState ? 'text-foreground' : 'text-muted-foreground'}
        />

        <span>
          {madeState ? 'Made' : 'Mark Made'}
        </span>
      </button>
    </form>

    <a
      href="/editor/{recipe.id}"
      class="text-xs font-semibold uppercase tracking-wider hover:text-primary border px-3 py-1.5 rounded-md"
    >
      Edit Recipe
    </a>
  </div>

  <section class="space-y-8 mb-14">
    <h2 class="text-xl font-semibold border-b pb-2">Ingredients</h2>

    {#each recipe.components ?? [] as component}
      <div class="space-y-3">
        <h3 class="text-sm font-semibold">
          {component.name}
        </h3>

        <ul class="list-disc list-outside pl-5 space-y-1 text-sm leading-relaxed">
          {#each component.ingredients ?? [] as ingredient}
            <li>
              {#if ingredient.raw}
                {ingredient.raw}
              {:else}
                {ingredient.amount ?? ''}
                {ingredient.unit ? ` ${ingredient.unit}` : ''}
                {ingredient.name ?? ''}
              {/if}
            </li>
          {/each}
        </ul>
      </div>
    {/each}
  </section>

  <section class="space-y-8 mb-14">
    <h2 class="text-xl font-semibold border-b pb-2">Instructions</h2>

    {#each recipe.components ?? [] as component}
      <div class="space-y-4">
        <h3 class="text-sm font-semibold">
          {component.name}
        </h3>

        <ol class="list-decimal list-outside pl-5 space-y-4 text-sm leading-relaxed">
          {#each component.steps ?? [] as step}
            <li class="pl-2">
              {step.description}

              {#if step.timer_seconds}
                <span class="text-xs text-muted-foreground ml-2">
                  ({Math.floor(step.timer_seconds / 60)} min)
                </span>
              {/if}
            </li>
          {/each}
        </ol>
      </div>
    {/each}
  </section>

  {#if recipe.notes?.length || recipe.storage?.length || recipe.equipment?.length}
    <section class="border-t pt-8 space-y-8">
      {#if recipe.notes?.length}
        <div class="space-y-3">
          <h2 class="text-sm font-semibold uppercase tracking-wider">Notes</h2>

          <div class="text-sm leading-relaxed space-y-2">
            {#each recipe.notes as note}
              <p>{note}</p>
            {/each}
          </div>
        </div>
      {/if}

      {#if recipe.storage?.length}
        <div class="space-y-3">
          <h2 class="text-sm font-semibold uppercase tracking-wider">Storage</h2>

          <div class="text-sm leading-relaxed space-y-2">
            {#each recipe.storage as item}
              <p>{item}</p>
            {/each}
          </div>
        </div>
      {/if}

      {#if recipe.equipment?.length}
        <div class="space-y-3">
          <h2 class="text-sm font-semibold uppercase tracking-wider">Equipment</h2>

          <ul class="list-disc list-outside pl-5 space-y-1 text-sm leading-relaxed">
            {#each recipe.equipment as item}
              <li>{item}</li>
            {/each}
          </ul>
        </div>
      {/if}
    </section>
  {/if}
</article>
