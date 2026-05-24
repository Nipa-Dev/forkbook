<script>
  import { ModeWatcher } from "mode-watcher";
  import favicon from "$lib/assets/favicon.svg";

  import * as Sidebar from "$lib/components/ui/sidebar";
  import AppSidebar from "$lib/components/app-sidebar.svelte";
  import ModeToggle from "$lib/components/ModeToggle.svelte";

  let { children } = $props();
</script>

<svelte:head>
  <link rel="icon" href={favicon} />
</svelte:head>

<Sidebar.Provider>
  <div class="flex min-h-screen">
    <!--<AppSidebar />-->
    <div class="hidden lg:block">
      <AppSidebar />
    </div>

    <Sidebar.Inset class="flex-1 min-w-0 overflow-y-auto overflow-x-hidden">
      {@render children()}
    </Sidebar.Inset>
  </div>
</Sidebar.Provider>

<!-- global on all pages
<div class="fixed right-4 top-4 z-50">
  <ModeToggle />
</div>

<ModeWatcher /> -->
