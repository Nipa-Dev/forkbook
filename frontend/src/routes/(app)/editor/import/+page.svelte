<script>
  import Button from '$lib/components/ui/button/button.svelte';
  import Input from '$lib/components/ui/input/input.svelte';
  import Label from '$lib/components/ui/label/label.svelte';
  import {
    Card,
    CardContent,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle
  } from '$lib/components/ui/card';
</script>

<div class="min-h-screen flex items-center justify-center bg-muted/30 p-6">
  <Card class="w-full max-w-xl">
    <CardHeader>
      <CardTitle>Upload Recipe</CardTitle>
      <CardDescription>
        Upload your recipe Markdown file and an image for the recipe.
      </CardDescription>
    </CardHeader>

    <form action="" method="post" enctype="multipart/form-data">
      <CardContent class="space-y-6 pb-8">
        <div class="space-y-2">
          <Label for="recipe_file">Recipe file</Label>
          <p class="text-sm text-muted-foreground">Markdown file (.md)</p>
          <Input type="file" id="recipe_file" name="recipe_file" accept=".md,text/markdown" />
        </div>

        <div class="space-y-2">
          <Label for="image_file">Recipe image</Label>
          <p class="text-sm text-muted-foreground">Image file</p>
          <Input type="file" id="image_file" name="image_file" accept="image/*" />
        </div>
      </CardContent>
      <CardFooter class="justify-end">
        <Button type="submit">Upload Recipe</Button>
      </CardFooter>
    </form>
  </Card>
</div>
