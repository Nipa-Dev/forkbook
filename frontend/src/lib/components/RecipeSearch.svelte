<script>
  import * as Dialog from '$lib/components/ui/dialog/index.js';
  import { Input } from '$lib/components/ui/input/index.js';
  import { Button, buttonVariants } from '$lib/components/ui/button/index.js';
  import { Badge } from '$lib/components/ui/badge/index.js';

  const difficulties = ['easy', 'medium', 'hard'];

  let searchQuery = $state('');
  let selectedDifficulty = $state('');

  function toggleDifficulty(level) {
    selectedDifficulty = selectedDifficulty === level ? '' : level;
  }

  function handleSubmit(e) {
    e.preventDefault();

    const url = new URL(window.location.href);

    if (searchQuery.trim()) {
      url.searchParams.set('search', searchQuery.trim());
    } else {
      url.searchParams.delete('search');
    }

    if (selectedDifficulty) {
      url.searchParams.set('difficulty', selectedDifficulty);
    } else {
      url.searchParams.delete('difficulty');
    }

    window.location.href = url.toString();
  }
</script>

<Dialog.Root>
  <Dialog.Trigger class={buttonVariants({ variant: 'outline' })}>
    Search recipes…
  </Dialog.Trigger>

  <Dialog.Content class="sm:max-w-md">
    <Dialog.Header>
      <Dialog.Title>Search recipes</Dialog.Title>
      <Dialog.Description>
        Search by recipe name or filter by difficulty level.
      </Dialog.Description>
    </Dialog.Header>

    <form onsubmit={handleSubmit} class="space-y-4">
      <Input
        bind:value={searchQuery}
        name="search"
        placeholder="Try: chicken, pasta..."
        autofocus
      />

      <fieldset class="space-y-1.5">
        <legend class="text-xs font-medium text-muted-foreground">Difficulty</legend>
        <div class="flex gap-2">
          {#each difficulties as level}
            <button
              type="button"
              onclick={() => toggleDifficulty(level)}
              class="focus:outline-none"
            >
              <Badge
                variant={selectedDifficulty === level ? 'default' : 'outline'}
                class="capitalize cursor-pointer px-3 py-1"
              >
                {level}
              </Badge>
            </button>
          {/each}
        </div>
      </fieldset>

      <div class="flex justify-end gap-2 pt-2">
        <Dialog.Close class={buttonVariants({ variant: 'ghost' })}>
          Cancel
        </Dialog.Close>
        <Button type="submit">Search</Button>
      </div>
    </form>
  </Dialog.Content>
</Dialog.Root>