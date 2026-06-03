<script>
  import * as Card from "$lib/components/ui/card/index.js";
  import { Button } from "$lib/components/ui/button/index.js";

  let { data } = $props();
</script>

<div class="flex min-h-screen flex-col items-center justify-center p-4">
  <Card.Root class="w-full max-w-xl">
    <Card.Header>
      <Card.Title
        class="text-xl font-bold text-emerald-600 dark:text-emerald-400"
      >
        Active Session Token
      </Card.Title>
      <Card.Description>
        This token was successfully fetched
      </Card.Description>
    </Card.Header>

    <Card.Content class="space-y-4">
      <div
        class="rounded-md border bg-muted p-4 font-mono text-xs break-all shadow-inner max-h-64 overflow-y-auto select-all"
      >
        {data.token}
      </div>

      <p class="text-xs text-muted-foreground italic">
        * Tip: You can double-click or click-and-drag inside the box above to
        copy the complete string.
      </p>
    </Card.Content>

    <Card.Footer class="flex justify-end gap-2 border-t pt-4">
      <Button variant="outline" href="/login">Back to Login</Button>
    </Card.Footer>
  </Card.Root>
</div>
