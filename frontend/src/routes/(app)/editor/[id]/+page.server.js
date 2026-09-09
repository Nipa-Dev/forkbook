import { api } from '$lib/server/api';
import { fail, redirect } from '@sveltejs/kit';

function parseArray(value, delimiter = ',') {
  if (!value) return [];

  return value
    .toString()
    .split(delimiter)
    .map((item) => item.trim())
    .filter(Boolean);
}

function parseNumber(value) {
  if (value === null || value === undefined || value === '') {
    return null;
  }

  const number = Number(value);

  return Number.isFinite(number) ? number : null;
}

function parseComponents(value) {
  if (!value) return [];

  try {
    return JSON.parse(value.toString());
  } catch {
    return [];
  }
}

export async function load({ params }) {
  const recipe = await api(`/recipes/${params.id}`);

  return { recipe };
}

export const actions = {
  save: async ({ request, params }) => {
    const data = await request.formData();

    const payload = {
      title: data.get('title')?.toString().trim() ?? '',
      description: data.get('description')?.toString().trim() || null,
      image_url: data.get('image_url')?.toString().trim() || null,
      difficulty: data.get('difficulty')?.toString() || 'easy',

      prep_time_minutes: parseNumber(data.get('prep_time_minutes')),
      cook_time_minutes: parseNumber(data.get('cook_time_minutes')),
      servings: parseNumber(data.get('servings')),

      tags: parseArray(data.get('tags'), ','),
      equipment: parseArray(data.get('equipment'), ','),
      notes: parseArray(data.get('notes'), '\n'),
      storage: parseArray(data.get('storage'), '\n'),

      components: parseComponents(data.get('components'))
    };

    try {
      await api(`/recipes/${params.id}`, {
        method: 'PATCH',
        body: JSON.stringify(payload)
      });

      // Upload image only if one was selected
      const image = data.get('image');

      if (image instanceof File && image.size > 0) {
        const imageData = new FormData();
        imageData.append('image', image);

        await api(`/recipes/${params.id}/image`, {
          method: 'PUT',
          body: imageData
        });
      }
    } catch (err) {
      console.error('API Save Error:', err);

      return fail(500, {
        error: 'Failed to save recipe'
      });
    }

    throw redirect(303, `/recipes/${params.id}`);
  }
};
