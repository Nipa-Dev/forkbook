<script>
  import { enhance } from '$app/forms';
  import { Star, Bookmark, CheckCircle } from 'lucide-svelte';
  let { recipe } = $props();
  const isMain = (name) => name === 'Main' || name === 'Component: Main';

  let userRating = $state(0);
  let hoverRating = $state(0);
  let bookmarkedState = $state(false);
  let madeState = $state(false);

  $effect(() => {
    userRating = Math.round(recipe.average_rating ?? 0);
    bookmarkedState = !!recipe.is_bookmarked;
    madeState = !!recipe.is_made;
  });
</script>

<article class="max-w-6xl mx-auto px-6 py-8">
  <div class="grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-16">
    <div class="space-y-12">
      <header class="border-b pb-6">
        <h1 class="text-3xl font-semibold tracking-tight mb-4">
          {recipe.title}
        </h1>
        {#if recipe.description}
          <p class="text-lg text-muted-foreground leading-relaxed">
            {recipe.description}
          </p>
        {/if}
      </header>

      <section class="space-y-6">
        <h2 class="text-xl font-semibold border-b pb-1">Ingredients</h2>
        <div class="grid sm:grid-cols-2 gap-8">
          {#each recipe.components ?? [] as component}
            <div class="space-y-2">
              {#if !isMain(component.name)}
                <h3 class="text-xs font-bold uppercase tracking-wider text-primary">
                  {component.name}
                </h3>
              {/if}
              <ul class="list-disc list-outside pl-5 space-y-1 text-sm leading-relaxed">
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

      <section class="space-y-6">
        <h2 class="text-xl font-semibold border-b pb-1">Instructions</h2>
        <div class="grid sm:grid-cols-2 gap-8 items-start">
          {#each recipe.components ?? [] as component}
            <div class="space-y-3">
              {#if !isMain(component.name)}
                <h3 class="text-xs font-bold uppercase tracking-wider text-primary">
                  {component.name}
                </h3>
              {/if}
              <ol class="list-decimal list-outside pl-5 space-y-3 text-sm leading-relaxed">
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

    <aside class="space-y-8 lg:sticky lg:top-8 h-fit">
      {#if recipe.image_url}
        <div class="rounded-xl overflow-hidden shadow-sm border">
          <img src={recipe.image_url} alt={recipe.title} class="w-full aspect-4/3 object-cover" />
        </div>
      {/if}

      <div class="space-y-6">
        <form method="POST" action="?/rateRecipe" use:enhance class="flex items-center gap-1">
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
                class="focus:outline-none transition-transform active:scale-95 cursor-pointer bg-transparent border-none p-0"
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

          <span class="ml-2 text-xs font-medium">
            <span class="text-foreground font-bold">{recipe.average_rating}</span>
            ({recipe.total_ratings})
          </span>
        </form>

        <div class="flex gap-2">
          <form method="POST" action="?/toggleBookmark" use:enhance>
            <input type="hidden" name="active" value={bookmarkedState ? 'false' : 'true'} />
            <button
              type="submit"
              class="flex items-center gap-2 text-xs font-medium hover:text-foreground cursor-pointer bg-transparent border-none p-0"
              aria-label={bookmarkedState ? 'Remove bookmark' : 'Bookmark recipe'}
            >
              <Bookmark
                size={16}
                class={bookmarkedState ? 'text-primary' : ''}
                fill={bookmarkedState ? 'currentColor' : 'none'}
              />
              <span>{bookmarkedState ? 'Bookmarked' : 'Add Bookmark'}</span>
            </button>
          </form>

          <form method="POST" action="?/toggleMade" use:enhance>
            <input type="hidden" name="active" value={madeState ? 'false' : 'true'} />
            <button
              type="submit"
              class="flex items-center gap-2 text-xs font-medium hover:text-foreground cursor-pointer bg-transparent border-none p-0"
              aria-label={madeState ? 'Mark as unmade' : 'Mark as made'}
            >
              <CheckCircle
                size={16}
                fill="none"
                class={madeState ? 'text-foreground' : 'text-muted-foreground'}
              />
              <span>{madeState ? 'Made' : 'Mark Made'}</span>
            </button>
          </form>
        </div>
        <div class="pt-4 border-t space-y-6">
          <div class="grid grid-cols-2 gap-4">
            <div class="flex flex-col">
              <span class="text-[10px] uppercase font-bold tracking-tighter">Cook Time</span>
              <span class="text-sm">{recipe.cook_time_minutes} min</span>
            </div>
            <div class="flex flex-col">
              <span class="text-[10px] uppercase font-bold tracking-tighter">Prep Time</span>
              <span class="text-sm">{recipe.prep_time_minutes ?? 0} min</span>
            </div>
          </div>

          {#if recipe.notes?.length > 0}
            <div class="space-y-1">
              <span class="text-[10px] uppercase font-bold tracking-tighter block">Notes</span>
              <div class="text-sm leading-relaxed space-y-2">
                {#each recipe.notes as note}
                  <p>{note}</p>
                {/each}
              </div>
            </div>
          {/if}

          {#if recipe.storage?.length > 0}
            <div class="space-y-1 pt-2">
              <span class="text-[10px] uppercase font-bold tracking-tighter block">Storage</span>
              <div class="text-sm leading-relaxed space-y-2">
                {#each recipe.storage as item}
                  <p>{item}</p>
                {/each}
              </div>
            </div>
          {/if}
        </div>
      </div>
      <a
        href="/editor/{recipe.id}"
        class="text-xs font-semibold uppercase tracking-wider hover:text-primary border px-3 py-1.5 rounded-md"
      >
        Edit Recipe
      </a>
    </aside>
  </div>
</article>
