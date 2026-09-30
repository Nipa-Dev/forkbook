export function parseRecipeFormData(data) {
  const parseArray = (value, delimiter = ',') => {
    if (!value) return [];
    return value
      .toString()
      .split(delimiter)
      .map((item) => item.trim())
      .filter(Boolean);
  };

  const parseNumber = (value) => {
    if (value === null || value === undefined || value === '') return null;
    const number = Number(value);
    return Number.isFinite(number) ? number : null;
  };

  const parseComponents = (value) => {
    if (!value) return [];
    try {
      return JSON.parse(value.toString());
    } catch {
      return [];
    }
  };

  return {
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
}
