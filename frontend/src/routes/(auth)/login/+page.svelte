<script>
  import { Label } from "$lib/components/ui/label/index.js";
  import { Input } from "$lib/components/ui/input/index.js";
  import * as Card from "$lib/components/ui/card/index.js";
  import { Button } from "$lib/components/ui/button/index.js";
  import ModeToggle from "$lib/components/ModeToggle.svelte";
  import { page } from "$app/state";

  let { form } = $props();

  const redirectTo = page.url.searchParams.get("redirectTo") || "/";
  const formAction = `?/login&redirectTo=${encodeURIComponent(redirectTo)}`;
</script>

<div class="flex min-h-screen flex-col items-center justify-center p-4">
  <Card.Root class="-my-4 w-full max-w-sm">
    <Card.Header>
      <Card.Title>Login to your account</Card.Title>
      <Card.Description
        >Enter your email below to login to your account</Card.Description
      >
      <Card.Action>
        <Button variant="link">Sign Up</Button>
      </Card.Action>
    </Card.Header>
    <Card.Content>
      <form id="login-form" method="POST" action={formAction}>
        <div class="flex flex-col gap-6">
          {#if form?.message}
            <p class="text-sm font-medium text-destructive">{form.message}</p>
          {/if}
          <div class="grid gap-2">
            <Label for="email">Email</Label>
            <Input
              id="email"
              name="username"
              type="email"
              placeholder="m@example.com"
              required
            />
          </div>
          <div class="grid gap-2">
            <div class="flex items-center">
              <Label for="password">Password</Label>
              <a
                href="##"
                class="ms-auto inline-block text-sm underline-offset-4 hover:underline"
              >
                Forgot your password?
              </a>
            </div>
            <Input id="password" name="password" type="password" required />
          </div>
        </div>
      </form>
    </Card.Content>
    <Card.Footer class="flex-col gap-2">
      <Button type="submit" form="login-form" class="w-full">Login</Button>
      <Button variant="outline" class="w-full">Login with Google</Button>
    </Card.Footer>
  </Card.Root>
</div>
