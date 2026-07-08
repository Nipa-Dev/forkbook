<script>
  import LayoutMain from './layouts/LayoutMain.svelte';
  import LayoutSecondary from './layouts/LayoutSecondary.svelte';

  const layouts = {
    main: LayoutMain,
    secondary: LayoutSecondary
  };

  let { data } = $props();

  const recipe = $derived(data.recipe);
  const Layout = $derived(layouts[data.layout] ?? LayoutMain);
</script>

<Layout {recipe} />
