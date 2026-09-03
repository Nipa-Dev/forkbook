<script>
  import { Input } from '$lib/components/ui/input';
  import { Label } from '$lib/components/ui/label';
  import { Button } from '$lib/components/ui/button';
  import { Textarea } from '$lib/components/ui/textarea';
  import * as Select from '$lib/components/ui/select';

  let { data } = $props();

  const recipeId = $derived(data.recipe?.id ?? '');
  const toList = (value) => (Array.isArray(value) ? value.join(', ') : (value ?? ''));

  const toLines = (value) => (Array.isArray(value) ? value.join('\n') : (value ?? ''));

  function ingredientForEditor(ingredient) {
    if (ingredient.raw) {
      return { raw: ingredient.raw };
    }

    return {
      raw: [ingredient.amount, ingredient.unit, ingredient.name].filter(Boolean).join(' ')
    };
  }

  let form = $state({
    title: '',
    description: '',
    cook_time_minutes: '',
    prep_time_minutes: '',
    servings: '',
    tags: '',
    equipment: '',
    notes: '',
    storage: '',
    difficulty: 'easy'
  });

  let components = $state([]);

  $effect(() => {
    const recipe = data.recipe;

    form.title = recipe?.title ?? '';
    form.description = recipe?.description ?? '';
    form.cook_time_minutes = recipe?.cook_time_minutes ?? '';
    form.prep_time_minutes = recipe?.prep_time_minutes ?? '';
    form.servings = recipe?.servings ?? '';
    form.tags = toList(recipe?.tags);
    form.equipment = toList(recipe?.equipment);
    form.notes = toLines(recipe?.notes);
    form.storage = toLines(recipe?.storage);
    form.difficulty = recipe?.difficulty ?? 'easy';

    components = componentsForEditor(recipe?.components);
  });

  const emptyComponent = () => ({
    name: 'Main',
    component_order: 1,
    ingredients: [{ raw: '' }],
    steps: [{ step_order: 1, description: '', timer_seconds: null }]
  });

  function componentsForEditor(components) {
    if (!components?.length) {
      return [emptyComponent()];
    }

    return components.map((component) => {
      const ingredients = component.ingredients.map(ingredientForEditor);

      return {
        ...component,
        ingredients
      };
    });
  }

  const difficultyOptions = [
    { value: 'easy', label: 'Easy' },
    { value: 'medium', label: 'Medium' },
    { value: 'hard', label: 'Hard' }
  ];

  let difficulty = $derived(data.recipe?.difficulty ?? 'easy');

  const triggerContent = $derived(
    difficultyOptions.find((o) => o.value === form.difficulty)?.label ?? 'Select difficulty'
  );

  const payloadComponents = $derived(components);
</script>

<ModeWatcher defaultMode="dark" />

<form
  method="POST"
  action="?/save"
  enctype="multipart/form-data"
  class="mx-auto max-w-3xl space-y-6 p-4 md:p-6"
