<script>
  import { Button } from '$lib/components/ui/button';
  import { Utensils } from 'lucide-svelte';
</script>

<svelte:head>
  <title>Forkbook</title>
  <meta
    name="description"
    content="A simple, self-hosted recipe manager for storing, organizing, and editing recipes."
  />
</svelte:head>

<div class="min-h-screen flex items-center justify-center p-6">
  <div class="max-w-2xl text-center space-y-8">
    <div class="space-y-4">
      <div class="flex justify-center">
        <div class="p-3 bg-primary/10 text-primary rounded-2xl">
          <Utensils class="w-10 h-10" />
        </div>
      </div>

      <h1 class="text-5xl font-bold tracking-tight">Forkbook</h1>

      <p class="text-xl text-muted-foreground">A simple place to keep your recipes.</p>

      <p class="text-muted-foreground max-w-lg mx-auto">
        Store, organize, edit, and import your recipes in a simple, readable format.
      </p>
    </div>

    <div class="flex justify-center gap-3">
      <Button href="/recipes" size="lg">Browse Recipes</Button>
    </div>
  </div>
</div>
