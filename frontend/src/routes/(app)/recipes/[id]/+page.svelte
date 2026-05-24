<script>
  import LayoutA from "./layouts/LayoutA.svelte";
  import LayoutB from "./layouts/LayoutB.svelte";
  import LayoutC from "./layouts/LayoutC.svelte";
  import LayoutD from "./layouts/LayoutD.svelte";

  const layouts = {
    A: LayoutA,
    B: LayoutB,
    C: LayoutC,
    D: LayoutD,
  };

  let { data } = $props();

  const recipe = $derived(data.recipe);
  const Layout = $derived(layouts[data.layout] ?? LayoutA);
</script>

<Layout {recipe} />
