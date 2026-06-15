<script>
  import { Label } from "$lib/components/ui/label/index.js";
  import { Input } from "$lib/components/ui/input/index.js";
  import * as Card from "$lib/components/ui/card/index.js";
  import { Button } from "$lib/components/ui/button/index.js";
  import ModeToggle from "$lib/components/ModeToggle.svelte";
  import { page } from "$app/state";

  let { form } = $props();

  const redirectTo = page.url.searchParams.get("redirectTo") || "/";
  const formAction = `?/signup&redirectTo=${encodeURIComponent(redirectTo)}`;
</script>

<div class="flex min-h-screen flex-col items-center justify-center p-4">
  <Card.Root class="-my-4 w-full max-w-sm">
    <Card.Header>
      <Card.Title>Sign Up</Card.Title>
      <Card.Description></Card.Description>
      <Card.Action>
        <Button variant="link" href="/login">Log In</Button>
      </Card.Action>
    </Card.Header>
    <Card.Content>
      <form id="signup-form" method="POST" action={formAction}>
        <div class="flex flex-col gap-6">
          {#if form?.message}
            <p class="text-sm font-medium text-destructive">{form.message}</p>
          {/if}
          <div class="grid gap-2">
            <Label for="username">Username</Label>
            <Input
              id="username"
              name="username"
              type="username"
              placeholder="username"
              required
            />
          </div>
          <div class="grid gap-2">
            <Label for="email">Email</Label>
            <Input
              id="email"
              name="email"
              type="email"
              placeholder="example@example.com"
              required
            />
          </div>
          <div class="grid gap-2">
            <div class="flex items-center">
              <Label for="password">Password</Label>
            </div>
            <Input id="password" name="password" type="password" required />
          </div>

          <div class="grid gap-2">
            <div class="flex items-center">
              <Label for="password-confirm">Confirm password</Label>
            </div>
            <Input id="password-confirm" name="password-confirm" type="password" required />
          </div>
        </div>
      </form>
    </Card.Content>
    <Card.Footer class="flex-col gap-2">
      <Button type="submit" form="signup-form" class="w-full">Signup</Button>
    </Card.Footer>
  </Card.Root>
</div>
