<script>
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import { Button } from '$lib/components/ui/button';
  import { Textarea } from '$lib/components/ui/textarea';
  import * as Select from '$lib/components/ui/select';

  let { data, form } = $props();

  let recipe = $state({});

  $effect(() => {
    recipe = {
      title: data.recipe.title ?? '',
      description: data.recipe.description ?? '',
      cook_time: data.recipe.cook_time_minutes ?? '',
      prep_time: data.recipe.prep_time_minutes ?? '',
      image_url: data.recipe.image_url ?? '',
      tags: (data.recipe.tags ?? []).join(', '),
      equipment: (data.recipe.equipment ?? []).join(', '),
      notes: data.recipe.notes ?? '',
      storage: data.recipe.storage ?? ''
    };
  });

  const options = [
    { value: 'easy', label: 'Easy' },
    { value: 'medium', label: 'Medium' },
    { value: 'hard', label: 'Hard' }
  ];

  let difficulty = $state(data.recipe.difficulty ?? 'easy');

  const triggerContent = $derived(
    options.find((o) => o.value === difficulty)?.label ?? 'Select difficulty'
  );
</script>

<form class="w-full max-w-3xl md:p-6 p-4 space-y-6" method="POST" action="?/save">
  <div class="space-y-2">
    <Label for="title">Title</Label>
    <Input id="title" name="title" bind:value={recipe.title} />
  </div>

  <div class="space-y-2">
    <Label for="description">Description</Label>
    <Textarea id="description" name="description" rows="4" bind:value={recipe.description} />
  </div>

  <div class="space-y-2">
    <Label>Difficulty</Label>

    <Select.Root type="single" name="difficulty" bind:value={difficulty}>
      <Select.Trigger class="w-full border rounded px-3 py-2">
        {triggerContent}
      </Select.Trigger>

      <Select.Content>
        <Select.Group>
          {#each options as opt (opt.value)}
            <Select.Item value={opt.value}>
              {opt.label}
            </Select.Item>
          {/each}
        </Select.Group>
      </Select.Content>
    </Select.Root>

    <input type="hidden" name="difficulty" value={difficulty} />
  </div>

  <div class="space-y-2">
    <Label for="cook_time">Time (minutes)</Label>
    <Input id="cook_time" name="cook_time" type="number" bind:value={recipe.cook_time_minutes} />
  </div>

  <div class="space-y-2">
    <Label for="image_url">Image URL</Label>
    <Input id="image_url" name="image_url" bind:value={recipe.image_url} />
  </div>

  <div class="space-y-2">
    <Label for="tags">Tags</Label>
    <Textarea
      id="tags"
      name="tags"
      bind:value={recipe.tags}
      placeholder="brownies, dessert, chocolate"
    />
  </div>

  <div class="space-y-2">
    <Label for="equipment">Equipment</Label>
    <Textarea
      id="equipment"
      name="equipment"
      bind:value={recipe.equipment}
      placeholder="mixing bowl, whisk, baking pan"
    />
  </div>

  <div class="space-y-2">
    <Label for="storage">Storage</Label>
    <Textarea id="storage" name="storage" rows="4" bind:value={recipe.storage} />
  </div>

  <div class="space-y-2">
    <Label for="notes">Notes</Label>
    <Textarea id="notes" name="notes" rows="4" bind:value={recipe.notes} />
  </div>

  <Button type="submit">Save Recipe</Button>
</form>