>
  <input type="hidden" name="components" value={JSON.stringify(payloadComponents)} />

  <Card.Root>
    <Card.Header>
      <Card.Title>General Information</Card.Title>
      <Card.Description>Basic details about your recipe.</Card.Description>
    </Card.Header>
    <Card.Content class="space-y-4">
      <div class="space-y-2">
        <Label for="title">Title</Label>
        <Input
          id="title"
          name="title"
          placeholder="e.g. Fancy recipe title"
          bind:value={form.title}
          required
        />
      </div>

      <div class="space-y-2">
        <Label for="description">Description</Label>
        <Textarea
          id="description"
          name="description"
          rows="3"
          placeholder="Brief summary of the dish..."
          bind:value={form.description}
        />
      </div>

      <div class="space-y-2">
        <Label for="image">Recipe Image</Label>
        <Input id="image" name="image" type="file" accept="image/*" />

        {#if data.recipe?.image_filename}
          <p class="text-sm text-muted-foreground">
            Current image: {data.recipe.image_filename}
          </p>
        {/if}
      </div>
    </Card.Content>
  </Card.Root>

  <Card.Root>
    <Card.Header class="flex items-center justify-between">
      <div>
        <Card.Title>Recipe Components</Card.Title>
        <Card.Description>
          Organize ingredients and steps into sections (e.g., Main, Sauce, Dough).
        </Card.Description>
      </div>
      <Button
        type="button"
        variant="outline"
        onclick={() => {
          components.push({
            name: '',
            component_order: components.length + 1,
            ingredients: [{ raw: '' }],
            steps: [{ step_order: 1, description: '', timer_seconds: null }]
          });
        }}
      >
        + Add Section
      </Button>
    </Card.Header>

    <Card.Content class="space-y-12">
      {#each components as component, compIndex}
        <div class="space-y-6">
          <div class="flex items-center gap-2">
            <Input
              placeholder="Component Name (e.g. Sauce)"
              bind:value={component.name}
              class="font-semibold text-lg"
              required
            />
            {#if components.length > 1}
              <Button
                type="button"
                variant="destructive"
                size="sm"
                onclick={() => {
                  components.splice(compIndex, 1);

                  components.forEach((component, index) => {
                    component.component_order = index + 1;
                  });
                }}
              >
                Remove Section
              </Button>
            {/if}
          </div>

          <div class="space-y-3">
            <Label class="font-semibold text-base">Ingredients</Label>

            <div class="border rounded-xl overflow-hidden divide-y divide-border bg-muted/10">
              {#each component.ingredients as ingredient, ingIndex}
                <div class="flex items-center group relative focus-within:z-10">
                  <Input
                    placeholder="e.g. 250 g flour or 2 tbsp olive oil"
                    bind:value={ingredient.raw}
                    class="border-none rounded-none shadow-none focus-visible:ring-1 focus-visible:ring-ring bg-transparent h-10 px-4"
                  />
                  <div class="pr-2">
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      class="hover:text-destructive"
                      onclick={() => component.ingredients.splice(ingIndex, 1)}
                    >
                      ✕
                    </Button>
                  </div>
                </div>
              {/each}
            </div>

            <Button
              type="button"
              variant="outline"
              size="sm"
              class="w-full sm:w-auto"
              onclick={() => component.ingredients.push({ raw: '' })}
            >
              + Add Ingredient
            </Button>
          </div>

          <div class="space-y-3 pt-2">
            <Label class="font-semibold text-base">Steps</Label>

            <div class="border rounded-xl overflow-hidden divide-y divide-border bg-muted/10">
              {#each component.steps as step, stepIndex}
                <div class="flex items-start group relative focus-within:z-10 px-4 py-1">
                  <span class="pt-2.5 font-mono text-sm select-none w-6">
                    {stepIndex + 1}.
                  </span>
                  <Textarea
                    placeholder="Step instructions..."
                    rows="2"
                    bind:value={step.description}
                    class="border-none rounded-none shadow-none focus-visible:ring-1 focus-visible:ring-ring bg-transparent min-h-10 py-2 px-2 resize-y"
                  />
                  <div class="pt-1.5 pl-2">
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      class="hover:text-destructive"
                      onclick={() => {
                        component.steps.splice(stepIndex, 1);

                        component.steps.forEach((step, index) => {
                          step.step_order = index + 1;
                        });
                      }}
                    >
                      ✕
                    </Button>
                  </div>
                </div>
              {/each}
            </div>

            <Button
              type="button"
              variant="outline"
              size="sm"
              class="w-full sm:w-auto"
              onclick={() => {
                component.steps.push({
                  step_order: component.steps.length + 1,
                  description: '',
                  timer_seconds: null
                });
              }}
            >
              + Add Step
            </Button>
          </div>
        </div>
      {/each}
    </Card.Content>
  </Card.Root>

  <Card.Root>
    <Card.Header>
      <Card.Title>Cooking Details</Card.Title>
    </Card.Header>
    <Card.Content class="grid grid-cols-1 gap-4 sm:grid-cols-2 md:grid-cols-4">
      <div class="space-y-2">
        <Label>Difficulty</Label>
        <Select.Root type="single" name="difficulty" bind:value={form.difficulty}>
          <Select.Trigger class="w-full">
            {triggerContent}
          </Select.Trigger>
          <Select.Content>
            <Select.Group>
              {#each difficultyOptions as opt (opt.value)}
                <Select.Item value={opt.value}>
                  {opt.label}
                </Select.Item>
              {/each}
            </Select.Group>
          </Select.Content>
        </Select.Root>
      </div>

      <div class="space-y-2">
        <Label for="prep_time">Prep Time (mins)</Label>
        <Input
          id="prep_time"
          name="prep_time_minutes"
          type="number"
          min="0"
          placeholder="15"
          bind:value={form.prep_time_minutes}
        />
      </div>

      <div class="space-y-2">
        <Label for="cook_time">Cook Time (mins)</Label>
        <Input
          id="cook_time"
          name="cook_time_minutes"
          type="number"
          min="0"
          placeholder="30"
          bind:value={form.cook_time_minutes}
        />
      </div>

      <div class="space-y-2">
        <Label for="servings">Servings</Label>
        <Input
          id="servings"
          name="servings"
          type="number"
          min="1"
          placeholder="4"
          bind:value={form.servings}
        />
      </div>
    </Card.Content>
  </Card.Root>

  <Card.Root>
    <Card.Header>
      <Card.Title>Categorization & Equipment</Card.Title>
    </Card.Header>
    <Card.Content class="grid gap-4 md:grid-cols-2">
      <div class="space-y-2">
        <Label for="tags">Tags (comma separated)</Label>
        <Input
          id="tags"
          name="tags"
          placeholder="gluten-free, dinner, simple"
          bind:value={form.tags}
        />
      </div>

      <div class="space-y-2">
        <Label for="equipment">Equipment (comma separated)</Label>
        <Input
          id="equipment"
          name="equipment"
          placeholder="mixing bowl, whisk, baking pan"
          bind:value={form.equipment}
        />
      </div>
    </Card.Content>
  </Card.Root>

  <Card.Root>
    <Card.Header>
      <Card.Title>Additional Details</Card.Title>
    </Card.Header>
    <Card.Content class="space-y-4">
      <div class="space-y-2">
        <Label for="storage">Storage Instructions</Label>
        <Textarea
          id="storage"
          name="storage"
          rows="2"
          placeholder="Keep in an airtight container for up to x days..."
          bind:value={form.storage}
        />
      </div>

      <div class="space-y-2">
        <Label for="notes">Notes & Tips</Label>
        <Textarea
          id="notes"
          name="notes"
          rows="3"
          placeholder="Pro tips, dietary substitutions, etc."
          bind:value={form.notes}
        />
      </div>
    </Card.Content>
  </Card.Root>

  <div class="flex justify-end gap-4 pt-2">
    <Button href={recipeId ? `/recipes/${recipeId}` : '/recipes'} variant="outline">Cancel</Button>
    <Button type="submit">Save Recipe</Button>
  </div>
</form>
