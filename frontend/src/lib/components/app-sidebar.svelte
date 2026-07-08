<script>
  import CalendarIcon from '@lucide/svelte/icons/calendar';
  import HouseIcon from '@lucide/svelte/icons/house';
  import InboxIcon from '@lucide/svelte/icons/inbox';
  import SearchIcon from '@lucide/svelte/icons/search';
  import UtensilsCrossedIcon from '@lucide/svelte/icons/utensils-crossed';
  import SettingsIcon from '@lucide/svelte/icons/settings';
  import * as Sidebar from '$lib/components/ui/sidebar/index.js';

  // Menu items.
  const items = [
    {
      title: 'Home',
      url: '/',
      icon: HouseIcon
    },
    {
      title: 'Recipes',
      url: '/recipes',
      icon: UtensilsCrossedIcon
    }
  ];
</script>

<Sidebar.Root>
  <Sidebar.Header class="px-4 py-3 border-b border-sidebar-border">
    <span> Forkbook </span>
  </Sidebar.Header>
  <Sidebar.Content>
    <Sidebar.Group>
      <Sidebar.GroupLabel>Navigation</Sidebar.GroupLabel>
      <Sidebar.GroupContent>
        <Sidebar.Menu>
          {#each items as item (item.title)}
            <Sidebar.MenuItem>
              <Sidebar.MenuButton>
                {#snippet child({ props })}
                  <a
                    href={item.url}
                    {...props}
                    class="flex items-center gap-2 px-2 py-1.5 rounded-md w-full"
                  >
                    <div class="shrink-0">
                      <item.icon class="h-4 w-4" />
                    </div>
                    <span>{item.title}</span>
                  </a>
                {/snippet}
              </Sidebar.MenuButton>
            </Sidebar.MenuItem>
          {/each}
        </Sidebar.Menu>
      </Sidebar.GroupContent>
    </Sidebar.Group>
  </Sidebar.Content>
</Sidebar.Root>
