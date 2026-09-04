import { api } from '$lib/server/api';
import { fail, redirect, isRedirect } from '@sveltejs/kit';

export const actions = {
  default: async ({ request, fetch }) => {
    const formData = await request.formData();
    const recipeFile = formData.get('recipe_file');

    if (!recipeFile || !(recipeFile instanceof File) || recipeFile.size === 0) {
      return fail(400, { error: 'Please upload a valid recipe file.' });
    }

    let createdRecipe;

    try {
      createdRecipe = await api(
        '/recipes/import',
        {
          method: 'POST',
          body: formData
        },
        fetch
      );
    } catch (error) {
      // Re-throw if it's already a SvelteKit error/redirect
      if (isRedirect(error)) throw error;

      console.error('Import recipe error:', error);
      return fail(500, {
        error: error?.message || 'Failed to import recipe. Please try again.'
      });
    }

    // Call redirect outside of the try/catch block
    if (createdRecipe?.id) {
      throw redirect(303, `/recipes/${createdRecipe.id}`);
    }

    return fail(500, { error: 'Recipe was created, but no ID was returned.' });
  }
};