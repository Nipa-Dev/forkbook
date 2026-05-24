<script>
  import * as Dialog from "$lib/components/ui/dialog/index.js";
  import { Input } from "$lib/components/ui/input/index.js";
  import { Button, buttonVariants } from "$lib/components/ui/button/index.js";

  function handleSubmit(e) {
    e.preventDefault();

    const form = new FormData(e.currentTarget);
    const query = form.get("search")?.toString() ?? "";

    const url = new URL(window.location.href);

    if (query.trim()) {
      url.searchParams.set("search", query);
    } else {
      url.searchParams.delete("search");
    }

    window.location.href = url.toString();
  }
</script>

<Dialog.Root>
  <Dialog.Trigger class={buttonVariants({ variant: "outline" })}>
    Search recipes…
  </Dialog.Trigger>

  <Dialog.Content class="sm:max-w-md">
    <Dialog.Header>
      <Dialog.Title>Search recipes</Dialog.Title>
      <Dialog.Description>
        Search by recipe name or ingredient.
      </Dialog.Description>
    </Dialog.Header>

    <form onsubmit={handleSubmit} class="flex gap-2">
      <Input name="search" placeholder="Try: chicken, pasta..." autofocus />
      <Button type="submit">Go</Button>
    </form>
  </Dialog.Content>
</Dialog.Root>
