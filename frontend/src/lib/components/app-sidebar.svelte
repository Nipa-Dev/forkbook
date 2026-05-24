<script>
  import * as Sidebar from "$lib/components/ui/sidebar";
</script>

<Sidebar.Root>
  <Sidebar.Header>
    <div class="px-2 py-2 font-semibold">Recipe Book</div>
  </Sidebar.Header>

  <Sidebar.Content>
    <Sidebar.Group>
      <Sidebar.GroupLabel>Navigation</Sidebar.GroupLabel>

      <Sidebar.Menu>
        <Sidebar.MenuItem>
          <Sidebar.MenuButton>
            {#snippet child({ props })}
              <a href="/recipes" {...props}> All Recipes </a>
            {/snippet}
          </Sidebar.MenuButton>
        </Sidebar.MenuItem>
      </Sidebar.Menu>
    </Sidebar.Group>
  </Sidebar.Content>

  <Sidebar.Footer>
    <div class="p-2 text-xs text-muted-foreground">v0.1</div>
  </Sidebar.Footer>
</Sidebar.Root>
