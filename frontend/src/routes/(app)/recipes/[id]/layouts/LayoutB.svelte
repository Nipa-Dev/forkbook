<script>
  import { Badge } from "$lib/components/ui/badge";
  let { recipe } = $props();
  const isMain = (name) => name === "Main" || name === "Component: Main";
</script>

<article class="max-w-7xl mx-auto px-6 py-8">
  <div class="grid grid-cols-1 lg:grid-cols-[400px_1fr] gap-16">
    <div class="space-y-12">
      {#if recipe.image_url}
        <div class="rounded-xl overflow-hidden shadow-sm aspect-square">
          <img
            src={recipe.image_url}
            alt={recipe.title}
            class="w-full h-full object-cover"
          />
        </div>
      {/if}

      <section class="space-y-6">
        <h2 class="text-xl font-semibold border-b pb-1">Ingredients</h2>
        <div class="space-y-8">
          {#each recipe.components ?? [] as component}
            <div class="space-y-2">
              {#if !isMain(component.name)}
                <h3 class="font-bold uppercase tracking-wider text-primary">
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

      {#if recipe.notes?.length > 0}
        <section class="space-y-3 pt-6 border-t">
          <h2 class="text-sm font-bold uppercase tracking-wider">Notes</h2>
          <ul
            class="list-disc list-outside pl-5 space-y-1 text-xs leading-relaxed"
          >
            {#each recipe.notes as item}
              <li>{item}</li>
            {/each}
          </ul>
        </section>
      {/if}
    </div>

    <div class="space-y-10">
      <header class="w-full border-b pb-6">
        {#if recipe.difficulty}
          <Badge variant="outline" class="mb-4 capitalize"
            >{recipe.difficulty}</Badge
          >
        {/if}
        <h1 class="text-4xl font-semibold tracking-tight">
          {recipe.title}
        </h1>
        {#if recipe.description}
          <p class="mt-4 text-lg leading-relaxed">
            {recipe.description}
          </p>
        {/if}
      </header>

      <section class="space-y-6">
        <h2 class="text-xl font-semibold border-b pb-1">Instructions</h2>
        <div class="space-y-10">
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
                class="list-decimal list-outside pl-5 space-y-4 text-sm leading-relaxed"
              >
                {#each component.steps ?? [] as step}
                  <li class="pl-2">
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
