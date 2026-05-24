<script>
  import { Badge } from "$lib/components/ui/badge";
  import { Star } from "lucide-svelte";
  let { recipe } = $props();
  const isMain = (name) => name === "Main" || name === "Component: Main";
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
                <h3
                  class="text-xs font-bold uppercase tracking-wider text-primary"
                >
                  {component.name}
                </h3>
              {/if}
              <ul
                class="list-disc list-outside pl-5 space-y-1 text-sm leading-relaxed"
              >
                {#each component.ingredients ?? [] as ing}
                  <li>
                    {#if ing.amount}
                      <span class="font-medium">{ing.amount}</span>
                      {ing.unit ? ` ${ing.unit}` : ""}
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
                <h3
                  class="text-xs font-bold uppercase tracking-wider text-primary"
                >
                  {component.name}
                </h3>
              {/if}
              <ol
                class="list-decimal list-outside pl-5 space-y-3 text-sm leading-relaxed"
              >
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
          <img
            src={recipe.image_url}
            alt={recipe.title}
            class="w-full aspect-square object-cover"
          />
        </div>
      {/if}

      <div class="space-y-6">
        <div class="flex items-center gap-1">
          <div class="flex text-primary">
            {#each Array(5) as _, i}
              <Star size={16} fill={i < 4 ? "currentColor" : "none"} />
            {/each}
          </div>
          <span
            class="ml-2 text-[10px] font-bold text-muted-foreground tracking-tighter uppercase"
            >Rating</span
          >
        </div>

        <div class="pt-4 border-t space-y-6">
          <div class="grid grid-cols-2 gap-4">
            <div class="flex flex-col">
              <span
                class="text-[10px] uppercase font-bold text-muted-foreground tracking-tighter"
                >Prep Time</span
              >
              <span class="text-sm">20 min</span>
            </div>
            <div class="flex flex-col">
              <span
                class="text-[10px] uppercase font-bold text-muted-foreground tracking-tighter"
                >Cook Time</span
              >
              <span class="text-sm">{recipe.time_minutes} min</span>
            </div>
          </div>

          {#if recipe.notes?.length > 0}
            <div class="space-y-1">
              <span
                class="text-[10px] uppercase font-bold tracking-tighter block"
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
                class="text-[10px] uppercase font-bold tracking-tighter block"
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
      </div>
    </aside>
  </div>
</article>
