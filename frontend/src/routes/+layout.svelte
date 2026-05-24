<script>
  import "../app.css";
  import { ModeWatcher } from "mode-watcher";

  import ModeToggle from "$lib/components/ModeToggle.svelte";

  let { children } = $props();
</script>

{@render children()}

<div class="fixed right-4 top-4 z-50">
  <ModeToggle />
</div>

<ModeWatcher />
